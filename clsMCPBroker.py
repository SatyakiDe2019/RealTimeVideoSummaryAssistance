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


import queue
from typing import Dict, List, Optional, Any, Union

from clsMCPMessage import clsMCPMessage
from clsConfigClient import clsConfigClient as cf

# ----------------------------------------------------------------------------------
# Message-Chaining Protocol (MCP) Implementation
# ----------------------------------------------------------------------------------


class clsMCPBroker:
    """Message broker for MCP protocol communication between agents"""
    
    def __init__(self):
        self.message_queues: Dict[str, queue.Queue] = {}
        self.subscribers: Dict[str, List[str]] = {}
        self.conversation_history: Dict[str, List[clsMCPMessage]] = {}
    
    def register_agent(self, agent_id: str) -> None:
        """Register an agent with the broker"""
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = queue.Queue()
            self.subscribers[agent_id] = []
    
    def subscribe(self, subscriber_id: str, publisher_id: str) -> None:
        """Subscribe an agent to messages from another agent"""
        if publisher_id in self.subscribers:
            if subscriber_id not in self.subscribers[publisher_id]:
                self.subscribers[publisher_id].append(subscriber_id)
    
    def publish(self, message: clsMCPMessage) -> None:
        """Publish a message to its intended receiver"""
        # Store in conversation history
        if message.conversation_id not in self.conversation_history:
            self.conversation_history[message.conversation_id] = []
        self.conversation_history[message.conversation_id].append(message)
        
        # Deliver to direct receiver
        if message.receiver in self.message_queues:
            self.message_queues[message.receiver].put(message)
        
        # Deliver to subscribers of the sender
        for subscriber in self.subscribers.get(message.sender, []):
            if subscriber != message.receiver:  # Avoid duplicates
                self.message_queues[subscriber].put(message)
    
    def get_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[clsMCPMessage]:
        """Get a message for the specified agent"""
        try:
            return self.message_queues[agent_id].get(timeout=timeout)
        except (queue.Empty, KeyError):
            return None
    
    def get_conversation_history(self, conversation_id: str) -> List[clsMCPMessage]:
        """Get the history of a conversation"""
        return self.conversation_history.get(conversation_id, [])

