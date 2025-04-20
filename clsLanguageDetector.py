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

# Import language detection library
from lingua import Language, LanguageDetectorBuilder

from clsConfigClient import clsConfigClient as cf

# ----------------------------------------------------------------------------------
# Language Detection
# ----------------------------------------------------------------------------------

class clsLanguageDetector:
    """Detect language using Lingua library with support for mixed language content"""
    
    def __init__(self):
        # Initialize language detector with high accuracy languages
        self.detector = LanguageDetectorBuilder.from_all_languages().build()
        
        # Define Indian languages for special handling
        self.indian_languages = {
            Language.HINDI,
            Language.BENGALI,
            Language.PUNJABI,
            Language.GUJARATI,
            Language.TAMIL,
            Language.TELUGU,
            Language.MARATHI,
            Language.URDU
        }
        
        # Map Lingua languages to language codes
        self.language_code_map = {
            Language.HINDI: "hi-IN",
            Language.BENGALI: "bn-IN",
            Language.PUNJABI: "pa-IN",
            Language.GUJARATI: "gu-IN",
            Language.TAMIL: "ta-IN",
            Language.TELUGU: "te-IN",
            Language.MARATHI: "mr-IN",
            Language.URDU: "ur-IN",
            Language.ENGLISH: "en-IN"
        }
    
    def detect(self, text):
        """Detect the language of the given text with support for mixed language content"""
        if not text:
            return {"language": "unknown", "is_indian": False, "language_code": "unknown", "is_mixed": False, "languages": []}
        
        # Get language probabilities for more detailed analysis
        confidences = self.detector.compute_language_confidence_values(text)
        
        # Sort by confidence scores
        sorted_confidences = sorted(confidences, key=lambda x: x.value, reverse=True)
        
        # Initialize result
        result = {"is_mixed": False, "languages": []}
        
        # Check for mixed language content
        # If top language is less than 70% confident OR second language is more than 25% confident
        if len(sorted_confidences) >= 2:
            top_confidence = sorted_confidences[0].value
            second_confidence = sorted_confidences[1].value
            
            if top_confidence < 0.7 or second_confidence > 0.25:
                # This is likely mixed language content
                result["is_mixed"] = True
                
                # Get top 3 languages with significant confidence (> 10%)
                for conf in sorted_confidences[:3]:
                    if conf.value > 0.1:  # Only include languages with significant presence
                        language = conf.language
                        is_indian = language in self.indian_languages
                        language_code = self.language_code_map.get(language, str(language).split('.')[1].lower())
                        
                        result["languages"].append({
                            "language": str(language).split('.')[1],
                            "is_indian": is_indian,
                            "language_code": language_code,
                            "confidence": conf.value
                        })
        
        # Get most likely language for main result fields
        if sorted_confidences:
            primary_language = sorted_confidences[0].language
            result["language"] = str(primary_language).split('.')[1]
            result["is_indian"] = primary_language in self.indian_languages
            result["language_code"] = self.language_code_map.get(primary_language, str(primary_language).split('.')[1].lower())
            
            # Add detected languages if not already set
            if not result["languages"]:
                result["languages"] = [{
                    "language": result["language"],
                    "is_indian": result["is_indian"],
                    "language_code": result["language_code"],
                    "confidence": sorted_confidences[0].value
                }]
            
            return result
        else:
            return {"language": "unknown", "is_indian": False, "language_code": "unknown", "is_mixed": False, "languages": []}

