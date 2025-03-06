document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const inputArea = document.getElementById('input-area');
    const analysisSection = document.getElementById('analysis-section');
    const analysisContent = document.getElementById('analysis-content');
    const setupInterviewContainer = document.getElementById('setup-interview-container');
    const setupInterviewForm = document.getElementById('setup-interview');
    const startButton = document.getElementById('start-interview');
    let sessionAnswers = {};

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
    
            // Target the span that contains the question text
            const questionSpan = chatMessages.lastElementChild.previousElementSibling.querySelector('.message-content');
            const questionText = questionSpan.textContent;
    
            sessionAnswers[message] = { question: questionText, answer: message };
            console.log("sessionAnswers before submit:", sessionAnswers);
            userInput.value = '';
    
            fetch('/submit_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: questionText, answer: message })
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
        messageContent.classList.add('message-content'); // Add a class for easier targeting
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
        console.log("displayAnalysis called with analysis:", analysis);
        analysisSection.style.display = 'block';
        analysisContent.innerHTML = formatAnalysis(analysis);
    }

    function formatAnalysis(data) {
        let analysisHtml = '';
        data.forEach(item => {
            const question = item.question; // Get question from the analysis data
            analysisHtml += `<h3>Question: ${question}</h3>`;
            analysisHtml += `<p><strong>Answer:</strong> ${item.answer}</p>`;
            analysisHtml += `<p><strong>Sentiment:</strong> ${item.sentiment.compound.toFixed(2)}</p>`;

            analysisHtml += `<p><strong>Technical Keywords:</strong> ${item.keywords.technical.join(', ')}</p>`;
            analysisHtml += `<p><strong>Soft Skills Keywords:</strong> ${item.keywords.soft_skills.join(', ')}</p>`;
            analysisHtml += `<p><strong>Technical Context:</strong> ${item.keywords.technical_context.join('<br>')}</p>`;
            analysisHtml += `<p><strong>Soft Skills Context:</strong> ${item.keywords.soft_skills_context.join('<br>')}</p>`;

            analysisHtml += `<p><strong>Grammar Errors:</strong> ${item.grammar_errors.join('<br>')}</p>`;
            analysisHtml += `<p><strong>Sentence Feedback:</strong> ${item.sentence_structure_feedback.join('<br>')}</p>`;
        });

        console.log("Generated analysisHtml:", analysisHtml);
        return analysisHtml;
    }
});