// AI Assistant Modal JavaScript

// DOM Elements
const modal = document.getElementById('aiAssistantModal');
const openBtn = document.getElementById('askMagicBtn');
const closeBtn = document.querySelector('.close-btn');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micBtn');
const chatWindow = document.getElementById('chatWindow');
const timerDisplay = document.querySelector('.recording-timer');
const waveform = document.getElementById('waveform');
const voiceStatus = document.getElementById('voiceStatus');
const voiceStatusText = voiceStatus ? voiceStatus.querySelector('.voice-status-text') : null;

// Recording state
let mediaRecorder = null;
let audioChunks = [];
let recordingTimer = null;
let recordingSeconds = 0;
let isUploadingVoice = false;

// Modal Control
openBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
    setTimeout(() => modal.classList.add('active'), 10);
});

closeBtn.addEventListener('click', () => {
    modal.classList.remove('active');
    setTimeout(() => modal.classList.add('hidden'), 300);
});

// Close on overlay click
modal.addEventListener('click', (e) => {
    if (e.target === modal || e.target.classList.contains('modal-overlay')) {
        closeBtn.click();
    }
});

// Text Chat Handler
async function sendTextMessage(text) {
    if (!text.trim()) return;
    
    // Add user message
    appendMessage('user', text);
    
    // Clear input
    chatInput.value = '';
    
    // Show loading
    showLoading();
    
    try {
        // Send to backend
        const formData = new FormData();
        formData.append('msg', text);
        
        const response = await fetch('/get', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Hide loading
        hideLoading();
        
        // Show bot response
        appendMessage('bot', data.answer || data.error || 'No response');
        
    } catch (error) {
        hideLoading();
        appendMessage('bot', 'Sorry, there was an error processing your message.');
        console.error('Chat error:', error);
    }
}

sendBtn.addEventListener('click', () => {
    const text = chatInput.value.trim();
    if (text) {
        sendTextMessage(text);
    }
});

// Enter key support
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

// Voice Recording Handler
micBtn.addEventListener('click', async () => {
    if (isUploadingVoice) {
        return;
    }
    
    if (!mediaRecorder) {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (e) => {
                audioChunks.push(e.data);
            };
            
            mediaRecorder.onstop = async () => {
                const blob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                stopRecordingUI();
                await sendVoiceMessage(blob);
            };
            
            mediaRecorder.start();
            startRecordingUI();
            
            // Auto-stop after 10 seconds
            setTimeout(() => {
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    mediaRecorder = null;
                }
            }, 10000);
            
        } catch (err) {
            console.error('Microphone error:', err);
            alert('Microphone access denied. Please enable it in your browser settings.');
        }
    } else {
        // Stop recording
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        mediaRecorder = null;
    }
});

function startRecordingUI() {
    micBtn.classList.add('recording');
    timerDisplay.classList.remove('hidden');
    waveform.classList.remove('hidden');
    recordingSeconds = 0;
    
    recordingTimer = setInterval(() => {
        recordingSeconds++;
        const mins = Math.floor(recordingSeconds / 60);
        const secs = recordingSeconds % 60;
        timerDisplay.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    }, 1000);
}

function stopRecordingUI() {
    micBtn.classList.remove('recording');
    timerDisplay.classList.add('hidden');
    waveform.classList.add('hidden');
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
}

// Voice Query Handler
async function sendVoiceMessage(audioBlob) {
    setMicProcessingState(true);
    showVoiceStatus('Sending voice clip...');
    
    // Show processing indicator in chat
    const statusMessageId = appendMessage('system', '📤 Sending voice clip...');
    
    try {
        // Upload to backend
        const formData = new FormData();
        formData.append('file', audioBlob, 'voice.webm');
        
        const response = await fetch('/voice-query', {
            method: 'POST',
            body: formData
        });
        
        showVoiceStatus('Processing response...');
        updateMessageText(statusMessageId, '🎤 Transcribing audio...');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove status message
        removeMessage(statusMessageId);
        
        // Show transcription as user message
        appendMessage('user', `🎤 ${data.text}`);
        
        // Show bot answer
        appendMessage('bot', data.answer);
        
        // Play TTS audio
        if (data.audio_base64) {
            const audio = new Audio(`data:audio/mpeg;base64,${data.audio_base64}`);
            audio.play().catch(err => {
                console.error('Audio playback error:', err);
            });
        }
        
    } catch (error) {
        removeMessage(statusMessageId);
        appendMessage('bot', 'Sorry, there was an error processing your voice message.');
        console.error('Voice error:', error);
    } finally {
        hideVoiceStatus();
        setMicProcessingState(false);
    }
}

// Chat UI Utilities
function appendMessage(type, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    const messageId = `msg-${Date.now()}-${Math.random()}`;
    messageDiv.id = messageId;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    if (type === 'bot') {
        messageDiv.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="bubble">
                ${text}
                <span class="time">${timestamp}</span>
            </div>
        `;
    } else if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="bubble">
                ${text}
                <span class="time">${timestamp}</span>
            </div>
            <div class="avatar">👤</div>
        `;
    } else {
        messageDiv.innerHTML = `<div class="bubble">${text}</div>`;
    }
    
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    
    // Remove empty state if exists
    const emptyState = chatWindow.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    return messageId;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-indicator';
    loadingDiv.id = 'loading-indicator';
    loadingDiv.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    chatWindow.appendChild(loadingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function hideLoading() {
    const loading = document.getElementById('loading-indicator');
    if (loading) {
        loading.remove();
    }
}

function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

function updateMessageText(messageId, newText) {
    const message = document.getElementById(messageId);
    if (!message) return;
    
    const bubble = message.querySelector('.bubble');
    if (bubble) {
        bubble.textContent = newText;
    }
}

function setMicProcessingState(isProcessing) {
    isUploadingVoice = isProcessing;
    micBtn.disabled = isProcessing;
    micBtn.classList.toggle('processing', isProcessing);
    if (!isProcessing) {
        micBtn.blur();
    }
}

function showVoiceStatus(message) {
    if (!voiceStatus) return;
    if (voiceStatusText) {
        voiceStatusText.textContent = message;
    } else {
        voiceStatus.textContent = message;
    }
    voiceStatus.classList.remove('hidden');
}

function hideVoiceStatus() {
    if (!voiceStatus) return;
    voiceStatus.classList.add('hidden');
}

