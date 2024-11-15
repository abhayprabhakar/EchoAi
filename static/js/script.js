// HTML Elements
const humanCircle = document.getElementById('start');
const aiCircle = document.getElementById('aiCircle');
const humanMessage = document.getElementById('humanMessage');
const aiMessage = document.getElementById('aiMessage');

// Media and Audio Variables
let mediaRecorder;
let audioChunks = [];
let silenceTimeout;
const SILENCE_THRESHOLD = 1000; // Time in ms before stopping recording 
const SILENCE_THRESHOLD_VALUE = 100; // Volume threshold to detect silence
const SILENCE_DETECTION_DELAY = 2000; // Delay before starting silence detection
let isRecording = false; // Flag to manage recording state
let isProcessing = false; // New flag to track if we're processing audio
let currentStream = null; // Store the current audio stream

// Event Listener for Starting Voice Chat
document.getElementById('start').addEventListener('click', () => {
    startVoiceChatLoop();
});

// Start the voice chat loop
function startVoiceChatLoop() {
    if (isRecording || isProcessing) return; // Prevent starting if already recording or processing
    isRecording = true;

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            currentStream = stream;
            setupMediaRecorder(stream);
            detectSilence(stream);
        })
        .catch(error => {
            console.error("Error accessing media devices:", error);
            isRecording = false;
        });
}

// Setup Media Recorder
function setupMediaRecorder(stream) {
    mediaRecorder = new MediaRecorder(stream);
    humanCircle.classList.add('speaking');
    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
        handleRecordingStop();
    };

    mediaRecorder.start();
}

// Handle when the recording stops
async function handleRecordingStop() {
    try {
        isProcessing = true; // Start processing phase
        humanCircle.classList.remove('speaking');
        
        // Validate audio chunks
        if (!audioChunks || audioChunks.length === 0) {
            throw new Error('No audio data available');
        }

        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob);

        // Stop all tracks in the current stream
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }

        // Make the fetch request with error handling
        const response = await fetch('https://test.abhayprabhakar.co.in/stt', { 
            method: 'POST', 
            body: formData 
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (!data) {
            throw new Error('Empty response from server');
        }

        await processTranscription(data);
    } catch (error) {
        console.error("Error in handleRecordingStop:", error);
        // Handle specific error types
        if (error instanceof TypeError) {
            console.error("TypeError occurred:", error.message);
        }
        restartRecording();
    }
}

// Process transcription data
async function processTranscription(data) {
    try {
        if (!data) {
            throw new Error('No data received from STT service');
        }

        if (data.error) {
            throw new Error(`STT error: ${data.error}`);
        }

        if (data.text) {
            humanMessage.textContent = data.text;
            humanMessage.classList.add('show-message');
            await sendTextToLLM(data.text);
        } else {
            throw new Error('No transcription text in response');
        }
    } catch (error) {
        console.error("Error in processTranscription:", error);
        restartRecording();
    }
}


// Send text to Language Model
async function sendTextToLLM(text) {
    try {
        if (!text || typeof text !== 'string') {
            throw new TypeError('Invalid text input for LLM');
        }

        const response = await fetch('https://test.abhayprabhakar.co.in/llm', {
            method: 'POST',
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        await handleLLMResponse(data);
    } catch (error) {
        console.error('Error in sendTextToLLM:', error);
        restartRecording();
    }
}

// Handle Language Model Response
async function handleLLMResponse(aidata) {
    if (aidata.text) {
        aiMessage.textContent = aidata.text;
        aiMessage.classList.add('show-message');
        await playAudioResponse(aidata.text);
        restartRecording(); // Restart recording after AI response
    } else {
        console.error("AI Response failed:", aidata.error);
        restartRecording();
    }
}

// Play Audio Response
async function playAudioResponse(text) {
    try {
        aiCircle.classList.add('speaking')
        const ttsResponse = await fetch('https://test.abhayprabhakar.co.in/tts', {
            method: 'POST',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        if (ttsResponse.ok) {
            const audioBlob = await ttsResponse.blob();
            const audioURL = URL.createObjectURL(audioBlob);
            await playAudioAndWait(audioURL);
            aiCircle.classList.remove('speaking');
        } else {
            console.error('Failed to load audio:', ttsResponse.statusText);
        }
        aiCircle.classList.remove('speaking')
    } catch (error) {
        console.error('Error playing audio response:', error);
    }
}

// New function to restart the recording process
function restartRecording() {
    try {
        isRecording = false;
        isProcessing = false;
        audioChunks = [];
        
        if (silenceTimeout) {
            clearTimeout(silenceTimeout);
            silenceTimeout = null;
        }

        // Clean up media recorder if it exists
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            try {
                mediaRecorder.stop();
            } catch (e) {
                console.warn('Error stopping mediaRecorder:', e);
            }
        }

        // Clean up stream tracks
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
            currentStream = null;
        }
        
        // Clear messages after a delay
        setTimeout(() => {
            humanMessage.classList.remove('show-message');
            aiMessage.classList.remove('show-message');
            // Start a new recording cycle
            startVoiceChatLoop();
        }, 1000);
    } catch (error) {
        console.error('Error in restartRecording:', error);
        // If restart fails, try again after a longer delay
        setTimeout(restartRecording, 2000);
    }
}
// Detect Silence and Stop Recording
function detectSilence(stream) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    analyser.fftSize = 2048;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    const checkSilence = () => {
        if (!mediaRecorder || mediaRecorder.state === "inactive") return; // Early exit if not recording
        analyser.getByteFrequencyData(dataArray);
        const averageVolume = dataArray.reduce((a, b) => a + b) / dataArray.length;

        if (averageVolume < SILENCE_THRESHOLD_VALUE) {
            if (!silenceTimeout) {
                silenceTimeout = setTimeout(() => {
                    if (mediaRecorder.state === "recording") { // Check state before stopping
                        mediaRecorder.stop(); // Stop recording on silence
                    }
                }, SILENCE_THRESHOLD);
            }
        } else {
            clearTimeout(silenceTimeout);
            silenceTimeout = null;
        }

        requestAnimationFrame(checkSilence); // Continuously check for silence
    };

    setTimeout(() => {
        checkSilence(); // Start checking for silence after the initial delay
    }, SILENCE_DETECTION_DELAY);
}

// Play Audio and Wait
function playAudioAndWait(audioSource) {
    return new Promise((resolve, reject) => {
        const audioPlayer = document.getElementById('audioPlayer');
        audioPlayer.src = audioSource;
        audioPlayer.play()
            .then(() => {
                audioPlayer.addEventListener('ended', resolve, { once: true });
            })
            .catch(reject);
    });
}

// Particle Animation (if needed)
function initializeParticles() {
    const particlesContainer = document.querySelector('.particles');
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 15}s`;
        particlesContainer.appendChild(particle);
    }
}

// Initialize particles when the script is loaded
initializeParticles();
    