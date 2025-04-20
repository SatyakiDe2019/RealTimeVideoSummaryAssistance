################################################
####                                        ####
#### Written By: SATYAKI DE                 ####
#### Written On:  15-May-2020               ####
#### Modified On: 20-Apr-2025               ####
####                                        ####
#### Objective: This script is a one of the ####
#### importtant agent that is part of the   ####
#### MCP protocols for multiple agents &    ####
#### the coordination with the other agents.####
####                                        ####
################################################

import time
from typing import Dict, List, Optional, Any, Union

# Import AutoGen components
from autogen import AssistantAgent, UserProxyAgent
import clsMCPBroker
from clsMCPMessage import clsMCPMessage

from clsConfigClient import clsConfigClient as cf

# Configure API keys - using environment variables directly
OPENAI_API_KEY = cf.conf["OPEN_AI_KEY"]
SARVAM_API_KEY = cf.conf["SARVAM_AI_KEY"]
GOOGLE_API_KEY = cf.conf["GOOGLE_API_KEY"]

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. The application may not function correctly.")
    # Set a default empty value to prevent KeyError
    OPENAI_API_KEY = ""
    
if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY environment variable not set. Google Translation may not work correctly.")
    GOOGLE_API_KEY = ""

if not SARVAM_API_KEY:
    print("Warning: SARVAM_API_KEY environment variable not set. Sarvam AI Translation may not work correctly.")
    SARVAM_API_KEY = ""

# ----------------------------------------------------------------------------------
# Research Agent (using AutoGen)
# ----------------------------------------------------------------------------------

class clsResearchAgent:
    """Research Agent built with AutoGen"""
    
    def __init__(self, agent_id: str, broker: clsMCPBroker):
        self.agent_id = agent_id
        self.broker = broker
        self.broker.register_agent(agent_id)
        
        # Configure AutoGen directly with API key
        if not OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set for ResearchAgent")
            
        # Create config list directly instead of loading from file
        config_list = [
            {
                "model": "gpt-4-0125-preview",
                "api_key": OPENAI_API_KEY
            }
        ]
        # Create AutoGen assistant for research
        self.assistant = AssistantAgent(
            name="research_assistant",
            system_message="""You are a Research Agent for YouTube videos. Your responsibilities include:
                1. Research topics mentioned in the video
                2. Find relevant information, facts, references, or context
                3. Provide concise, accurate information to support the documentation
                4. Focus on delivering high-quality, relevant information
                
                Respond directly to research requests with clear, factual information.
            """,
            llm_config={"config_list": config_list, "temperature": 0.1}
        )
        
        # Create user proxy to handle message passing
        self.user_proxy = UserProxyAgent(
            name="research_manager",
            human_input_mode="NEVER",
            code_execution_config={"work_dir": "coding", "use_docker": False},
            default_auto_reply="Working on the research request..."
        )
        
        # Current conversation tracking
        self.current_requests = {}
    
    def handle_mcp_message(self, message: clsMCPMessage) -> Optional[clsMCPMessage]:
        """Handle an incoming MCP message"""
        if message.message_type == "request":
            # Process research request from Documentation Agent
            request_text = message.content.get("text", "")
            
            # Use AutoGen to process the research request
            def research_task():
                self.user_proxy.initiate_chat(
                    self.assistant,
                    message=f"Research request for YouTube video content: {request_text}. Provide concise, factual information."
                )
                # Return last assistant message
                return self.assistant.chat_messages[self.user_proxy.name][-1]["content"]
            
            # Execute research task
            research_result = research_task()
            
            # Send research results back to Documentation Agent
            response = clsMCPMessage(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="research_response",
                content={"text": research_result},
                reply_to=message.id,
                conversation_id=message.conversation_id
            )
            
            self.broker.publish(response)
            return response
        
        return None
    
    def run(self):
        """Run the agent to listen for MCP messages"""
        print(f"Research Agent {self.agent_id} is running...")
        while True:
            message = self.broker.get_message(self.agent_id, timeout=1)
            if message:
                self.handle_mcp_message(message)
            time.sleep(0.1)

