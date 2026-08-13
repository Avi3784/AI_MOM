from fastapi import FastAPI
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

# Note: We will add the WebSocket and Audio upload endpoints here in the upcoming modules.
