from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from dotenv import load_dotenv
from groq import AsyncGroq

# Load environment variables from .env file
load_dotenv()

# Initialize Groq async client
# It automatically looks for the GROQ_API_KEY in the environment
groq_client = AsyncGroq()

# Initialize the FastAPI application
app = FastAPI(
    title="AI MOM API",
    description="Backend API for the AI Meeting Minutes application using Groq.",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows our frontend (which might be hosted on a different port) to communicate with our backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you'd replace "*" with your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# A simple root endpoint to verify our server is running properly.
@app.get("/")
async def root():
    """
    Health check endpoint. 
    When you visit http://localhost:8000/ it will return this message.
    """
    return {"message": "Welcome to AI MOM API! The server is running successfully."}

# DAY 2 & 3: The WebSocket Engine & Live Transcription
# This endpoint listens for a WebSocket connection from the frontend.
# It receives chunks of audio in real-time, transcribes them using Groq, and sends text back.
@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio transcription.
    The client connects here and streams binary audio data (e.g., webm chunks).
    """
    # Accept the incoming WebSocket connection
    await websocket.accept()
    print("Client connected to WebSocket.")
    
    try:
        # Keep the connection open and listen for messages indefinitely
        while True:
            # Receive binary audio chunk from the frontend
            audio_chunk = await websocket.receive_bytes()
            print(f"Received audio chunk of size: {len(audio_chunk)} bytes")
            
            # DAY 3: Groq Transcription
            # We need to save the audio chunk to a temporary file because the Groq API expects a file.
            # We assume the frontend sends WebM audio chunks (common in browsers).
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                temp_audio.write(audio_chunk)
                temp_audio_path = temp_audio.name
            
            try:
                # Open the temporary audio file and send it to Groq Whisper
                with open(temp_audio_path, "rb") as file:
                    transcription = await groq_client.audio.transcriptions.create(
                        file=(os.path.basename(temp_audio_path), file.read()),
                        model="whisper-large-v3",
                        response_format="text",
                        language="en" # Optional: force English or remove for auto-detect
                    )
                
                # Groq returns the text directly when response_format="text"
                text = transcription.strip() if isinstance(transcription, str) else ""
                
                # Only send back if there is actual text
                if text:
                    print(f"Transcribed: {text}")
                    # Send the transcribed text back to the client
                    await websocket.send_text(text)
            
            except Exception as api_err:
                print(f"Groq API error: {api_err}")
                await websocket.send_text("[Transcription Error]")
            
            finally:
                # Clean up the temporary file so we don't fill up the hard drive!
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            
    except WebSocketDisconnect:
        # This triggers when the client closes the connection or the meeting ends
        print("Client disconnected from WebSocket.")
    except Exception as e:
        # Catch any unexpected errors
        print(f"WebSocket error: {e}")

# DAY 4: The Intelligence Engine
class TranscriptRequest(BaseModel):
    transcript: str

@app.post("/api/summarize")
async def summarize_meeting(request: TranscriptRequest):
    """
    Takes the full meeting transcript and generates a summary using Groq's LLaMA 3 model.
    """
    if not request.transcript.strip():
        return {"error": "Transcript is empty."}
        
    # The prompt instructs the AI on how to format our meeting minutes
    system_prompt = """
    You are an expert executive assistant. Read the provided meeting transcript and create a concise summary.
    Please format your response in Markdown with the following sections:
    
    ### 📝 Meeting Overview
    A brief summary of what the meeting was about.
    
    ### 🎯 Key Decisions
    Bullet points of major decisions made.
    
    ### ✅ Action Items
    A list of tasks assigned, and who they are assigned to (if mentioned).
    """
    
    try:
        print("Sending transcript to Groq for summarization...")
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.transcript}
            ],
            model="llama3-8b-8192", # We use LLaMA 3 8B for fast and excellent summarization
            temperature=0.5, # Slightly creative but mostly deterministic
        )
        
        summary = chat_completion.choices[0].message.content
        print("Summarization complete.")
        return {"summary": summary}
        
    except Exception as e:
        print(f"Summarization error: {e}")
        return {"error": "Failed to generate summary."}

