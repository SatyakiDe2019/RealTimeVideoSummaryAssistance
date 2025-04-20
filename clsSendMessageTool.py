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

from typing import Dict, Optional, Any
from pydantic import Field
from langchain.tools import BaseTool

import clsMCPBroker
import clsMCPMessage

from clsConfigClient import clsConfigClient as cf

# ----------------------------------------------------------------------------------
# Documentation Agent (using LangChain)
# ----------------------------------------------------------------------------------

class clsSendMessageTool(BaseTool):
    """Tool for sending messages via MCP protocol"""
    
    name: str = "send_message"
    description: str = "Send a message to another agent via the MCP protocol"
    sender_id: str = Field(default="", exclude=True)
    broker: Any = Field(default=None, exclude=True)
    tool_config: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    
    def __init__(self, sender_id: str, broker: clsMCPBroker):
        super().__init__()
        self.sender_id = sender_id
        self.broker = broker
        self.tool_config = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "receiver": {
                            "type": "string",
                            "description": "The ID of the agent to send the message to"
                        },
                        "message_type": {
                            "type": "string",
                            "description": "The type of message (request, response, notification)"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content of the message"
                        },
                        "conversation_id": {
                            "type": "string",
                            "description": "The ID of the conversation"
                        },
                        "reply_to": {
                            "type": "string",
                            "description": "The ID of the message being replied to (optional)"
                        }
                    },
                    "required": ["receiver", "message_type", "content", "conversation_id"]
                }
            }
        }
    
    def _run(self, receiver: str, message_type: str, content: str, 
             conversation_id: str, reply_to: Optional[str] = None) -> str:
        """Run the tool"""
        message = clsMCPMessage(
            sender=self.sender_id,
            receiver=receiver,
            message_type=message_type,
            content={"text": content},
            reply_to=reply_to,
            conversation_id=conversation_id
        )
        self.broker.publish(message)
        return f"Message sent to {receiver}"

