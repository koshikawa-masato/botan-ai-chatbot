/**
 * Botan OBS Subtitle Overlay
 * WebSocket-based real-time subtitle display for OBS Browser Source
 */

let ws = null;
let reconnectInterval = null;
const MAX_SUBTITLES = 3; // Maximum number of subtitles displayed simultaneously
const SUBTITLE_DURATION = 5000; // 5 seconds

// DOM Elements
const subtitleContainer = document.getElementById('subtitle-container');
const statusIndicator = document.getElementById('status');
const statusText = document.getElementById('status-text');

// WebSocket Connection
function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/obs`;

    console.log('[OBS Subtitle] Connecting to:', wsUrl);
    updateStatus('Connecting...', 'disconnected');

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('[OBS Subtitle] Connected');
        updateStatus('Connected', 'connected');
        clearInterval(reconnectInterval);

        // Send initial connection message
        ws.send(JSON.stringify({
            type: 'obs_connect',
            timestamp: Date.now() / 1000
        }));
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('[OBS Subtitle] Received:', data);

            if (data.type === 'subtitle' || data.type === 'chat_response') {
                handleSubtitle(data);
            } else if (data.type === 'typing') {
                showTypingIndicator();
            }
        } catch (error) {
            console.error('[OBS Subtitle] Parse error:', error);
        }
    };

    ws.onerror = (error) => {
        console.error('[OBS Subtitle] WebSocket error:', error);
        updateStatus('Error', 'disconnected');
    };

    ws.onclose = () => {
        console.log('[OBS Subtitle] Disconnected');
        updateStatus('Disconnected', 'disconnected');

        // Auto-reconnect after 3 seconds
        reconnectInterval = setInterval(() => {
            console.log('[OBS Subtitle] Reconnecting...');
            connect();
        }, 3000);
    };
}

// Handle Subtitle Display
function handleSubtitle(data) {
    const text = data.response || data.text || data.message;
    const speaker = data.speaker || 'botan'; // 'botan' or 'user'
    const duration = data.duration || SUBTITLE_DURATION;

    if (!text) {
        console.warn('[OBS Subtitle] No text in message:', data);
        return;
    }

    removeTypingIndicator();
    showSubtitle(text, speaker, duration);
}

// Show Subtitle with Animation
function showSubtitle(text, speaker, duration) {
    // Create subtitle element
    const subtitleDiv = document.createElement('div');
    subtitleDiv.className = `subtitle-text ${speaker}-style`;

    // Add speaker name (optional)
    if (speaker === 'botan') {
        const speakerName = document.createElement('span');
        speakerName.className = 'speaker-name';
        speakerName.textContent = '🌸 牡丹';
        subtitleDiv.appendChild(speakerName);
    }

    // Add text content
    const textNode = document.createTextNode(text);
    subtitleDiv.appendChild(textNode);

    // Add to container
    subtitleContainer.appendChild(subtitleDiv);

    // Limit number of subtitles
    limitSubtitles();

    // Auto-remove after duration
    setTimeout(() => {
        subtitleDiv.style.animation = 'fadeOut 0.5s ease-out';
        setTimeout(() => {
            if (subtitleDiv.parentNode) {
                subtitleDiv.remove();
            }
        }, 500);
    }, duration);
}

// Typing Indicator
function showTypingIndicator() {
    // Check if already exists
    if (document.querySelector('.typing-indicator')) {
        return;
    }

    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.textContent = '🌸 牡丹 is typing...';
    typingDiv.id = 'typing-indicator';

    subtitleContainer.appendChild(typingDiv);
}

function removeTypingIndicator() {
    const typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Limit Subtitles to MAX_SUBTITLES
function limitSubtitles() {
    const subtitles = subtitleContainer.querySelectorAll('.subtitle-text');

    if (subtitles.length > MAX_SUBTITLES) {
        // Remove oldest subtitle
        const oldest = subtitles[0];
        oldest.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            if (oldest.parentNode) {
                oldest.remove();
            }
        }, 300);
    }
}

// Update Status Indicator
function updateStatus(text, status) {
    statusText.textContent = text;
    statusIndicator.className = `status-indicator ${status}`;

    // Hide status after 3 seconds when connected
    if (status === 'connected') {
        setTimeout(() => {
            statusIndicator.style.display = 'none';
        }, 3000);
    } else {
        statusIndicator.style.display = 'block';
    }
}

// Test Mode (URL parameter ?test=1)
function testMode() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('test') === '1') {
        console.log('[OBS Subtitle] Test mode enabled');

        // Show test subtitles
        setTimeout(() => {
            showSubtitle('やっほー！オジサン！', 'botan', 3000);
        }, 1000);

        setTimeout(() => {
            showSubtitle('今日も配信がんばろ〜', 'botan', 3000);
        }, 3000);

        setTimeout(() => {
            showSubtitle('マジで楽しい！', 'botan', 3000);
        }, 5000);
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    console.log('[OBS Subtitle] Initializing...');
    connect();
    testMode();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (ws) {
        ws.close();
    }
    clearInterval(reconnectInterval);
});
