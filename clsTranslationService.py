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

# Import translation libraries
import requests

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
# Translation Services
# ----------------------------------------------------------------------------------

class clsTranslationService:
    """Translation service using multiple providers with support for mixed languages"""
    
    def __init__(self):
        # Initialize Sarvam AI client
        self.sarvam_api_key = SARVAM_API_KEY
        self.sarvam_url = "https://api.sarvam.ai/translate"
        
        # Initialize Google Cloud Translation client using simple HTTP requests
        self.google_api_key = GOOGLE_API_KEY
        self.google_translate_url = "https://translation.googleapis.com/language/translate/v2"
    
    def translate_with_sarvam(self, text, source_lang, target_lang="en-IN"):
        """Translate text using Sarvam AI (for Indian languages)"""
        if not self.sarvam_api_key:
            return {"error": "Sarvam API key not set"}
        
        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": self.sarvam_api_key
        }
        
        payload = {
            "input": text,
            "source_language_code": source_lang,
            "target_language_code": target_lang,
            "speaker_gender": "Female",
            "mode": "formal",
            "model": "mayura:v1"
        }
        
        try:
            response = requests.post(self.sarvam_url, headers=headers, json=payload)
            if response.status_code == 200:
                return {"translated_text": response.json().get("translated_text", ""), "provider": "sarvam"}
            else:
                return {"error": f"Sarvam API error: {response.text}", "provider": "sarvam"}
        except Exception as e:
            return {"error": f"Error calling Sarvam API: {str(e)}", "provider": "sarvam"}
    
    def translate_with_google(self, text, target_lang="en"):
        """Translate text using Google Cloud Translation API with direct HTTP request"""
        if not self.google_api_key:
            return {"error": "Google API key not set"}
        
        try:
            # Using the translation API v2 with API key
            params = {
                "key": self.google_api_key,
                "q": text,
                "target": target_lang
            }
            
            response = requests.post(self.google_translate_url, params=params)
            if response.status_code == 200:
                data = response.json()
                translation = data.get("data", {}).get("translations", [{}])[0]
                return {
                    "translated_text": translation.get("translatedText", ""),
                    "detected_source_language": translation.get("detectedSourceLanguage", ""),
                    "provider": "google"
                }
            else:
                return {"error": f"Google API error: {response.text}", "provider": "google"}
        except Exception as e:
            return {"error": f"Error calling Google Translation API: {str(e)}", "provider": "google"}
    
    def translate(self, text, language_info):
        """Translate text to English based on language detection info"""
        # If already English or unknown language, return as is
        if language_info["language_code"] == "en-IN" or language_info["language_code"] == "unknown":
            return {"translated_text": text, "provider": "none"}
        
        # Handle mixed language content
        if language_info.get("is_mixed", False) and language_info.get("languages", []):
            # Strategy for mixed language: 
            # 1. If one of the languages is English, don't translate the entire text, as it might distort English portions
            # 2. If no English but contains Indian languages, use Sarvam as it handles code-mixing better
            # 3. Otherwise, use Google Translate for the primary detected language
            
            has_english = False
            has_indian = False
            
            for lang in language_info.get("languages", []):
                if lang["language_code"] == "en-IN" or lang["language_code"].startswith("en-"):
                    has_english = True
                if lang.get("is_indian", False):
                    has_indian = True
            
            if has_english:
                # Contains English - use Google for full text as it handles code-mixing well
                return self.translate_with_google(text)
            elif has_indian:
                # Contains Indian languages - use Sarvam
                # Use the highest confidence Indian language as source
                indian_langs = [lang for lang in language_info.get("languages", []) if lang.get("is_indian", False)]
                if indian_langs:
                    # Sort by confidence
                    indian_langs.sort(key=lambda x: x.get("confidence", 0), reverse=True)
                    source_lang = indian_langs[0]["language_code"]
                    return self.translate_with_sarvam(text, source_lang)
                else:
                    # Fallback to primary language
                    if language_info["is_indian"]:
                        return self.translate_with_sarvam(text, language_info["language_code"])
                    else:
                        return self.translate_with_google(text)
            else:
                # No English, no Indian languages - use Google for primary language
                return self.translate_with_google(text)
        else:
            # Not mixed language - use standard approach
            if language_info["is_indian"]:
                # Use Sarvam AI for Indian languages
                return self.translate_with_sarvam(text, language_info["language_code"])
            else:
                # Use Google for other languages
                return self.translate_with_google(text)

