document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const inputArea = document.getElementById('input-area');
    const setupInterviewContainer = document.getElementById('setup-interview-container');
    const setupInterviewForm = document.getElementById('setup-interview');
    const startButton = document.getElementById('start-interview');
    let currentQuestion = null; // Store the current question

    startButton.addEventListener('click', setupInterview);

    function setupInterview() {
        const formData = new FormData(setupInterviewForm);
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(() => {
            setupInterviewContainer.style.display = 'none';
            inputArea.style.display = 'flex';
            appendMessage('bot-message', 'Welcome to your interview!');
            getQuestion();
        })
        .catch(error => {
            console.error('Error setting up interview:', error);
            alert('An error occurred during interview setup.');
        });
    }

    function getQuestion() {
        fetch('/ask_question')
            .then(response => response.json())
            .then(data => {
                console.log("Data received from server:", data);
                if (data.status === "redirect") {
                    window.location.href = data.redirect_url; // Redirect to dashboard
                } else if (data.question) {
                    currentQuestion = data.question; // Store the question
                    appendMessage('bot-message', data.question);
                } else if (data.status === 'finished') {
                    inputArea.style.display = 'none';
                    console.log("Interview finished.");
                    window.location.href = data.redirect_url; // Redirect to dashboard if finished.
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error getting question:', error);
                alert('An error occurred while getting the question.');
            });
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            appendMessage('user-message', message);
            fetch('/submit_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: currentQuestion, // Use the stored question
                    answer: message
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    getQuestion();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error submitting answer:', error);
                alert('An error occurred while submitting your answer.');
            });
            userInput.value = ''; // Clear the input after sending
        }
    }

    function appendMessage(className, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', className);

        const messageContent = document.createElement('span');
        messageContent.classList.add('message-content');
        messageContent.textContent = message;

        const timestamp = document.createElement('span');
        timestamp.classList.add('timestamp');
        timestamp.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Speech recognition functionality
    let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        const speechButton = document.getElementById('speech-button');
        let speechActive = false;

        speechButton.addEventListener('click', () => {
            if (speechActive) {
                recognition.stop();
                speechActive = false;
                speechButton.classList.remove('active');
            } else {
                recognition.start();
                speechActive = true;
                speechButton.classList.add('active');
            }
        });

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript + ' ';
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            userInput.value = (userInput.value + ' ' + finalTranscript).trim() || (userInput.value + interimTranscript).trim();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            alert('Speech recognition error. Please try again.');
            speechActive = false;
            speechButton.classList.remove('active');
        };
    } else {
        console.error('Speech recognition is not supported in this browser.');
        alert('Speech recognition is not supported in your browser.');
        document.getElementById('speech-button').style.display = 'none';
    }
});