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

from clsConfigClient import clsConfigClient as cf
import clsMCPBroker
from clsLanguageDetector import clsLanguageDetector
from clsTranslationService import clsTranslationService
from clsMCPMessage import clsMCPMessage

# ----------------------------------------------------------------------------------
# Translation Agent
# ----------------------------------------------------------------------------------

class clsTranslationAgent:
    """Agent for language detection and translation"""
    
    def __init__(self, agent_id: str, broker: clsMCPBroker):
        self.agent_id = agent_id
        self.broker = broker
        self.broker.register_agent(agent_id)
        
        # Initialize language detector
        self.language_detector = clsLanguageDetector()
        
        # Initialize translation service
        self.translation_service = clsTranslationService()
    
    def process_text(self, text, conversation_id=None):
        """Process text: detect language and translate if needed, handling mixed language content"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Detect language with support for mixed language content
        language_info = self.language_detector.detect(text)
        
        # Decide if translation is needed
        needs_translation = True
        
        # Pure English content doesn't need translation
        if language_info["language_code"] == "en-IN" or language_info["language_code"] == "unknown":
            needs_translation = False
        
        # For mixed language, check if it's primarily English
        if language_info.get("is_mixed", False) and language_info.get("languages", []):
            english_langs = [
                lang for lang in language_info.get("languages", []) 
                if lang["language_code"] == "en-IN" or lang["language_code"].startswith("en-")
            ]
            
            # If the highest confidence language is English and > 60% confident, don't translate
            if english_langs and english_langs[0].get("confidence", 0) > 0.6:
                needs_translation = False
        
        if needs_translation:
            # Translate using the appropriate service based on language detection
            translation_result = self.translation_service.translate(text, language_info)
            
            return {
                "original_text": text,
                "language": language_info,
                "translation": translation_result,
                "final_text": translation_result.get("translated_text", text),
                "conversation_id": conversation_id
            }
        else:
            # Already English or unknown language, return as is
            return {
                "original_text": text,
                "language": language_info,
                "translation": {"provider": "none"},
                "final_text": text,
                "conversation_id": conversation_id
            }
    
    def handle_mcp_message(self, message: clsMCPMessage) -> Optional[clsMCPMessage]:
        """Handle an incoming MCP message"""
        if message.message_type == "translation_request":
            # Process translation request from Documentation Agent
            text = message.content.get("text", "")
            
            # Process the text
            result = self.process_text(text, message.conversation_id)
            
            # Send translation results back to requester
            response = clsMCPMessage(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="translation_response",
                content=result,
                reply_to=message.id,
                conversation_id=message.conversation_id
            )
            
            self.broker.publish(response)
            return response
        
        return None
    
    def run(self):
        """Run the agent to listen for MCP messages"""
        print(f"Translation Agent {self.agent_id} is running...")
        while True:
            message = self.broker.get_message(self.agent_id, timeout=1)
            if message:
                self.handle_mcp_message(message)
            time.sleep(0.1)

