document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const removeImage = document.getElementById('removeImage');
    const clearChat = document.querySelector('.clear-chat');
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const sampleQuestions = document.querySelectorAll('.sample-question');
    
    // Variables
    let selectedImage = null;
    
    // Plant database
    const plantDatabase = {
        "tomato": {
            "watering": "Regular watering, keeping soil consistently moist",
            "sunlight": "Full sun, at least 6-8 hours daily",
            "soil": "Well-draining, slightly acidic soil rich in organic matter",
            "pests": "Watch for aphids, hornworms, and whiteflies"
        },
        "rose": {
            "watering": "Deep watering once a week, avoid wetting the leaves",
            "sunlight": "At least 6 hours of direct sunlight daily",
            "soil": "Well-draining, loamy soil with organic matter",
            "pests": "Watch for aphids, Japanese beetles, and black spot"
        },
        "basil": {
            "watering": "Keep soil consistently moist but not waterlogged",
            "sunlight": "Full sun to partial shade",
            "soil": "Rich, well-draining soil",
            "pests": "Watch for aphids, Japanese beetles, and slugs"
        },
        "succulent": {
            "watering": "Allow soil to dry completely between waterings",
            "sunlight": "Bright, indirect light or morning sun",
            "soil": "Fast-draining cactus or succulent mix",
            "pests": "Watch for mealybugs and scale insects"
        }
    };
    
    // Event Listeners
    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });
    
    imageUpload.addEventListener('change', handleImageUpload);
    removeImage.addEventListener('click', clearImagePreview);
    clearChat.addEventListener('click', clearChatHistory);
    menuToggle.addEventListener('click', toggleSidebar);
    
    // Sample questions
    sampleQuestions.forEach(question => {
        question.addEventListener('click', function() {
            userInput.value = this.textContent;
            handleSendMessage();
        });
    });
    
    // Functions
    async function handleSendMessage() {
        const message = userInput.value.trim();
        
        if (message === '' && !selectedImage) return;
        
        // Add user message to chat
        addUserMessage(message, selectedImage);
        
        // Clear input
        userInput.value = '';
        
        // Show loading indicator
        showLoading();
        
        try {
            let response;
            
            // Use FormData for file uploads
            if (selectedImage) {
                // Create form data
                const formData = new FormData();
                formData.append('user_id', 'user123');
                formData.append('query', message || '');
                
                // Get the file from the input
                const fileInput = document.getElementById('imageUpload');
                if (fileInput.files.length > 0) {
                    formData.append('image', fileInput.files[0]);
                } else {
                    throw new Error('No image file selected');
                }
                
                console.log('Sending image request with FormData');
                
                // Send as multipart/form-data
                response = await fetch('http://localhost:8000/chat/with_image', {
                    method: 'POST',
                    body: formData
                });
            } else {
                // Regular JSON for text-only
                const requestBody = {
                    user_id: 'user123',
                    query: message
                };
                
                console.log('Sending text request:', JSON.stringify(requestBody, null, 2));
                
                response = await fetch('http://localhost:8000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });
            }
            
            const responseData = await response.json();
            
            if (!response.ok) {
                console.error('Error response:', responseData);
                throw new Error(responseData.detail || 'Network response was not ok');
            }
            
            // Remove loading indicator
            removeLoading();
            
            // Add bot response to chat
            addBotMessage(responseData.response);
            
            // Clear image preview
            clearImagePreview();
        } catch (error) {
            console.error('Error:', error);
            removeLoading();
            // Handle different types of errors
            if (error.message.includes('Validation error')) {
                addBotMessage(`Error: ${error.message}`);
            } else if (error.message.includes('Unprocessable Entity')) {
                addBotMessage("Sorry, there was a problem with the request format. Please try again.");
            } else {
                addBotMessage(`Sorry, I encountered an error: ${error.message}`);
            }
        }
    }
    
    function handleImageUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        if (!file.type.match('image.*')) {
            alert('Please select an image file');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            selectedImage = e.target.result;
            imagePreview.style.backgroundImage = `url(${selectedImage})`;
            imagePreviewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
    
    function clearImagePreview() {
        selectedImage = null;
        imagePreview.style.backgroundImage = '';
        imagePreviewContainer.style.display = 'none';
        imageUpload.value = '';
    }
    
    function addUserMessage(message, image) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        
        let content = `<div class="message-content">`;
        
        if (message) {
            content += `<p>${message}</p>`;
        } else if (image) {
            content += `<p>I'd like to identify this plant.</p>`;
        }
        
        if (image) {
            content += `<img src="${image}" class="message-image" alt="User uploaded image">`;
        }
        
        content += `</div>`;
        messageDiv.innerHTML = content;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        
        // Convert markdown-like syntax to HTML
        message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        message = message.replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${message}</p>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.innerHTML = `
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        `;
        loadingDiv.id = 'loadingIndicator';
        chatMessages.appendChild(loadingDiv);
        scrollToBottom();
    }
    
    function removeLoading() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function clearChatHistory() {
        // Keep only the welcome message
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        clearImagePreview();
    }
    
    function toggleSidebar() {
        sidebar.classList.toggle('active');
    }
    
    // Mock function to analyze plant images
    function analyzePlantImage(image) {
        // In a real app, this would call an API or ML model
        // For demo, randomly "identify" the plant
        const plants = ["tomato", "rose", "basil", "succulent"];
        const identifiedPlant = plants[Math.floor(Math.random() * plants.length)];
        
        const confidence = (Math.random() * (0.98 - 0.7) + 0.7).toFixed(2);
        return { plant: identifiedPlant, confidence: confidence };
    }
    
    // Generate response based on user input
    function generateResponse(query, image) {
        // If an image was uploaded, analyze it
        if (image) {
            const { plant, confidence } = analyzePlantImage(image);
            
            // Format confidence as percentage
            const confidencePct = `${(confidence * 100).toFixed(1)}%`;
            
            const plantInfo = plantDatabase[plant];
            
            let response = `I've identified this as a **${plant.charAt(0).toUpperCase() + plant.slice(1)}** (confidence: ${confidencePct}).\n\n`;
            
            if (plantInfo) {
                response += `**Care tips for ${plant.charAt(0).toUpperCase() + plant.slice(1)}:**\n`;
                response += `- **Watering**: ${plantInfo.watering}\n`;
                response += `- **Sunlight**: ${plantInfo.sunlight}\n`;
                response += `- **Soil**: ${plantInfo.soil}\n`;
                response += `- **Common pests**: ${plantInfo.pests}`;
            }
            
            return response;
        }
        
        // Process text query
        if (!query) return "I'm not sure what you're asking. Could you provide more details?";
        
        const queryLower = query.toLowerCase();
        
        // Check for greetings
        if (/\b(hello|hi|hey|greetings)\b/.test(queryLower)) {
            return "Hello! I'm your Garden Assistant. How can I help with your garden today?";
        }
        
        // Check for plant care questions
        for (const plant in plantDatabase) {
            if (queryLower.includes(plant)) {
                if (queryLower.includes("water")) {
                    return `For ${plant}: ${plantDatabase[plant].watering}`;
                } else if (/\b(sun|light|sunlight)\b/.test(queryLower)) {
                    return `For ${plant}: ${plantDatabase[plant].sunlight}`;
                } else if (queryLower.includes("soil")) {
                    return `For ${plant}: ${plantDatabase[plant].soil}`;
                } else if (/\b(pest|bug|insect)\b/.test(queryLower)) {
                    return `For ${plant}: ${plantDatabase[plant].pests}`;
                } else {
                    const plantInfo = plantDatabase[plant];
                    let response = `**${plant.charAt(0).toUpperCase() + plant.slice(1)} Care Guide:**\n`;
                    response += `- **Watering**: ${plantInfo.watering}\n`;
                    response += `- **Sunlight**: ${plantInfo.sunlight}\n`;
                    response += `- **Soil**: ${plantInfo.soil}\n`;
                    response += `- **Common pests**: ${plantInfo.pests}`;
                    return response;
                }
            }
        }
        
        // General gardening questions
        if (queryLower.includes("plant") && queryLower.includes("indoor")) {
            return "Great indoor plants for beginners include pothos, snake plants, and ZZ plants. They're low-maintenance and can thrive in various light conditions.";
        }
        
        if (queryLower.includes("compost")) {
            return "Composting is great for your garden! Mix green materials (vegetable scraps, grass clippings) with brown materials (dried leaves, paper) in roughly equal amounts. Turn your compost pile regularly and keep it slightly moist.";
        }
        
        if (queryLower.includes("fertilize") || queryLower.includes("fertilizer")) {
            return "Most plants benefit from fertilizing during their growing season. Use a balanced fertilizer (like 10-10-10) for general purposes, or choose specialized formulations for flowering or fruiting plants.";
        }
        
        // Default response
        return "I'm not sure about that. Could you ask about specific plants like tomatoes, roses, basil, or succulents? Or upload a plant image for identification.";
    }
});