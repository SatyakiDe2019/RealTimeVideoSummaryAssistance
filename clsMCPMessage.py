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
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

# ----------------------------------------------------------------------------------
# Message-Chaining Protocol (MCP) Implementation
# ----------------------------------------------------------------------------------

class clsMCPMessage(BaseModel):
    """Message format for MCP protocol"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    sender: str
    receiver: str
    message_type: str  # "request", "response", "notification"
    content: Dict[str, Any]
    reply_to: Optional[str] = None
    conversation_id: str
    metadata: Dict[str, Any] = {}

