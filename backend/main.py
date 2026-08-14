from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# DAY 2: The WebSocket Engine
# This endpoint listens for a WebSocket connection from the frontend.
# It receives chunks of audio in real-time.
@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio transcription.
    The client connects here and streams binary audio data.
    """
    # Accept the incoming WebSocket connection
    await websocket.accept()
    print("Client connected to WebSocket.")
    
    try:
        # Keep the connection open and listen for messages indefinitely
        while True:
            # Receive binary audio chunk from the frontend
            audio_chunk = await websocket.receive_bytes()
            
            # For Day 2, we just acknowledge receipt.
            # In Day 3, we will send this chunk to the Groq Whisper API.
            print(f"Received audio chunk of size: {len(audio_chunk)} bytes")
            
            # Send a simple text response back to the client
            await websocket.send_text("Audio chunk received.")
            
    except WebSocketDisconnect:
        # This triggers when the client closes the connection or the meeting ends
        print("Client disconnected from WebSocket.")
    except Exception as e:
        # Catch any unexpected errors
        print(f"WebSocket error: {e}")
