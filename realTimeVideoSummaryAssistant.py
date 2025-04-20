################################################
####                                        ####
#### Written By: SATYAKI DE                 ####
#### Written On:  15-May-2020               ####
#### Modified On: 20-Apr-2025               ####
####                                        ####
#### Objective: This script is a the main   ####
#### application file that implement MCP    ####
#### protocols for multiple agents & the    ####
#### coordination between the different     ####
#### agents.                                ####
####                                        ####
################################################

import threading
from fastapi import FastAPI

from clsConfigClient import clsConfigClient as cf

import clsMCPBroker as t
from clsDocumentationAgent import clsDocumentationAgent
from clsTranslationAgent import clsTranslationAgent
from clsResearchAgent import clsResearchAgent
from clsYouTubeVideoProcessor import clsYouTubeVideoProcessor

# Create a global MCP broker
mcp_broker = t.clsMCPBroker()

# ----------------------------------------------------------------------------------
# Main Application
# ----------------------------------------------------------------------------------

# Create FastAPI app
app = FastAPI(
    title="YouTube Video Summary Assistant API",
    description="API for processing YouTube videos with language detection, translation, and analysis",
    version="1.0.0"
)

# Initialize agents
doc_agent = clsDocumentationAgent(agent_id="doc_agent", broker=mcp_broker)
translation_agent = clsTranslationAgent(agent_id="translation_agent", broker=mcp_broker)
research_agent = clsResearchAgent(agent_id="research_agent", broker=mcp_broker)

# Define lifespan for startup and shutdown events
# Set up broker subscriptions
# Import components from existing code
from realTimeVideoSummaryAssistant import (
    mcp_broker, 
    clsDocumentationAgent, 
    clsTranslationAgent, 
    clsResearchAgent, 
    clsYouTubeVideoProcessor
)

# Set up subscriptions
mcp_broker.subscribe("doc_agent", "research_agent")
mcp_broker.subscribe("research_agent", "doc_agent")
mcp_broker.subscribe("doc_agent", "translation_agent")
mcp_broker.subscribe("translation_agent", "doc_agent")

# Start agent threads
doc_thread = threading.Thread(target=doc_agent.run, daemon=True)
translation_thread = threading.Thread(target=translation_agent.run, daemon=True)
research_thread = threading.Thread(target=research_agent.run, daemon=True)

doc_thread.start()
translation_thread.start()
research_thread.start()


# Create video processor
video_processor = clsYouTubeVideoProcessor(
    doc_agent,
    translation_agent,
    research_agent
)

# API endpoints
@app.post("/api/processVideo")
async def processVideo(youtube_url: str):
    try:
        """
        Process a YouTube video and return a task ID.
        The task will run in the background and results can be fetched using the /api/task/{task_id} endpoint.
        """

        resPonse = ""
        youtube_url = youtube_url

        if youtube_url:
            result = video_processor.process_youtube_video(youtube_url)
            
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                # Print summary
                print("\nVideo Summary:")
                print(result["documentation"]["summary"])
                
                # Print segment analyses
                print("\nSegment Analyses:")
                for segment in result["processed_segments"][:3]:  # Show first 3 for brevity
                    print(f"\nTimestamp: {segment.get('start', 0)}")
                    print(f"Text: {segment.get('text', '')}")
                    if "processed_text" in segment and segment["processed_text"] != segment["text"]:
                        print(f"Translated Text: {segment.get('processed_text', '')}")
                    
                    # Find corresponding analysis
                    for proc_segment in result["documentation"]["processed_segments"]:
                        if proc_segment["timestamp"] == segment.get("start", 0):
                            print(f"Analysis: {proc_segment.get('analysis', '')}")
                            resPonse = resPonse + str(proc_segment.get('analysis', ''))
                            break
                
                print("\nProcessing complete. Full results are available in the return object.")
        else:
            print("No YouTube URL provided.")

        xbuff = {
            "status": "Success",
            "YouTube_URL": youtube_url,
            "Analysis": resPonse
        }
        
        # Return task ID
        return xbuff
    
    except Exception as e:

        xbuff = {
            "status": "Failure",
            "YouTube_URL": youtube_url,
            "Analysis": "Failed to process video!"
        }
        
        # Return task ID
        return xbuff


# Root endpoint for basic health/status
@app.get("/")
def read_root():
    return {"status": "running", "message": "YouTube Video Processing API up and running"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Main entry point to run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("realTimeVideoSummaryAssistant:app", host="0.0.0.0", port=8000, reload=True)
