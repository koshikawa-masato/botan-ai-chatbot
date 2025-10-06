// WebSocket接続
let ws = null;
let isConnected = false;

// DOM要素
const chatArea = document.getElementById('chatArea');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const voiceToggle = document.getElementById('voiceToggle');
const reflectionToggle = document.getElementById('reflectionToggle');
const typingIndicator = document.getElementById('typingIndicator');

// WebSocket接続
function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket connected');
        isConnected = true;
        updateStatus(true);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        isConnected = false;
        updateStatus(false);

        // 3秒後に再接続
        setTimeout(connect, 3000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleResponse(data);
    };
}

// ステータス更新
function updateStatus(connected) {
    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = '接続済み';
        sendButton.disabled = false;
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = '切断中...';
        sendButton.disabled = true;
    }
}

// メッセージ送信
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !isConnected) return;

    // ユーザーメッセージを表示
    addMessage('user', message);

    // タイピングインジケータ表示
    showTyping(true);

    // WebSocketで送信
    const data = {
        type: 'chat',
        message: message,
        user_id: 'web_user',
        enable_voice: voiceToggle.checked,
        enable_reflection: reflectionToggle.checked,
        timestamp: Date.now() / 1000
    };

    ws.send(JSON.stringify(data));

    // 入力欄をクリア
    messageInput.value = '';
}

// レスポンス処理
function handleResponse(data) {
    // タイピングインジケータ非表示
    showTyping(false);

    if (data.type === 'error') {
        addMessage('botan', `エラー: ${data.error}`, null, true);
        return;
    }

    // 牡丹のメッセージを表示
    const audioUrl = data.audio_url;
    addMessage('botan', data.response, audioUrl);

    // 音声自動再生（オプション）
    if (audioUrl && voiceToggle.checked) {
        // 自動再生は多くのブラウザでブロックされるため、ボタンクリックに任せる
    }
}

// メッセージ追加
function addMessage(sender, text, audioUrl = null, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🌸';

    const content = document.createElement('div');
    content.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;

    if (isError) {
        bubble.style.background = '#ffebee';
        bubble.style.color = '#c62828';
    }

    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit'
    });

    content.appendChild(bubble);
    content.appendChild(time);

    // 音声プレーヤー
    if (audioUrl) {
        const audioPlayer = createAudioPlayer(audioUrl);
        content.appendChild(audioPlayer);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    // タイピングインジケータの前に挿入
    chatArea.insertBefore(messageDiv, typingIndicator);

    // スクロール
    scrollToBottom();
}

// 音声プレーヤー作成
function createAudioPlayer(audioUrl) {
    const playerDiv = document.createElement('div');
    playerDiv.className = 'audio-player';

    const playButton = document.createElement('button');
    playButton.innerHTML = '▶️ 音声再生';

    const audio = new Audio(audioUrl);

    playButton.onclick = () => {
        if (audio.paused) {
            audio.play();
            playButton.innerHTML = '⏸️ 停止';
        } else {
            audio.pause();
            audio.currentTime = 0;
            playButton.innerHTML = '▶️ 音声再生';
        }
    };

    audio.onended = () => {
        playButton.innerHTML = '▶️ 音声再生';
    };

    playerDiv.appendChild(playButton);

    return playerDiv;
}

// タイピングインジケータ
function showTyping(show) {
    if (show) {
        typingIndicator.classList.add('active');
        scrollToBottom();
    } else {
        typingIndicator.classList.remove('active');
    }
}

// スクロール
function scrollToBottom() {
    setTimeout(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    }, 100);
}

// イベントリスナー
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// 初期化
connect();
