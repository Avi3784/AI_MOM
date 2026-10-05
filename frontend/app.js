// =============================================
// AI MOM - Frontend JavaScript
// Handles: Microphone recording, WebSocket streaming,
//          live transcript display, and AI summarization.
// =============================================

// --- Configuration ---
// The backend URL. Change this if your server runs on a different address.
const API_BASE = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws/transcribe";

// --- DOM Elements ---
// Grab references to all the HTML elements we need to interact with.
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const summarizeBtn = document.getElementById("summarize-btn");
const statusEl = document.getElementById("status");
const transcriptEl = document.getElementById("transcript");
const summaryEl = document.getElementById("summary");
const copyTranscriptBtn = document.getElementById("copy-transcript-btn");
const copySummaryBtn = document.getElementById("copy-summary-btn");

// --- State Variables ---
// These keep track of what's happening in the app right now.
let mediaRecorder = null;   // The browser's MediaRecorder that captures mic audio
let websocket = null;       // The WebSocket connection to our backend
let fullTranscript = "";    // We accumulate all transcribed text here

// --- Helper: Update the status text ---
function setStatus(text, className) {
    statusEl.textContent = text;
    statusEl.className = "status";
    if (className) {
        statusEl.classList.add(className);
    }
}

// =============================================
// DAY 5: Microphone Recording & WebSocket Connection
// =============================================

// When the user clicks "Start Meeting"
startBtn.addEventListener("click", async () => {
    try {
        // Step 1: Ask the browser for microphone permission
        // This will show the "Allow microphone?" popup to the user.
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Step 2: Open a WebSocket connection to our backend
        websocket = new WebSocket(WS_URL);

        websocket.onopen = () => {
            console.log("WebSocket connected.");
            setStatus("Recording...", "recording");

            // Step 3: Create a MediaRecorder to capture audio from the mic
            // We use "audio/webm" format because it's widely supported in browsers.
            mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

            // Step 4: Every time a chunk of audio is ready, send it to the backend
            // timeslice in start() controls how often we get a chunk (in ms).
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && websocket.readyState === WebSocket.OPEN) {
                    // Send the raw audio blob over the WebSocket
                    websocket.send(event.data);
                }
            };

            // Start recording, send a chunk every 5 seconds
            // 5 seconds gives Whisper enough audio context for accurate transcription.
            mediaRecorder.start(5000);

            // Clear previous transcript
            transcriptEl.innerHTML = "";
            fullTranscript = "";

            // Update button states
            startBtn.disabled = true;
            stopBtn.disabled = false;
            summarizeBtn.disabled = true;
            copyTranscriptBtn.disabled = true;
        };

        // =============================================
        // DAY 6: Live UI Updates
        // =============================================

        // When we receive transcribed text back from the server
        websocket.onmessage = (event) => {
            const text = event.data;

            // Skip error messages from being added to the full transcript
            if (text === "[Transcription Error]") {
                console.warn("Transcription error received from server.");
                return;
            }

            // Append to our running full transcript
            fullTranscript += text + " ";

            // Create a new line element and add it to the transcript panel
            const line = document.createElement("div");
            line.className = "transcript-line";
            line.textContent = text;
            transcriptEl.appendChild(line);

            // Auto-scroll to the bottom so the user always sees the latest text
            transcriptEl.scrollTop = transcriptEl.scrollHeight;
        };

        // Handle WebSocket errors
        websocket.onerror = (error) => {
            console.error("WebSocket error:", error);
            setStatus("Connection error", "");
        };

        // Handle WebSocket closing
        websocket.onclose = () => {
            console.log("WebSocket closed.");
        };

    } catch (err) {
        // This happens if the user denies microphone access
        console.error("Microphone access denied:", err);
        setStatus("Microphone access denied", "");
        alert("Please allow microphone access to use this app.");
    }
});

// When the user clicks "Stop Meeting"
stopBtn.addEventListener("click", () => {
    // Stop the MediaRecorder (this stops capturing audio from the mic)
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        // Also stop all audio tracks to release the microphone
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }

    // Close the WebSocket connection
    if (websocket) {
        websocket.close();
    }

    // Update button states
    startBtn.disabled = false;
    stopBtn.disabled = true;
    copyTranscriptBtn.disabled = false;

    // Only enable "Generate Summary" if we actually have a transcript
    if (fullTranscript.trim().length > 0) {
        summarizeBtn.disabled = false;
    }

    setStatus("Meeting ended", "");
});

// When the user clicks "Generate Summary"
summarizeBtn.addEventListener("click", async () => {
    if (!fullTranscript.trim()) {
        alert("No transcript available to summarize.");
        return;
    }

    // Show loading state
    setStatus("Generating summary...", "processing");
    summarizeBtn.disabled = true;
    summaryEl.innerHTML = '<span class="spinner"></span> AI is thinking...';

    try {
        // Send the full transcript to our /api/summarize endpoint
        const response = await fetch(`${API_BASE}/api/summarize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transcript: fullTranscript })
        });

        const data = await response.json();

        if (data.error) {
            summaryEl.innerHTML = `<p style="color: #ef4444;">Error: ${data.error}</p>`;
            setStatus("Summary failed", "");
        } else {
            // Render the markdown summary as HTML using the marked library
            summaryEl.innerHTML = marked.parse(data.summary);
            copySummaryBtn.disabled = false;
            setStatus("Summary ready", "");
        }

    } catch (err) {
        console.error("Summary request failed:", err);
        summaryEl.innerHTML = '<p style="color: #ef4444;">Failed to connect to the server.</p>';
        setStatus("Server error", "");
    }
});

// =============================================
// DAY 7: Copy to Clipboard (Polish)
// =============================================

// Copy transcript text to clipboard
copyTranscriptBtn.addEventListener("click", () => {
    if (fullTranscript.trim()) {
        navigator.clipboard.writeText(fullTranscript.trim());
        copyTranscriptBtn.textContent = "Copied!";
        setTimeout(() => { copyTranscriptBtn.textContent = "Copy"; }, 2000);
    }
});

// Copy summary text to clipboard
copySummaryBtn.addEventListener("click", () => {
    const summaryText = summaryEl.innerText;
    if (summaryText) {
        navigator.clipboard.writeText(summaryText);
        copySummaryBtn.textContent = "Copied!";
        setTimeout(() => { copySummaryBtn.textContent = "Copy"; }, 2000);
    }
});
