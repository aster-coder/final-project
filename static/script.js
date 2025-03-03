document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const inputArea = document.getElementById('input-area');
    const analysisSection = document.getElementById('analysis-section');
    const analysisContent = document.getElementById('analysis-content');
    const setupInterviewContainer = document.getElementById('setup-interview-container'); // Corrected ID
    const setupInterviewForm = document.getElementById('setup-interview'); // Corrected ID
    const startButton = document.getElementById('start-interview'); // Corrected ID

    startButton.addEventListener('click', setupInterview);

    function setupInterview() {
        const formData = new FormData(setupInterviewForm); // Corrected ID
        for (let pair of formData.entries()) {
            console.log(pair[0] + ', ' + pair[1]);
        }
        fetch('/setup_interview', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                setupInterviewContainer.style.display = 'none'; // Corrected ID
                inputArea.style.display = 'flex';
                getQuestion();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error setting up interview:', error);
            alert('An error occurred during interview setup.');
        });
    }

    function getQuestion() {
        fetch('/get_question')
            .then(response => response.json())
            .then(data => {
                if (data.question) {
                    appendMessage('bot-message', data.question);
                } else if (data.status === 'finished') {
                    getAnalysis();
                    inputArea.style.display = 'none';
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

    function getAnalysis() {
        fetch('/get_analysis')
            .then(response => response.json())
            .then(data => {
                if (data && Object.keys(data).length > 0) {
                    analysisSection.style.display = 'block';
                    analysisContent.innerHTML = formatAnalysis(data);
                } else {
                    alert('No analysis data available.');
                }
            })
            .catch(error => {
                console.error('Error getting analysis:', error);
                alert('An error occurred while getting the analysis.');
            });
    }

    function formatAnalysis(data) {
        let analysisHtml = '';
        for (const question in data) {
            if (question.endsWith('_analysis')) {
                const questionBase = question.replace('_analysis', '');
                const analysis = data[question];
                const answer = data[questionBase];

                analysisHtml += `<h3>Question: ${questionBase}</h3>`;
                analysisHtml += `<p><strong>Answer:</strong> ${answer}</p>`;
                analysisHtml += `<p><strong>Matched Keywords:</strong> ${analysis.matched_keywords ? analysis.matched_keywords.join(', ') : 'None'}</p>`;
                analysisHtml += `<p><strong>Keyword Match Score:</strong> ${analysis.keyword_match_score}</p>`;
                analysisHtml += `<p><strong>Sentiment:</strong> Positive: ${analysis.sentiment.pos.toFixed(2)}, Negative: ${analysis.sentiment.neg.toFixed(2)}, Neutral: ${analysis.sentiment.neu.toFixed(2)}, Compound: ${analysis.sentiment.compound.toFixed(2)}</p>`;
                analysisHtml += `<p><strong>Answer Length:</strong> ${analysis.answer_length} words</p>`;
                analysisHtml += "<p><strong>Advice:</strong></p>";
                let adviceGiven = false;

                if (analysis.keyword_match_score < 0.5) {
                    analysisHtml += `<p>  - Your answer to '${questionBase}' could include more relevant keywords.</p>`;
                    adviceGiven = true;
                }

                if (analysis.sentiment.compound < -0.2) {
                    analysisHtml += `<p>  - Your answer to '${questionBase}' had a somewhat negative tone.</p>`;
                    adviceGiven = true;
                }

                if (analysis.answer_length < 20) {
                    analysisHtml += `<p>  - Your answer to '${questionBase}' was quite short.</p>`;
                    adviceGiven = true;
                }

                if (!adviceGiven) {
                    analysisHtml += "<p>  - Your answer looks good!</p>";
                }
            }
        }
        return analysisHtml;
    }
});