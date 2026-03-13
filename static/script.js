const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const messagesContainer = document.getElementById('messages');
const historyList = document.getElementById('chat-history-list');

// =====================================================
// VOICE INPUT (Speech-to-Text)
// =====================================================
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let silenceTimer = null;
const micBtn = document.getElementById('mic-btn');

const SILENCE_THRESHOLD = 2000;

function getSupportedMimeType() {
    const types = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/wav',
        'audio/mp4',
        ''
    ];

    for (const type of types) {
        if (!type) {
            return null;
        }
        if (MediaRecorder.isTypeSupported(type)) {
            console.log('Using MIME type:', type);
            return type;
        }
    }
    return null;
}

async function startRecording() {
    try {
        console.log('Requesting microphone access...');
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        });
        console.log('Microphone access granted');

        const mimeType = getSupportedMimeType();
        console.log('Supported MIME type:', mimeType);

        if (!mimeType) {
            alert('Audio recording not supported in this browser. Try Chrome or Edge.');
            return;
        }

        mediaRecorder = new MediaRecorder(stream, { mimeType });
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            console.log('Audio data available, size:', event.data.size);
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                resetSilenceTimer();
            }
        };

        mediaRecorder.onerror = event => {
            console.error('MediaRecorder error:', event);
        };

        mediaRecorder.onstop = () => {
            console.log('Recording stopped, chunks:', audioChunks.length);
            sendAudioToServer();
        };

        mediaRecorder.start(200);
        isRecording = true;
        micBtn.classList.add('recording');
        userInput.placeholder = 'Listening... (click mic to stop)';

        startSilenceDetection();
    } catch (err) {
        console.error('Mic error:', err);
        alert('Could not access microphone: ' + err.message + '\n\nPlease allow microphone permission and try again.');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;
        micBtn.classList.remove('recording');
        micBtn.classList.add('processing');
        userInput.placeholder = 'Processing...';
        clearSilenceTimer();
    }
}

function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function startSilenceDetection() {
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(mediaRecorder.stream);
    source.connect(analyser);
    analyser.fftSize = 256;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    const checkSilence = () => {
        if (!isRecording) return;

        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;

        if (average < 5) { // Very quiet
            if (!silenceTimer) {
                silenceTimer = setTimeout(() => {
                    stopRecording();
                }, SILENCE_THRESHOLD);
            }
        } else {
            clearSilenceTimer();
        }

        if (isRecording) {
            requestAnimationFrame(checkSilence);
        }
    };

    checkSilence();
}

function resetSilenceTimer() {
    clearSilenceTimer();
    if (isRecording) {
        silenceTimer = setTimeout(() => {
            stopRecording();
        }, SILENCE_THRESHOLD);
    }
}

function clearSilenceTimer() {
    if (silenceTimer) {
        clearTimeout(silenceTimer);
        silenceTimer = null;
    }
}

async function sendAudioToServer() {
    if (audioChunks.length === 0) {
        alert('No audio recorded. Please try again.');
        micBtn.classList.remove('processing');
        userInput.placeholder = 'Ask Ramya anything...';
        return;
    }

    try {
        console.log('Sending audio, chunks:', audioChunks.length);

        const audioBlob = new Blob(audioChunks, { type: getSupportedMimeType() || 'audio/webm' });
        console.log('Audio blob size:', audioBlob.size);

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        console.log('Sending to /stt endpoint...');
        const response = await fetch('/stt', {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('STT error:', errorData);
            alert('Voice recognition failed: ' + (errorData.error || 'Unknown error'));
            return;
        }

        const data = await response.json();
        console.log('Transcription result:', data.text);

        if (data.text && data.text.trim()) {
            userInput.value = data.text.trim();
            chatForm.dispatchEvent(new Event('submit'));
        } else {
            alert('Could not understand. Please try again.');
        }
    } catch (err) {
        console.error('STT error:', err);
        alert('Voice recognition failed: ' + err.message);
    } finally {
        micBtn.classList.remove('processing');
        userInput.placeholder = 'Ask Ramya anything...';
    }
}

// Single click to toggle recording
micBtn?.addEventListener('click', toggleRecording);

// =====================================================
// VOICE SETTINGS STATE (Tasks 3 & 4)
// =====================================================
let isMuted = localStorage.getItem('ramya_muted') === 'true';

const muteBtn = document.getElementById('mute-btn');
const voiceSettingsBtn = document.getElementById('voice-settings-btn');
const voicePanel = document.getElementById('voice-settings-panel');
const voiceSelect = document.getElementById('voice-select');
const rateSlider = document.getElementById('rate-slider');
const pitchSlider = document.getElementById('pitch-slider');
const rateLabel = document.getElementById('rate-label');
const pitchLabel = document.getElementById('pitch-label');

// Restore saved voice settings from localStorage (only on chat page)
if (voiceSelect && localStorage.getItem('ramya_voice')) voiceSelect.value = localStorage.getItem('ramya_voice');
if (rateSlider && localStorage.getItem('ramya_rate')) rateSlider.value = localStorage.getItem('ramya_rate');
if (pitchSlider && localStorage.getItem('ramya_pitch')) pitchSlider.value = localStorage.getItem('ramya_pitch');

function updateMuteUI() {
    if (!muteBtn) return;
    muteBtn.textContent = isMuted ? '🔇' : '🔊';
    muteBtn.classList.toggle('muted', isMuted);
}
if (muteBtn) updateMuteUI();

if (muteBtn) muteBtn.addEventListener('click', () => {
    isMuted = !isMuted;
    localStorage.setItem('ramya_muted', isMuted);
    updateMuteUI();
});

if (voiceSettingsBtn) voiceSettingsBtn.addEventListener('click', () => {
    voicePanel.style.display = voicePanel.style.display === 'none' ? 'block' : 'none';
});

function rateToPercent(val) {
    // val in range -50..100, display as e.g. "+20%" or "-10%"
    const sign = val >= 0 ? '+' : '';
    return `${sign}${val}%`;
}
function pitchToHz(val) {
    const sign = val >= 0 ? '+' : '';
    return `${sign}${val}Hz`;
}

function updateRateLabel() {
    if (!rateSlider || !rateLabel) return;
    const displayX = (parseInt(rateSlider.value) / 100) + 1;
    rateLabel.textContent = `${displayX}x`;
    localStorage.setItem('ramya_rate', rateSlider.value);
}
function updatePitchLabel() {
    if (!pitchSlider || !pitchLabel) return;
    pitchLabel.textContent = `${pitchSlider.value} Hz`;
    localStorage.setItem('ramya_pitch', pitchSlider.value);
}
if (rateSlider) rateSlider.addEventListener('input', updateRateLabel);
if (pitchSlider) pitchSlider.addEventListener('input', updatePitchLabel);
if (voiceSelect) voiceSelect.addEventListener('change', () => localStorage.setItem('ramya_voice', voiceSelect.value));
if (rateSlider) updateRateLabel();
if (pitchSlider) updatePitchLabel();

// =====================================================
// SENTENCE DETECTOR - Detects sentence boundaries during streaming
// =====================================================
class SentenceDetector {
    constructor() {
        this.buffer = '';
        this.sentences = [];
        // Abbreviations to ignore for sentence splitting
        this.abbreviations = ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Sr', 'Jr', 'vs', 'etc', 'i.e', 'e.g', 'St', 'Ave', 'Blvd', 'Rd', 'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    }

    addToken(token) {
        this.buffer += token;
        return this.checkForSentence();
    }

    checkForSentence() {
        // Match sentence endings: . ! ? followed by space or end
        // But ignore common abbreviations
        const sentenceEndPattern = /[.!?]+(\s|$)/g;
        let match;
        let lastIndex = 0;

        while ((match = sentenceEndPattern.exec(this.buffer)) !== null) {
            const potentialEnd = match.index + match[0].length;
            const potentialSentence = this.buffer.substring(0, potentialEnd).trim();

            // Check if it ends with an abbreviation
            const beforePunctuation = potentialSentence.replace(/[.!?]+\s*$/, '');
            const endsWithAbbreviation = this.abbreviations.some(abbr =>
                beforePunctuation.endsWith(abbr) || beforePunctuation.endsWith(abbr.toLowerCase())
            );

            if (!endsWithAbbreviation && potentialSentence.length > 0) {
                this.buffer = this.buffer.substring(potentialEnd);
                return potentialSentence;
            }
        }
        return null;
    }

    flush() {
        const remaining = this.buffer.trim();
        this.buffer = '';
        return remaining.length > 0 ? remaining : null;
    }
}

// =====================================================
// AUDIO QUEUE MANAGER - Manages parallel TTS and sequential playback
// =====================================================
class AudioQueueManager {
    constructor() {
        this.audioQueue = [];           // {audioBlob, sentence, index}
        this.pendingRequests = new Map(); // index -> Promise
        this.isPlaying = false;
        this.currentIndex = 0;
        this.currentAudio = null;
        this.onSentencePlay = null;     // Callback when sentence starts playing
        this.onSentenceEnd = null;      // Callback when sentence ends
        this.onQueueComplete = null;    // Callback when all sentences played
        this.isStopped = false;
    }

    async fetchTTS(sentence, index, voice, rate, pitch) {
        try {
            const cleanSentence = sentence.trim();
            if (!cleanSentence) return { audioBlob: null, sentence: '', index };

            const response = await fetch('/tts_stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: cleanSentence, voice, rate, pitch })
            });

            if (!response.ok) {
                throw new Error('TTS request failed');
            }

            const audioBlob = await response.blob();
            return { audioBlob, sentence: cleanSentence, index };
        } catch (error) {
            console.warn(`TTS failed for sentence ${index}:`, error);
            return { audioBlob: null, sentence, index };
        }
    }

    addSentence(sentence, index, voice, rate, pitch) {
        if (this.isStopped) return;

        const promise = this.fetchTTS(sentence, index, voice, rate, pitch);
        this.pendingRequests.set(index, promise);

        promise.then(result => {
            if (this.isStopped) return;

            this.audioQueue.push(result);
            this.audioQueue.sort((a, b) => a.index - b.index);

            // Start playing if this is the next sentence to play
            if (result.index === this.currentIndex && !this.isPlaying) {
                this.playNext();
            }
        });
    }

    playNext() {
        if (this.isStopped) return;

        // Find the next sentence to play
        const nextItem = this.audioQueue.find(item => item.index === this.currentIndex);

        if (nextItem && nextItem.audioBlob) {
            this.isPlaying = true;
            const audioUrl = URL.createObjectURL(nextItem.audioBlob);
            this.currentAudio = new Audio(audioUrl);

            if (this.onSentencePlay) {
                this.onSentencePlay(nextItem.sentence, nextItem.index);
            }

            this.currentAudio.onended = () => {
                URL.revokeObjectURL(audioUrl);
                this.currentIndex++;

                if (this.onSentenceEnd) {
                    this.onSentenceEnd(nextItem.sentence, nextItem.index);
                }

                // Check if more sentences to play
                const hasNext = this.audioQueue.some(item => item.index === this.currentIndex) ||
                    this.pendingRequests.size > this.audioQueue.length;

                if (hasNext) {
                    this.playNext();
                } else {
                    this.isPlaying = false;
                    if (this.onQueueComplete) {
                        this.onQueueComplete();
                    }
                }
            };

            this.currentAudio.onerror = () => {
                console.warn('Audio playback error');
                this.currentIndex++;
                this.isPlaying = false;
                this.playNext();
            };

            this.currentAudio.play();
        } else if (nextItem) {
            // Audio failed but we have the sentence, just show text and continue
            if (this.onSentencePlay) {
                this.onSentencePlay(nextItem.sentence, nextItem.index);
            }
            this.currentIndex++;
            setTimeout(() => this.playNext(), 100);
        } else if (this.pendingRequests.size > this.audioQueue.length) {
            // Still waiting for audio, retry after short delay
            setTimeout(() => this.playNext(), 100);
        } else {
            this.isPlaying = false;
            if (this.onQueueComplete) {
                this.onQueueComplete();
            }
        }
    }

    stop() {
        this.isStopped = true;
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        this.audioQueue = [];
        this.pendingRequests.clear();
        this.isPlaying = false;
    }
}

// =====================================================
// HELPER: PLAY TTS SENTENCE BY SENTENCE (Streaming)
// =====================================================
let globalAudioManager = null;

async function playTTSSentenceBySentence(msgDiv, fullText) {
    if (isMuted) {
        // If muted, just show the full text immediately
        msgDiv.innerHTML = safeMarkdownParse(fullText);
        return;
    }

    const rate = rateToPercent(parseInt(rateSlider?.value || 0));
    const pitch = pitchToHz(parseInt(pitchSlider?.value || 0));
    const voice = voiceSelect?.value || 'en-US-JennyNeural';

    // Split text into sentences
    const sentences = splitIntoSentences(fullText);

    if (sentences.length === 0) {
        msgDiv.innerHTML = marked.parse(fullText);
        return;
    }

    // Create container for sentence spans
    msgDiv.innerHTML = '';
    const sentenceContainer = document.createElement('div');
    sentenceContainer.className = 'sentence-container';
    msgDiv.appendChild(sentenceContainer);

    // Create audio manager
    try {
        globalAudioManager = new AudioQueueManager();
    } catch (e) {
        console.error("Failed to create AudioManager:", e);
        msgDiv.innerHTML = safeMarkdownParse(fullText);
        return;
    }
    let currentSentenceIndex = -1;

    // Callback when a sentence starts playing
    globalAudioManager.onSentencePlay = (sentence, index) => {
        console.log(`Playing sentence ${index}: ${sentence.substring(0, 20)}...`);
        // Highlight current sentence
        const allSpans = sentenceContainer.querySelectorAll(".sentence-span");
        allSpans.forEach((span, i) => {
            if (i < index) {
                span.classList.remove("current-sentence");
                span.classList.add("played-sentence");
            } else if (i === index) {
                span.classList.add("current-sentence");
                span.classList.remove("played-sentence");
            }
        });

        // Show the sentence if not already visible
        let span = document.getElementById(`sentence-span-${index}`);
        if (!span) {
            span = document.createElement("span");
            span.id = `sentence-span-${index}`;
            span.className = "sentence-span current-sentence";
            span.innerHTML = safeMarkdownParse(sentence);
            sentenceContainer.appendChild(span);
        } else {
            // Already there but might need highlighting
            span.classList.add("current-sentence");
            span.classList.remove("played-sentence");
        }

        // Scroll to show current sentence
        const chatArea = document.querySelector(".messages-container");
        if (chatArea) {
            chatArea.scrollTop = chatArea.scrollHeight;
        }
    };

    // Callback when a sentence ends
    globalAudioManager.onSentenceEnd = (sentence, index) => {
        const span = document.getElementById(`sentence-span-${index}`);
        if (span) {
            span.classList.remove('current-sentence');
            span.classList.add('played-sentence');
        }
    };

    // Callback when all sentences complete
    globalAudioManager.onQueueComplete = () => {
        globalAudioManager = null;
    };

    // Add all sentences to the queue (parallel TTS requests)
    sentences.forEach((sentence, index) => {
        globalAudioManager.addSentence(sentence, index, voice, rate, pitch);
    });
}

function splitIntoSentences(text) {
    // Split on sentence boundaries (. ! ?) but handle abbreviations
    const abbreviations = ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Sr', 'Jr', 'vs', 'etc', 'i.e', 'e.g', 'St', 'Ave', 'Blvd', 'Rd', 'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    const result = [];
    let buffer = '';

    // Match sentence endings: . ! ? followed by space or end
    const sentenceEndPattern = /[.!?]+(\s|$)/g;
    let match;
    let lastIndex = 0;

    while ((match = sentenceEndPattern.exec(text)) !== null) {
        const potentialEnd = match.index + match[0].length;
        const potentialSentence = text.substring(lastIndex, potentialEnd).trim();

        // Check if it ends with an abbreviation
        const beforePunctuation = potentialSentence.replace(/[.!?]+\s*$/, '');
        const endsWithAbbreviation = abbreviations.some(abbr =>
            beforePunctuation.endsWith(abbr) || beforePunctuation.endsWith(abbr.toLowerCase())
        );

        if (!endsWithAbbreviation && potentialSentence.length > 0) {
            result.push(potentialSentence);
            lastIndex = potentialEnd;
        }
    }

    // Add remaining text as final sentence
    const remaining = text.substring(lastIndex).trim();
    if (remaining.length > 0) {
        result.push(remaining);
    }

    return result;
}

// Keep old function for backward compatibility (replay button)
async function playTTSWithSync(msgDiv, fullText) {
    if (isMuted) {
        msgDiv.innerHTML = safeMarkdownParse(fullText);
        return;
    }

    const rate = rateToPercent(parseInt(rateSlider?.value || 0));
    const pitch = pitchToHz(parseInt(pitchSlider?.value || 0));
    const voice = voiceSelect?.value || 'en-US-JennyNeural';

    try {
        const ttsResp = await fetch('/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: fullText, voice, rate, pitch })
        });

        if (!ttsResp.ok) {
            msgDiv.innerHTML = safeMarkdownParse(fullText);
            return;
        }

        const audioBlob = await ttsResp.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        window.currentAudio = audio;
        audio.play();

        audio.addEventListener('ended', () => {
            URL.revokeObjectURL(audioUrl);
            window.currentAudio = null;
        });

    } catch (ttsErr) {
        console.warn("TTS unavailable:", ttsErr);
        msgDiv.innerHTML = safeMarkdownParse(fullText);
    }
}

function safeMarkdownParse(text) {
    if (typeof marked !== 'undefined' && marked.parse) {
        return marked.parse(text);
    }
    console.warn("marked.js not loaded, falling back to plain text");
    return escapeHtml(text).replace(/\n/g, '<br>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// =====================================================
// HELPER: ADD COPY BUTTON (Task 7)
// =====================================================
function addCopyButton(wrapper, msgDiv) {
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.title = 'Copy reply';
    copyBtn.textContent = '📋 Copy';
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(msgDiv.textContent).then(() => {
            copyBtn.textContent = '✅ Copied!';
            copyBtn.classList.add('copied');
            setTimeout(() => {
                copyBtn.textContent = '📋 Copy';
                copyBtn.classList.remove('copied');
            }, 2000);
        });
    });
    wrapper.appendChild(copyBtn);
}

// =====================================================
// HELPER: ADD PLAY BUTTON (Replay TTS)
// =====================================================
function addPlayButton(wrapper, msgDiv) {
    const playBtn = document.createElement('button');
    playBtn.className = 'play-btn';
    playBtn.title = 'Play voice';
    playBtn.textContent = '🔊';

    playBtn.addEventListener('click', async () => {
        if (window.currentAudio && window.currentAudio.playing) {
            window.currentAudio.pause();
            window.currentAudio = null;
            playBtn.textContent = '🔊';
            return;
        }

        playBtn.textContent = '⏳';

        const rate = rateToPercent(parseInt(rateSlider.value));
        const pitch = pitchToHz(parseInt(pitchSlider.value));
        const voice = voiceSelect.value;

        // Get plain text from the message div
        const msgText = msgDiv.textContent;

        try {
            const ttsResp = await fetch('/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: msgText, voice, rate, pitch })
            });

            if (!ttsResp.ok) {
                playBtn.textContent = '🔊';
                return;
            }

            const audioBlob = await ttsResp.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);

            window.currentAudio = audio;
            playBtn.textContent = '⏸';

            audio.addEventListener('ended', () => {
                playBtn.textContent = '🔊';
                URL.revokeObjectURL(audioUrl);
                window.currentAudio = null;
            });

            audio.play();
        } catch (e) {
            console.warn("TTS playback error:", e);
            playBtn.textContent = '🔊';
        }
    });

    wrapper.appendChild(playBtn);
}

// =====================================================
// HELPER: ADD TIMESTAMP (Task 6)
// =====================================================
function addTimestamp(msgDiv) {
    const timeSpan = document.createElement('span');
    timeSpan.className = 'msg-time';
    timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    msgDiv.appendChild(timeSpan);
}

// =====================================================
// CHAT FORM SUBMIT
// =====================================================
chatForm?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const message = userInput.value.trim();
    if (!message) return;

    const sendBtn = document.getElementById('send-btn');
    const stopBtn = document.getElementById('stop-btn');

    if (!currentChatName) {
        const autoName = message.substring(0, 30).replace(/[^a-zA-Z0-9_\-]/g, '');
        currentChatName = autoName || "new_chat";
        await fetch('/start_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: currentChatName })
        });
        await loadChatHistory();
        document.getElementById('status').innerText = "Online (" + currentChatName + ")";
    }

    userInput.disabled = true;
    sendBtn.style.display = 'none';
    stopBtn.style.display = 'block';

    // Display User Message
    appendMessage('user', message);
    userInput.value = '';

    // Add typing indicator
    const typingId = 'typing-' + Date.now();
    const typingWrapper = document.createElement('div');
    typingWrapper.id = typingId;
    typingWrapper.classList.add('message-wrapper', 'ramya-wrapper');
    typingWrapper.innerHTML = `<div class="message-bubble" style="font-style: italic; color: #94a3b8;">Ramya is typing...</div>`;
    messagesContainer.appendChild(typingWrapper);
    messagesContainer.parentElement.scrollTop = messagesContainer.parentElement.scrollHeight;

    let reader = null;

    stopBtn.onclick = () => {
        if (reader) {
            reader.cancel();
            stopBtn.style.display = 'none';
            sendBtn.style.display = 'block';
            userInput.disabled = false;
            userInput.focus();
        }
    };

    try {
        const response = await fetch('/send_message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, chat_name: currentChatName })
        });

        document.getElementById(typingId)?.remove();

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: "Server Error" }));
            throw new Error(errorData.message || "Server Error");
        }

        // Display Bot Response (Buffer mode - show "Generating voice" first)
        const wrapper = document.createElement('div');
        wrapper.classList.add('message-wrapper', 'ramya-wrapper');
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message-bubble', 'typing');
        wrapper.appendChild(msgDiv);
        messagesContainer.appendChild(wrapper);

        // Show "Generating voice..." indicator BEFORE streaming starts
        const ttsTypingId = 'typing-tts-' + Date.now();
        const typingWrapper = document.createElement('div');
        typingWrapper.id = ttsTypingId;
        typingWrapper.classList.add('message-wrapper', 'ramya-wrapper');
        typingWrapper.innerHTML = `<div class="message-bubble" style="font-style: italic; color: #94a3b8;">Generating voice...</div>`;
        messagesContainer.appendChild(typingWrapper);
        messagesContainer.parentElement.scrollTop = messagesContainer.parentElement.scrollHeight;

        // Buffer the streaming response
        let fullContent = "";

        reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            fullContent += chunk;

            // Optional: Live update the UI if needed, but we split into sentences anyway
            // msgDiv.innerHTML = marked.parse(fullContent);
        }

        // Streaming complete - add timestamp, copy button, and play button
        addTimestamp(msgDiv);
        addCopyButton(wrapper, msgDiv);
        addPlayButton(wrapper, msgDiv);

        // Use sentence-by-sentence streaming TTS
        console.log("Full response content length:", fullContent.length);
        if (fullContent.trim()) {
            try {
                await playTTSSentenceBySentence(msgDiv, fullContent);
            } catch (playErr) {
                console.error("Playback error, falling back to static text:", playErr);
                msgDiv.innerHTML = safeMarkdownParse(fullContent);
            }
        } else {
            console.warn("Empty response received from server");
            msgDiv.innerText = "Error: Empty response";
        }

        document.getElementById(ttsTypingId)?.remove();
        msgDiv.classList.remove('typing');

    } catch (error) {
        if (error.name !== 'AbortError') {
            // Remove any typing indicators
            const typingElements = messagesContainer.querySelectorAll('[id^="typing-"]');
            typingElements.forEach(el => el.remove());
            console.error("Error:", error);
            appendMessage('bot', "Error: " + error.message);
        }
    } finally {
        userInput.disabled = false;
        sendBtn.style.display = 'block';
        stopBtn.style.display = 'none';
        userInput.focus();
    }
});

// =====================================================
// appendMessage: used for history & errors (Task 6 timestamp)
// =====================================================
function appendMessage(role, text, storedTimestamp = null) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('message-wrapper', role === 'user' ? 'user-wrapper' : 'ramya-wrapper');

    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message-bubble');
    msgDiv.innerText = text;

    // Task 6: Timestamp - use stored timestamp if available
    if (storedTimestamp) {
        // Convert milliseconds timestamp to Date
        const date = new Date(storedTimestamp);
        const timeSpan = document.createElement('span');
        timeSpan.className = 'msg-time';
        timeSpan.textContent = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        msgDiv.appendChild(timeSpan);
    } else {
        // Generate current timestamp for new messages
        addTimestamp(msgDiv);
    }

    wrapper.appendChild(msgDiv);
    messagesContainer.appendChild(wrapper);

    const chatWindow = document.getElementById('chat-window');
    chatWindow.scrollTop = chatWindow.scrollHeight;
}


let currentChatName = "";

window.onload = async () => {
    console.log('Page loaded, currentChatName:', currentChatName);

    // Only run chat history loading if we are on a page that supports it
    if (!historyList && !document.getElementById('previous-chats-container')) {
        console.log('Not a chat or home page, skipping history load');
        return;
    }

    // Check for chat query parameter first (from home page)
    const urlParams = new URLSearchParams(window.location.search);
    const chatParam = urlParams.get('chat');
    console.log('Chat param from URL:', chatParam);

    if (chatParam) {
        try {
            console.log('Opening chat from URL:', chatParam);
            // Load chat history first, then open the specific chat
            await loadChatHistory();
            await startChatSession(chatParam);
            console.log('Chat loaded successfully');
            // Clean URL without reload
            window.history.replaceState({}, document.title, window.location.pathname);
        } catch (e) {
            console.error('Error loading chat:', e);
        }
    } else {
        await loadChatHistory();
    }
};

document.getElementById('new-chat-btn')?.addEventListener('click', () => {
    const chatName = prompt("What shall we name this new conversation?");
    if (chatName) {
        startChatSession(chatName.replace(/\s+/g, '_'));
    }
});

async function loadChatHistory() {
    if (!historyList) return;
    try {
        const resp = await fetch('/chats');
        const data = await resp.json();

        historyList.innerHTML = '';
        if (data.chats && data.chats.length > 0) {
            data.chats.forEach(chat => {
                const li = document.createElement('li');
                if (chat === currentChatName) li.classList.add('active-chat');

                const nameSpan = document.createElement('span');
                nameSpan.innerText = chat;
                nameSpan.style.flexGrow = "1";

                const deleteBtn = document.createElement('button');
                deleteBtn.innerHTML = '&times;';
                deleteBtn.classList.add('delete-chat-btn');
                deleteBtn.onclick = (e) => {
                    e.stopPropagation();
                    if (confirm(`Delete chat "${chat}"?`)) {
                        deleteChat(chat);
                    }
                };

                li.appendChild(nameSpan);
                li.appendChild(deleteBtn);
                li.onclick = () => startChatSession(chat);
                historyList.appendChild(li);
            });
        } else {
            historyList.innerHTML = '<li>No previous chats</li>';
        }
    } catch (e) { console.error("Error fetching chats:", e); }
}

async function deleteChat(chatName) {
    try {
        const resp = await fetch('/delete_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: chatName })
        });
        if (resp.ok) {
            if (currentChatName === chatName) {
                currentChatName = "";
                messagesContainer.innerHTML = '<div class="message bot">Select or start a new chat!</div>';
            }
            await loadChatHistory();
        }
    } catch (e) { console.error("Delete error:", e); }
}

async function startChatSession(chatName) {
    currentChatName = chatName;
    await fetch('/start_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: chatName })
    });

    await loadChatHistory();

    const historyResp = await fetch(`/chat_history/${encodeURIComponent(chatName)}`);
    const historyData = await historyResp.json();

    messagesContainer.innerHTML = '';
    if (historyData.history && historyData.history.length > 0) {
        historyData.history.forEach(item => {
            // Handle both old format (string) and new format (object)
            let text = typeof item === 'string' ? item : item.text;
            let timestamp = typeof item === 'object' ? item.timestamp : null;

            if (text.startsWith("User said: ")) {
                appendMessage('user', text.replace("User said: ", ""), timestamp);
            } else if (text.startsWith("Ramya replied: ")) {
                const botText = text.replace("Ramya replied: ", "");
                // Create message with play button for bot messages
                const wrapper = document.createElement('div');
                wrapper.classList.add('message-wrapper', 'ramya-wrapper');
                const msgDiv = document.createElement('div');
                msgDiv.classList.add('message-bubble');
                msgDiv.innerText = botText;

                // Add timestamp
                if (timestamp) {
                    const date = new Date(timestamp);
                    const timeSpan = document.createElement('span');
                    timeSpan.className = 'msg-time';
                    timeSpan.textContent = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    msgDiv.appendChild(timeSpan);
                }

                wrapper.appendChild(msgDiv);
                messagesContainer.appendChild(wrapper);

                // Add play button for bot messages
                addPlayButton(wrapper, msgDiv);
            }
        });
    } else {
        messagesContainer.innerHTML = '<div class="message bot">Hello! I\'m Ramya. What do you want?</div>';
    }

    const statusEl = document.getElementById('status');
    if (statusEl) statusEl.innerText = "Online (" + chatName + ")";
}

// ==================== HOME PAGE FUNCTIONS ====================

async function loadHomePage() {
    const container = document.getElementById('previous-chats-container');
    const noChatsMsg = document.getElementById('no-chats-message');

    try {
        const resp = await fetch('/chats');
        const data = await resp.json();

        container.innerHTML = '';

        if (data.chats && data.chats.length > 0) {
            noChatsMsg.style.display = 'none';

            for (let i = 0; i < data.chats.length; i++) {
                const chatName = data.chats[i];
                const gradientClass = `chat-bar-prev-${(i % 10) + 1}`;

                // Get last message preview
                const lastMessage = await getLastMessagePreview(chatName);

                const bar = document.createElement('div');
                bar.className = `chat-bar chat-bar-previous ${gradientClass}`;
                bar.innerHTML = `
                    <div class="chat-bar-icon">
                        <svg viewBox="0 0 24 24" width="24" height="24">
                            <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"></path>
                        </svg>
                    </div>
                    <div class="chat-bar-content">
                        <span class="chat-bar-title">${escapeHtml(chatName)}</span>
                        <span class="chat-bar-preview">${escapeHtml(lastMessage) || 'No messages yet'}</span>
                    </div>
                    <button class="delete-bar-btn" title="Delete chat">&times;</button>
                `;

                // Click to open chat
                bar.addEventListener('click', (e) => {
                    if (!e.target.classList.contains('delete-bar-btn')) {
                        openChatFromHome(chatName);
                    }
                });

                // Delete button
                const deleteBtn = bar.querySelector('.delete-bar-btn');
                deleteBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    deleteChatFromHome(chatName);
                });

                container.appendChild(bar);
            }
        } else {
            noChatsMsg.style.display = 'block';
        }
    } catch (e) {
        console.error('Error loading chats:', e);
        noChatsMsg.style.display = 'block';
        noChatsMsg.innerHTML = '<p>Error loading chats. Please try again.</p>';
    }
}

async function getLastMessagePreview(chatName) {
    try {
        const resp = await fetch(`/chat_history/${encodeURIComponent(chatName)}`);
        const data = await resp.json();

        if (data.history && data.history.length > 0) {
            const lastMsg = data.history[data.history.length - 1];
            const msgText = typeof lastMsg === 'string' ? lastMsg : (lastMsg.text || lastMsg.message || '');
            let preview = msgText.replace('User said: ', '').replace('Ramya replied: ', '');
            if (preview.length > 50) {
                preview = preview.substring(0, 50) + '...';
            }
            return preview;
        }
    } catch (e) {
        console.error('Error getting last message:', e);
    }
    return '';
}

// New Chat button - create chat and redirect to chat page
document.getElementById('new-chat-bar')?.addEventListener('click', async () => {
    const chatName = prompt("What shall we name this new conversation?");
    if (chatName) {
        const safeName = chatName.replace(/\s+/g, '_');
        await fetch('/start_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: safeName })
        });
        window.location.href = '/chat?chat=' + encodeURIComponent(safeName);
    }
});

async function openChatFromHome(chatName) {
    console.log('Opening chat from home:', chatName);
    // Start the chat session
    await fetch('/start_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: chatName })
    });

    // Redirect to main chat page with chat name as query parameter
    window.location.href = '/chat?chat=' + encodeURIComponent(chatName);
}

async function deleteChatFromHome(chatName) {
    if (!confirm(`Delete chat "${chatName}"? This action cannot be undone.`)) {
        return;
    }

    try {
        const resp = await fetch('/delete_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: chatName })
        });

        if (resp.ok) {
            // Reload the home page to refresh the bars
            loadHomePage();
        } else {
            alert('Error deleting chat. Please try again.');
        }
    } catch (e) {
        console.error('Error deleting chat:', e);
        alert('Error deleting chat. Please try again.');
    }
}

// ==================== SECURITY & PASSWORD CHANGE ====================

const securityModal = document.getElementById('security-modal');
const openSecurityBtn = document.getElementById('open-security-btn');
const closeSecurityBtn = document.getElementById('close-security-modal');
const changePasswordForm = document.getElementById('change-password-form');
const passwordMessage = document.getElementById('password-message');

if (openSecurityBtn) {
    openSecurityBtn.addEventListener('click', (e) => {
        e.preventDefault();
        securityModal.style.display = 'block';
        passwordMessage.innerText = '';
        changePasswordForm.reset();
    });
}

if (closeSecurityBtn) {
    closeSecurityBtn.addEventListener('click', () => {
        securityModal.style.display = 'none';
    });
}

// Close on outside click
window.addEventListener('click', (event) => {
    if (event.target === securityModal) {
        securityModal.style.display = 'none';
    }
});

if (changePasswordForm) {
    changePasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const currentPassword = document.getElementById('current-password').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        if (newPassword !== confirmPassword) {
            passwordMessage.innerText = 'New passwords do not match';
            passwordMessage.className = 'error-text';
            return;
        }

        if (newPassword.length < 6) {
            passwordMessage.innerText = 'New password must be at least 6 characters';
            passwordMessage.className = 'error-text';
            return;
        }

        try {
            const resp = await fetch('/change_password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const result = await resp.json();

            if (resp.ok) {
                passwordMessage.innerText = 'Password updated successfully!';
                passwordMessage.className = 'error-text success-text';
                setTimeout(() => {
                    securityModal.style.display = 'none';
                }, 1500);
            } else {
                passwordMessage.innerText = result.message || 'Failed to update password';
                passwordMessage.className = 'error-text';
            }
        } catch (err) {
            console.error('Password change error:', err);
            passwordMessage.innerText = 'An error occurred. Please try again.';
            passwordMessage.className = 'error-text';
        }
    });
}