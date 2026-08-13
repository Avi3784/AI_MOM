# AI MOM (AI Meeting Minutes)

A lightning-fast, beginner-friendly meeting transcription and summarization web application powered by the Groq API.

## Overview

This project is built from scratch in small modules to demonstrate clean architecture and seamless API integration. It uses:
- **FastAPI (Python)** for a robust and fast backend.
- **Vanilla HTML/CSS/JS** for a simple, dependency-free frontend.
- **Groq API** for ultra-fast Whisper transcription and LLaMA 3 meeting summarization.

## Architecture

```mermaid
graph TD
    subgraph Frontend
        A[Browser UI<br/>HTML/CSS/JS]
        B[Microphone / File Upload]
    end

    subgraph Backend - FastAPI
        C[API Routes]
        D[WebSocket Engine<br/>Real-time Data]
        E[HTTP Endpoints]
    end

    subgraph Groq API
        F[Whisper API<br/>Audio to Text]
        G[LLaMA 3 API<br/>Text Summarization]
    end

    A <-->|WebSocket Stream / HTTP| C
    B --> A
    C --> D
    C --> E
    
    D -->|Audio Chunks| F
    F -->|Live Transcripts| D
    
    E -->|Full Transcript| G
    G -->|Meeting Minutes| E
```

## Setup Instructions (Day 1)

1. Clone this repository.
2. Navigate to the `backend` folder and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `backend/.env.example` to `backend/.env` and add your Groq API key.
5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```
6. Visit `http://localhost:8000/` to ensure the server is running.
