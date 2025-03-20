document.addEventListener('DOMContentLoaded', function() {
    const pageId = document.body.id;

    if (pageId === 'setup-page') {
        // --- Setup Page Logic ---
        const setupInterviewForm = document.getElementById('setup-interview');
        const startButton = document.getElementById('start-interview');
        const webcamVideo = document.getElementById('webcam-video');

        if (startButton) {
            startButton.addEventListener('click', function(event) {
                event.preventDefault();
                setupInterview();
            });
        }

        function setupInterview() {
            const formData = new FormData(setupInterviewForm);
            fetch('/start_interview_config', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            })
            .catch(error => {
                console.error('Error setting up interview:', error);
                alert('An error occurred during interview setup.');
            });
        }

        async function initializeWebcam(){
            try {
                const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
                webcamVideo.srcObject = videoStream;
            } catch (error) {
                console.error('Error accessing webcam:', error);
                alert('Unable to access webcam.');
            }
        }
        initializeWebcam();

    } else if (pageId === 'interview-page') {
        // --- Interview Page Logic ---
        const chatMessages = document.querySelector('.chat-messages');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');
        const inputArea = document.getElementById('input-area');
        const webcamVideo = document.getElementById('webcam-video');
        let currentQuestion = null;
        let mediaRecorder;
        let recordedChunks = [];
        let videoStream;
        let eyeContactPercentages = [];

        getQuestion();

        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });

        async function initializeWebcam(){
            try {
                videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
                webcamVideo.srcObject = videoStream;
            } catch (error) {
                console.error('Error accessing webcam:', error);
                alert('Unable to access webcam.');
            }
        }
        initializeWebcam();

        function getQuestion() {
            fetch('/ask_question')
                .then(response => response.json())
                .then(data => {
                    if (data.status === "redirect") {
                        if (data.redirect_url && typeof data.redirect_url === 'string') {
                            window.location.assign(data.redirect_url);
                        } else {
                            console.error("Invalid redirect URL:", data.redirect_url);
                        }
                    } else if (data.question) {
                        currentQuestion = data.question;
                        appendMessage('bot-message', data.question);
                    } else if (data.status === 'finished') {
                        inputArea.style.display = 'none';
                        window.location.href = data.redirect_url;
                    } else if (data.error) {
                        alert(data.error);
                    } else {
                        alert("An unexpected error occurred.");
                    }
                })
                .catch(error => {
                    console.error('Error getting question:', error);
                    alert('An error occurred while getting the question.');
                });
        }

        function sendMessage() {
            const message = userInput.value.trim();
            if (message) {
                appendMessage('user-message', message);
                let videoPromise = Promise.resolve();
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    videoPromise = new Promise(resolve => {
                        mediaRecorder.onstop = () => {
                            const blob = new Blob(recordedChunks, { type: 'video/webm' });
                            recordedChunks = [];
                            sendVideoToServer(blob).then(() => resolve());
                            if (videoStream) {
                                videoStream.getTracks().forEach(track => track.stop());
                                videoStream = null;
                            }
                        };
                    });
                } else if (videoStream) {
                    videoStream.getTracks().forEach(track => track.stop());
                    videoStream = null;
                }
                if (videoStream) {
                    videoStream.getTracks().forEach(track => track.stop());
                    videoStream = null;
                    webcamVideo.srcObject = null;
                }
                videoPromise.then(() => {
                    fetch('/submit_answer', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            question: currentQuestion,
                            answer: message,
                            eye_contact_percentages: eyeContactPercentages
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            getQuestion();
                        } else if (data.status === 'redirect') {
                            window.location.assign(data.redirect_url);
                        } else if (data.error) {
                            alert(data.error);
                        } else {
                            alert("An unexpected error occurred.");
                        }
                    })
                    .catch(error => {
                        console.error('Error submitting answer:', error);
                        alert('An error occurred while submitting your answer.');
                    });
                });
                userInput.value = '';
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

        let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            const speechButton = document.getElementById('speech-button');
            let speechActive = false;

            speechButton.addEventListener('click', async () => {
                if (!speechActive) {
                    try {
                        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
                        mediaRecorder = new MediaRecorder(videoStream);
                        mediaRecorder.ondataavailable = event => {
                            if (event.data.size > 0) {
                                recordedChunks.push(event.data);
                            }
                        };
                        mediaRecorder.start();
                        speechActive = true;
                        speechButton.classList.add('active');
                        recognition.start();
                        webcamVideo.srcObject = videoStream;
                    } catch (error) {
                        console.error('Error accessing webcam:', error);
                        alert('Unable to access webcam.');
                    }
                } else {
                    speechActive = false;
                    speechButton.classList.remove('active');
                    recognition.stop();
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


    function sendVideoToServer(blob) {
        return new Promise((resolve, reject) => {
            const formData = new FormData();
            formData.append('video', blob, 'recording.webm');
            fetch('/process_video', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                eyeContactPercentages.push(data.eye_contact_percentage);
                console.log("Eye contact percentages:", eyeContactPercentages);
                resolve(); // Resolve the promise when video processing is complete
            })
            .catch(error => {
                console.error('Error sending video:', error);
                reject(error); // Reject the promise on error
            });
        });
    }
}
});