// ========================================
// API CONFIGURATION
// ========================================
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api', // Change this to your Flask API URL
    ENDPOINTS: {
        ANALYZE_IMAGE: '/analyze-image',
        CHAT: '/chat',
        VOICE_TO_TEXT: '/voice-to-text',
        TEXT_TO_SPEECH: '/text-to-speech'
    }
};

// ========================================
// API HELPER FUNCTIONS
// ========================================

/**
 * Upload and analyze image
 * @param {Blob} imageBlob - Image file blob
 * @param {string} language - Current language code
 * @returns {Promise<Object>} Analysis result
 */
async function analyzeImage(imageBlob, language) {
    const formData = new FormData();
    formData.append('image', imageBlob, 'crop.jpg');
    formData.append('language', language);

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.ANALYZE_IMAGE}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Image analysis error:', error);
        throw error;
    }
}

/**
 * Send chat message to backend
 * @param {string} message - User message
 * @param {string} language - Current language code
 * @param {string} sessionId - Chat session ID (optional)
 * @returns {Promise<Object>} Chat response
 */
async function sendChatMessage(message, language, sessionId = null) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                language: language,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Chat API error:', error);
        throw error;
    }
}

/**
 * Convert voice/audio to text using backend
 * @param {Blob} audioBlob - Audio file blob
 * @param {string} language - Current language code
 * @returns {Promise<Object>} Transcription result
 */
async function convertVoiceToText(audioBlob, language) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.wav');
    formData.append('language', language);

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.VOICE_TO_TEXT}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Voice to text error:', error);
        throw error;
    }
}

/**
 * Get text-to-speech audio from backend
 * @param {string} text - Text to convert to speech
 * @param {string} language - Current language code
 * @returns {Promise<Blob>} Audio blob
 */
async function getTextToSpeech(text, language) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TEXT_TO_SPEECH}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                language: language
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const audioBlob = await response.blob();
        return audioBlob;
    } catch (error) {
        console.error('Text to speech error:', error);
        throw error;
    }
}

// ========================================
// TRANSLATION DATA
// ========================================
const translations = {
    en: {
        tagline: "I help you grow healthier crops.",
        "start-btn": "Let's Start",
        "language-btn": "Select Language",
        "select-language": "Select Language",
        "scan-title": "Capture Product",
        "capture-btn": "📷 Capture Photo",
        "upload-btn": "🖼️ Upload from Gallery",
        "chat-title": "Kisan Dost",
        "tap-to-speak": "Tap to speak",
        "welcome-msg": "Hello! I'm your Kisan Dost. How can I help you today?",
        "analyzing": "Analyzing your product...",
        "scan-complete": "I've identified your crop. What would you like to know about it?",
        "listening": "Listening...",
        "processing": "Processing your question...",
        "error": "Sorry, something went wrong. Please try again."
    },
    ur: {
        tagline: "میں آپ کی صحت مند فصلیں اُگانے میں مدد کرتا ہوں۔",
        "start-btn": "شروع کریں",
        "language-btn": "زبان منتخب کریں",
        "select-language": "زبان منتخب کریں",
        "scan-title": "مصنوعات کی تصویر",
        "capture-btn": "📷 تصویر لیں",
        "upload-btn": "🖼️ گیلری سے اپ لوڈ کریں",
        "chat-title": "کسان دوست",
        "tap-to-speak": "بولنے کے لیے ٹیپ کریں",
        "welcome-msg": "السلام علیکم! میں آپ کا کسان دوست ہوں۔ میں آپ کی کیسے مدد کر سکتا ہوں؟",
        "analyzing": "آپ کی مصنوعات کا تجزیہ کر رہے ہیں...",
        "scan-complete": "میں نے آپ کی فصل کی شناخت کر لی ہے۔ آپ اس کے بارے میں کیا جاننا چاہتے ہیں؟",
        "listening": "سن رہے ہیں...",
        "processing": "آپ کے سوال پر کام ہو رہا ہے...",
        "error": "معذرت، کچھ غلط ہو گیا۔ براہ کرم دوبارہ کوشش کریں۔"
    },
    sd: {
        tagline: "مان توهان جي صحتمند فصلن کي پوکڻ ۾ مدد ڪريان ٿو.",
        "start-btn": "شروع ڪريو",
        "language-btn": "ٻولي چونڊيو",
        "select-language": "ٻولي چونڊيو",
        "scan-title": "پراڊڪٽ جي تصوير",
        "capture-btn": "📷 تصوير وٺو",
        "upload-btn": "🖼️ گيلري مان اپ لوڊ ڪريو",
        "chat-title": "ڪسان دوست",
        "tap-to-speak": "ڳالهائڻ لاءِ ٽيپ ڪريو",
        "welcome-msg": "سلام! مان توهان جو ڪسان دوست آهيان. مان توهان جي ڪيئن مدد ڪري سگهان ٿو؟",
        "analyzing": "توهان جي پراڊڪٽ جو تجزيو ڪري رهيا آهيون...",
        "scan-complete": "مون توهان جي فصل جي سڃاڻپ ڪري ڇڏي آهي. توهان ان بابت ڇا ڄاڻڻ چاهيو ٿا؟",
        "listening": "ٻڌي رهيا آهيون...",
        "processing": "توهان جي سوال تي ڪم ڪري رهيا آهيون...",
        "error": "معاف ڪجو، ڪجهه غلط ٿي ويو. مهرباني ڪري ٻيهر ڪوشش ڪريو."
    }
};

// ========================================
// APP STATE MANAGEMENT
// ========================================
let currentPage = 'landing-page';
let currentLanguage = 'en';
let cameraStream = null;
let currentSpeech = null;
let recognition = null;
let isRecording = false;
let chatSessionId = null; // Store session ID for chat context

// ========================================
// SPEECH RECOGNITION
// ========================================
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = () => {
            isRecording = true;
            const micBtn = document.getElementById('mic-btn');
            const micText = micBtn.querySelector('.mic-text');
            micBtn.classList.add('recording');
            micText.textContent = translations[currentLanguage]['listening'];
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            handleVoiceInput(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            resetMicButton();
        };
        
        recognition.onend = () => {
            resetMicButton();
        };
    }
}

function resetMicButton() {
    isRecording = false;
    const micBtn = document.getElementById('mic-btn');
    const micText = micBtn.querySelector('.mic-text');
    micBtn.classList.remove('recording');
    micText.setAttribute('data-translate', 'tap-to-speak');
    micText.textContent = translations[currentLanguage]['tap-to-speak'];
}

// ========================================
// VOICE INPUT HANDLER WITH API INTEGRATION
// ========================================
async function handleVoiceInput(text) {
    if (text.trim()) {
        // Add user message to chat
        addMessage('user', text);
        
        // Show processing indicator
        const micText = document.querySelector('.mic-text');
        const originalText = micText.textContent;
        micText.textContent = translations[currentLanguage]['processing'];
        
        try {
            // Send message to backend API
            const response = await sendChatMessage(text, currentLanguage, chatSessionId);
            
            // Update session ID if provided
            if (response.session_id) {
                chatSessionId = response.session_id;
            }
            
            // Add bot response with speech
            if (response.response || response.message) {
                const botMessage = response.response || response.message;
                addMessage('bot', botMessage, true);
            }
            
        } catch (error) {
            console.error('Error processing voice input:', error);
            // Fallback response if API fails
            addMessage('bot', translations[currentLanguage]['error'], true);
        } finally {
            // Reset mic button text
            micText.textContent = translations[currentLanguage]['tap-to-speak'];
        }
    }
}

// ========================================
// TEXT-TO-SPEECH FUNCTIONALITY
// ========================================
function speakText(text, lang) {
    // Cancel any ongoing speech
    if (currentSpeech) {
        window.speechSynthesis.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);
    
    const langMap = {
        'en': 'en-US',
        'ur': 'ur-PK',
        'sd': 'en-IN'
    };
    
    utterance.lang = langMap[lang] || 'en-US';
    
    // Get available voices and try to match the language
    const voices = window.speechSynthesis.getVoices();
    const langCode = langMap[lang];
    
    let selectedVoice = voices.find(voice => voice.lang.startsWith(langCode.split('-')[0]));
    
    // For Urdu, try Hindi or Arabic as fallback
    if (lang === 'ur' && !selectedVoice) {
        selectedVoice = voices.find(voice => 
            voice.lang.startsWith('hi') || 
            voice.lang.startsWith('ar')
        );
    }
    
    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }
    
    utterance.rate = 0.85;
    utterance.pitch = 1;
    utterance.volume = 1;

    currentSpeech = utterance;
    window.speechSynthesis.speak(utterance);

    return utterance;
}

// Alternative: Use backend TTS (uncomment if you want to use backend TTS instead)
/*
async function speakTextFromBackend(text, lang) {
    try {
        const audioBlob = await getTextToSpeech(text, lang);
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
        
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
        };
        
        return audio;
    } catch (error) {
        console.error('Backend TTS error:', error);
        // Fallback to browser TTS
        return speakText(text, lang);
    }
}
*/

// Load voices
if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = () => {
        // Voices loaded
    };
}

// ========================================
// PAGE NAVIGATION
// ========================================
function navigateTo(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    currentPage = pageId;

    // Initialize camera when navigating to scan page
    if (pageId === 'scan-page') {
        initCamera();
    } else if (cameraStream) {
        stopCamera();
    }
}

// ========================================
// LANGUAGE MANAGEMENT
// ========================================
function setLanguage(lang) {
    currentLanguage = lang;
    
    // Set language-specific recognition
    if (recognition) {
        const langMap = {
            'en': 'en-US',
            'ur': 'ur-PK',
            'sd': 'sd-PK'
        };
        recognition.lang = langMap[lang] || 'en-US';
    }
    
    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(elem => {
        const key = elem.getAttribute('data-translate');
        if (translations[lang][key]) {
            elem.textContent = translations[lang][key];
        }
    });
    
    // Add RTL class for Urdu/Sindhi
    document.querySelectorAll('.language-option, .message-bubble').forEach(elem => {
        if (lang === 'ur' || lang === 'sd') {
            elem.classList.add('rtl-text');
        } else {
            elem.classList.remove('rtl-text');
        }
    });
}

// ========================================
// CAMERA MANAGEMENT
// ========================================
async function initCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } 
        });
        const video = document.getElementById('camera-feed');
        video.srcObject = stream;
        cameraStream = stream;
    } catch (error) {
        console.error('Camera access error:', error);
        alert('Unable to access camera. Please check permissions.');
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
}

// ========================================
// CHAT MANAGEMENT
// ========================================
function clearChatHistory() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML = '';
    chatSessionId = null; // Reset session
    
    if (currentSpeech) {
        window.speechSynthesis.cancel();
    }
}

// ========================================
// IMAGE CAPTURE AND PROCESSING WITH API
// ========================================
function capturePhoto() {
    const video = document.getElementById('camera-feed');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Convert to blob
    canvas.toBlob(blob => {
        processImage(blob);
    }, 'image/jpeg', 0.9);
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
        processImage(file);
    }
}

async function processImage(imageBlob) {
    const loader = document.getElementById('loader');
    const scanPage = document.getElementById('scan-page');
    
    // Hide buttons, show loader
    scanPage.querySelector('.action-buttons').style.display = 'none';
    loader.classList.add('active');
    
    try {
        // Send image to backend API for analysis
        const analysisResult = await analyzeImage(imageBlob, currentLanguage);
        
        // Hide loader, show buttons
        loader.classList.remove('active');
        scanPage.querySelector('.action-buttons').style.display = 'flex';
        stopCamera();
        navigateTo('chat-page');
        
        // Add initial bot message with analysis result
        const message = analysisResult.message || analysisResult.response || translations[currentLanguage]['scan-complete'];
        
        // Store session ID if provided
        if (analysisResult.session_id) {
            chatSessionId = analysisResult.session_id;
        }
        
        addMessage('bot', message, true);
        
    } catch (error) {
        console.error('Image processing error:', error);
        
        // Hide loader, show buttons
        loader.classList.remove('active');
        scanPage.querySelector('.action-buttons').style.display = 'flex';
        
        // Show error message
        alert(translations[currentLanguage]['error']);
    }
}

// ========================================
// CHAT MESSAGE DISPLAY
// ========================================
function addMessage(type, text, enableSpeech = false) {
    const chatWindow = document.getElementById('chat-window');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    
    // Add RTL class if needed
    if (currentLanguage === 'ur' || currentLanguage === 'sd') {
        bubbleDiv.classList.add('rtl-text');
    }
    
    bubbleDiv.textContent = text;
    
    // Add speaker icon for bot messages
    if (type === 'bot') {
        const speakerIcon = document.createElement('span');
        speakerIcon.className = 'speaker-icon';
        speakerIcon.textContent = '🔊';
        speakerIcon.title = 'Click to hear message';
        
        speakerIcon.addEventListener('click', function() {
            speakerIcon.classList.add('speaking');
            const utterance = speakText(text, currentLanguage);
            
            utterance.onend = () => {
                speakerIcon.classList.remove('speaking');
            };
        });
        
        bubbleDiv.appendChild(speakerIcon);
        
        // Auto-play speech if enabled
        if (enableSpeech) {
            setTimeout(() => {
                speakerIcon.classList.add('speaking');
                const utterance = speakText(text, currentLanguage);
                utterance.onend = () => {
                    speakerIcon.classList.remove('speaking');
                };
            }, 300);
        }
    }
    
    messageDiv.appendChild(bubbleDiv);
    chatWindow.appendChild(messageDiv);
    
    // Scroll to bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ========================================
// EVENT LISTENERS
// ========================================
document.getElementById('start-btn').addEventListener('click', () => {
    navigateTo('scan-page');
});

document.getElementById('language-btn').addEventListener('click', () => {
    navigateTo('language-page');
});

document.getElementById('lang-back-btn').addEventListener('click', () => {
    navigateTo('landing-page');
});

document.getElementById('scan-back-btn').addEventListener('click', () => {
    navigateTo('landing-page');
});

document.getElementById('chat-back-btn').addEventListener('click', () => {
    clearChatHistory();
    navigateTo('scan-page');
});

// Language selection
document.querySelectorAll('.language-option').forEach(option => {
    option.addEventListener('click', (e) => {
        const lang = e.target.getAttribute('data-lang');
        setLanguage(lang);
        navigateTo('landing-page');
    });
});

// Capture photo button
document.getElementById('capture-photo-btn').addEventListener('click', capturePhoto);

// Upload photo button
document.getElementById('upload-photo-btn').addEventListener('click', () => {
    document.getElementById('file-input').click();
});

// File input change
document.getElementById('file-input').addEventListener('change', handleFileUpload);

// Microphone button for voice input
document.getElementById('mic-btn').addEventListener('click', () => {
    if (!recognition) {
        alert('Speech recognition is not supported in your browser. Please use Chrome, Edge etc')
    }
});