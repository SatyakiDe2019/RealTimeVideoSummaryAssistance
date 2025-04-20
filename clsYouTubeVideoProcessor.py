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

import re
from typing import Dict, List, Optional, Any, Union

# Import YouTube transcript API
from youtube_transcript_api import YouTubeTranscriptApi

from clsConfigClient import clsConfigClient as cf

# ----------------------------------------------------------------------------------
# YouTube Transcript Extraction
# ----------------------------------------------------------------------------------

def extract_youtube_id(youtube_url):
    """Extract YouTube video ID from URL"""
    youtube_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
    if youtube_id_match:
        return youtube_id_match.group(1)
    return None

def get_youtube_transcript(youtube_url):
    """Get transcript from YouTube video"""
    video_id = extract_youtube_id(youtube_url)
    if not video_id:
        return {"error": "Invalid YouTube URL or ID"}
    
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # First try to get manual transcripts
        try:
            transcript = transcript_list.find_manually_created_transcript(["en"])
            transcript_data = transcript.fetch()
            print(f"Debug - Manual transcript format: {type(transcript_data)}")
            if transcript_data and len(transcript_data) > 0:
                print(f"Debug - First item type: {type(transcript_data[0])}")
                print(f"Debug - First item sample: {transcript_data[0]}")
            return {"text": transcript_data, "language": "en", "auto_generated": False}
        except Exception as e:
            print(f"Debug - No manual transcript: {str(e)}")
            # If no manual English transcript, try any available transcript
            try:
                available_transcripts = list(transcript_list)
                if available_transcripts:
                    transcript = available_transcripts[0]
                    print(f"Debug - Using transcript in language: {transcript.language_code}")
                    transcript_data = transcript.fetch()
                    print(f"Debug - Auto transcript format: {type(transcript_data)}")
                    if transcript_data and len(transcript_data) > 0:
                        print(f"Debug - First item type: {type(transcript_data[0])}")
                        print(f"Debug - First item sample: {transcript_data[0]}")
                    return {
                        "text": transcript_data, 
                        "language": transcript.language_code, 
                        "auto_generated": transcript.is_generated
                    }
                else:
                    return {"error": "No transcripts available for this video"}
            except Exception as e:
                return {"error": f"Error getting transcript: {str(e)}"}
    except Exception as e:
        return {"error": f"Error getting transcript list: {str(e)}"}

# ----------------------------------------------------------------------------------
# YouTube Video Processor
# ----------------------------------------------------------------------------------

class clsYouTubeVideoProcessor:
    """Process YouTube videos using the agent system"""
    
    def __init__(self, documentation_agent, translation_agent, research_agent):
        self.documentation_agent = documentation_agent
        self.translation_agent = translation_agent
        self.research_agent = research_agent
    
    def process_youtube_video(self, youtube_url):
        """Process a YouTube video"""
        print(f"Processing YouTube video: {youtube_url}")
        
        # Extract transcript
        transcript_result = get_youtube_transcript(youtube_url)
        
        if "error" in transcript_result:
            return {"error": transcript_result["error"]}
        
        # Start a new conversation
        conversation_id = self.documentation_agent.start_processing()
        
        # Process transcript segments
        transcript_data = transcript_result["text"]
        transcript_language = transcript_result["language"]
        
        print(f"Debug - Type of transcript_data: {type(transcript_data)}")
        
        # For each segment, detect language and translate if needed
        processed_segments = []
        
        try:
            # Make sure transcript_data is a list of dictionaries with text and start fields
            if isinstance(transcript_data, list):
                for idx, segment in enumerate(transcript_data):
                    print(f"Debug - Processing segment {idx}, type: {type(segment)}")
                    
                    # Extract text properly based on the type
                    if isinstance(segment, dict) and "text" in segment:
                        text = segment["text"]
                        start = segment.get("start", 0)
                    else:
                        # Try to access attributes for non-dict types
                        try:
                            text = segment.text
                            start = getattr(segment, "start", 0)
                        except AttributeError:
                            # If all else fails, convert to string
                            text = str(segment)
                            start = idx * 5  # Arbitrary timestamp
                    
                    print(f"Debug - Extracted text: {text[:30]}...")
                    
                    # Create a standardized segment
                    std_segment = {
                        "text": text,
                        "start": start
                    }
                    
                    # Process through translation agent
                    translation_result = self.translation_agent.process_text(text, conversation_id)
                    
                    # Update segment with translation information
                    segment_with_translation = {
                        **std_segment,
                        "translation_info": translation_result
                    }
                    
                    # Use translated text for documentation
                    if "final_text" in translation_result and translation_result["final_text"] != text:
                        std_segment["processed_text"] = translation_result["final_text"]
                    else:
                        std_segment["processed_text"] = text
                    
                    processed_segments.append(segment_with_translation)
            else:
                # If transcript_data is not a list, treat it as a single text block
                print(f"Debug - Transcript is not a list, treating as single text")
                text = str(transcript_data)
                std_segment = {
                    "text": text,
                    "start": 0
                }
                
                translation_result = self.translation_agent.process_text(text, conversation_id)
                segment_with_translation = {
                    **std_segment,
                    "translation_info": translation_result
                }
                
                if "final_text" in translation_result and translation_result["final_text"] != text:
                    std_segment["processed_text"] = translation_result["final_text"]
                else:
                    std_segment["processed_text"] = text
                
                processed_segments.append(segment_with_translation)
                
        except Exception as e:
            print(f"Debug - Error processing transcript: {str(e)}")
            return {"error": f"Error processing transcript: {str(e)}"}
        
        # Process the transcript with the documentation agent
        documentation_result = self.documentation_agent.process_transcript(
            processed_segments,
            conversation_id
        )
        
        return {
            "youtube_url": youtube_url,
            "transcript_language": transcript_language,
            "processed_segments": processed_segments,
            "documentation": documentation_result,
            "conversation_id": conversation_id
        }

