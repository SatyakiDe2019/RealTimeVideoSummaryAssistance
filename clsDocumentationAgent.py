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
import uuid
from typing import Dict, List, Optional, Any, Union

# Import LangChain components
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory 
from langchain_openai import ChatOpenAI
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages

from clsConfigClient import clsConfigClient as cf

from clsSendMessageTool import clsSendMessageTool
import clsMCPBroker
from clsMCPMessage import clsMCPMessage

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
# Documentation Agent (using LangChain)
# ----------------------------------------------------------------------------------

class clsDocumentationAgent:
    """Documentation Agent built with LangChain"""
    
    def __init__(self, agent_id: str, broker: clsMCPBroker):
        self.agent_id = agent_id
        self.broker = broker
        self.broker.register_agent(agent_id)
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model="gpt-4-0125-preview",
            temperature=0.1,
            api_key=OPENAI_API_KEY
        )
        
        # Create tools
        self.tools = [
            clsSendMessageTool(sender_id=self.agent_id, broker=self.broker)
        ]
        
        # Set up LLM with tools
        self.llm_with_tools = self.llm.bind(
            tools=[tool.tool_config for tool in self.tools]
        )
        
        # Setup memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Documentation Agent for YouTube video transcripts. Your responsibilities include:
                1. Process YouTube video transcripts
                2. Identify key points, topics, and main ideas
                3. Organize content into a coherent and structured format
                4. Create concise summaries
                5. Request research information when necessary
                
                When you need additional context or research, send a request to the Research Agent.
                Always maintain a professional tone and ensure your documentation is clear and organized.
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        self.agent = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: self.memory.load_memory_variables({})["chat_history"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
            }
            | self.prompt
            | self.llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )
        
        # Video data
        self.current_conversation_id = None
        self.video_notes = {}
        self.key_points = []
        self.transcript_segments = []
        
    def start_processing(self) -> str:
        """Start processing a new video"""
        self.current_conversation_id = str(uuid.uuid4())
        self.video_notes = {}
        self.key_points = []
        self.transcript_segments = []
        
        return self.current_conversation_id
    
    def process_transcript(self, transcript_segments, conversation_id=None):
        """Process a YouTube transcript"""
        if not conversation_id:
            conversation_id = self.start_processing()
        self.current_conversation_id = conversation_id
        
        # Store transcript segments
        self.transcript_segments = transcript_segments
        
        # Process segments
        processed_segments = []
        for segment in transcript_segments:
            processed_result = self.process_segment(segment)
            processed_segments.append(processed_result)
        
        # Generate summary
        summary = self.generate_summary()
        
        return {
            "processed_segments": processed_segments,
            "summary": summary,
            "conversation_id": conversation_id
        }
    
    def process_segment(self, segment):
        """Process individual transcript segment"""
        text = segment.get("text", "")
        start = segment.get("start", 0)
        
        # Use LangChain agent to process the segment
        result = self.agent_executor.invoke({
            "input": f"Process this video transcript segment at timestamp {start}s: {text}. If research is needed, send a request to the research_agent."
        })
        
        # Update video notes
        timestamp = start
        self.video_notes[timestamp] = {
            "text": text,
            "analysis": result["output"]
        }
        
        return {
            "timestamp": timestamp,
            "text": text,
            "analysis": result["output"]
        }
    
    def handle_mcp_message(self, message: clsMCPMessage) -> Optional[clsMCPMessage]:
        """Handle an incoming MCP message"""
        if message.message_type == "research_response":
            # Process research information received from Research Agent
            research_info = message.content.get("text", "")
            
            result = self.agent_executor.invoke({
                "input": f"Incorporate this research information into video analysis: {research_info}"
            })
            
            # Send acknowledgment back to Research Agent
            response = clsMCPMessage(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="acknowledgment",
                content={"text": "Research information incorporated into video analysis."},
                reply_to=message.id,
                conversation_id=message.conversation_id
            )
            
            self.broker.publish(response)
            return response
        
        elif message.message_type == "translation_response":
            # Process translation response from Translation Agent
            translation_result = message.content
            
            # Process the translated text
            if "final_text" in translation_result:
                text = translation_result["final_text"]
                original_text = translation_result.get("original_text", "")
                language_info = translation_result.get("language", {})
                
                result = self.agent_executor.invoke({
                    "input": f"Process this translated text: {text}\nOriginal language: {language_info.get('language', 'unknown')}\nOriginal text: {original_text}"
                })
                
                # Update notes with translation information
                for timestamp, note in self.video_notes.items():
                    if note["text"] == original_text:
                        note["translated_text"] = text
                        note["language"] = language_info
                        break
            
            return None
        
        return None
    
    def run(self):
        """Run the agent to listen for MCP messages"""
        print(f"Documentation Agent {self.agent_id} is running...")
        while True:
            message = self.broker.get_message(self.agent_id, timeout=1)
            if message:
                self.handle_mcp_message(message)
            time.sleep(0.1)
    
    def generate_summary(self) -> str:
        """Generate a summary of the video"""
        if not self.video_notes:
            return "No video data available to summarize."
        
        all_notes = "\n".join([f"{ts}: {note['text']}" for ts, note in self.video_notes.items()])
        
        result = self.agent_executor.invoke({
            "input": f"Generate a concise summary of this YouTube video, including key points and topics:\n{all_notes}"
        })
        
        return result["output"]

