document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const inputArea = document.getElementById('input-area');
    const analysisSection = document.getElementById('analysis-section'); //correct line
    const analysisContent = document.getElementById('analysis-content');
    const setupInterviewContainer = document.getElementById('setup-interview-container');
    const setupInterviewForm = document.getElementById('setup-interview');
    const startButton = document.getElementById('start-interview');
    let sessionAnswers = {}; // Added to store session answers

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
                console.log("Data received from server:", data); //added log
                if (data.question) {
                    appendMessage('bot-message', data.question);
                } else if (data.status === 'finished') {
                    inputArea.style.display = 'none';
                    console.log("Analysis data received:", data.analysis);
                    displayAnalysis(data.analysis);
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
            sessionAnswers[chatMessages.lastElementChild.textContent] = message;
            console.log("sessionAnswers before submit:", sessionAnswers); //added console log
            userInput.value = '';
    
            fetch('/submit_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: chatMessages.lastElementChild.textContent, answer: message })
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
        }
    }

    function appendMessage(className, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', className);

        const messageContent = document.createElement('span');
        messageContent.textContent = message;

        const timestamp = document.createElement('span');
        timestamp.classList.add('timestamp');
        timestamp.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function displayAnalysis(analysis) {
        console.log("displayAnalysis called with analysis:", analysis); // added console log
        analysisSection.style.display = 'block';
        analysisContent.innerHTML = formatAnalysis(analysis);
    }
    
    function formatAnalysis(data) {
        let analysisHtml = '';
        data.forEach(item => { // Iterate through the list
            analysisHtml += `<h3>Question: ${item.question}</h3>`;
            analysisHtml += `<p><strong>Answer:</strong> ${item.answer}</p>`;
            analysisHtml += `<p><strong>Sentiment:</strong> ${item.sentiment.compound.toFixed(2)}</p>`;
        });
        
        console.log("Generated analysisHtml:", analysisHtml); //added console log
        return analysisHtml;
    }
});