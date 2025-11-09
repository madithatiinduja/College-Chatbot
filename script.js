// Cllg Chatbot - Frontend JavaScript
class CllgChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearChatBtn = document.getElementById('clearChat');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.quickActions = document.getElementById('quickActions');
        
        this.chatHistory = [];
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.displayWelcomeMessage();
        this.loadChatHistory();
    }
    
    setupEventListeners() {
        // Send message on button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Clear chat
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        
        // Quick action buttons
        this.quickActions.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-btn')) {
                const query = e.target.getAttribute('data-query');
                this.messageInput.value = query;
                this.sendMessage();
            }
        });
        
        // Input focus for better UX
        this.messageInput.addEventListener('focus', () => {
            this.messageInput.parentElement.style.borderColor = '#667eea';
        });
        
        this.messageInput.addEventListener('blur', () => {
            this.messageInput.parentElement.style.borderColor = '#e2e8f0';
        });
    }
    
    displayWelcomeMessage() {
        const welcomeMessage = {
            type: 'bot',
            content: `Hello! I'm your AI college assistant. I'm here to help you 24/7 with any questions about college life, academics, campus services, and more. How can I assist you today?`,
            timestamp: new Date()
        };
        
        this.addMessageToChat(welcomeMessage);
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Add user message to chat
        const userMessage = {
            type: 'user',
            content: message,
            timestamp: new Date()
        };
        
        this.addMessageToChat(userMessage);
        this.messageInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await this.sendToBackend(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response to chat
            const botMessage = {
                type: 'bot',
                content: response.reply,
                timestamp: new Date()
            };
            
            this.addMessageToChat(botMessage);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            
            // Show error message
            const errorMessage = {
                type: 'bot',
                content: 'I apologize, but I\'m experiencing some technical difficulties right now. Please try again in a moment.',
                timestamp: new Date()
            };
            
            this.addMessageToChat(errorMessage);
        }
    }
    
    async sendToBackend(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            // Fallback to local AI logic if backend is unavailable
            console.log('Backend unavailable, using local AI logic');
            return this.getLocalAIResponse(message);
        }
    }
    
    getLocalAIResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Admission requirements
        if (lowerMessage.includes('admission') || lowerMessage.includes('requirements') || lowerMessage.includes('apply')) {
            return {
                reply: `Here are the general admission requirements for our college:

• High school diploma or equivalent (GED)
• Completed application form with $50 application fee
• Official high school transcripts
• SAT or ACT scores (recommended)
• Personal statement or essay
• Letters of recommendation (2 required)
• Application deadline: March 1st for Fall semester

For specific programs, additional requirements may apply. Would you like me to provide details about a particular major or program?`
            };
        }
        
        // Available courses
        if (lowerMessage.includes('course') || lowerMessage.includes('class') || lowerMessage.includes('major')) {
            return {
                reply: `We offer a wide range of courses across various disciplines:

**Arts & Humanities:**
• English Literature, Creative Writing, History, Philosophy, Art History

**Business & Economics:**
• Business Administration, Marketing, Finance, Economics, Entrepreneurship

**Science & Technology:**
• Computer Science, Biology, Chemistry, Physics, Mathematics, Engineering

**Social Sciences:**
• Psychology, Sociology, Political Science, Anthropology, Education

**Health Sciences:**
• Nursing, Public Health, Nutrition, Exercise Science

Each major has specific course requirements and electives. What field interests you most?`
            };
        }
        
        // Financial aid
        if (lowerMessage.includes('financial') || lowerMessage.includes('aid') || lowerMessage.includes('scholarship') || lowerMessage.includes('cost')) {
            return {
                reply: `We're committed to making education affordable! Here's information about financial aid:

**Tuition & Fees:**
• Full-time tuition: $12,500 per semester
• Room & board: $8,000 per semester
• Books & supplies: ~$1,200 per semester

**Financial Aid Options:**
• Federal Pell Grants (up to $6,895/year)
• Federal Direct Loans
• Work-study programs
• Institutional scholarships
• State grants

**Application Process:**
1. Complete FAFSA (Free Application for Federal Student Aid)
2. Submit by March 1st priority deadline
3. Review your financial aid package
4. Accept/decline offers

Our financial aid office can help you explore all options. Would you like me to connect you with them?`
            };
        }
        
        // Library hours
        if (lowerMessage.includes('library') || lowerMessage.includes('hours') || lowerMessage.includes('study')) {
            return {
                reply: `Our library is a great place to study! Here are the current hours:

**Main Library Hours:**
• Monday-Thursday: 7:00 AM - 11:00 PM
• Friday: 7:00 AM - 8:00 PM
• Saturday: 9:00 AM - 6:00 PM
• Sunday: 12:00 PM - 11:00 PM

**Special Collections:**
• Rare Books Room: By appointment only
• Media Center: Same as main library
• Study Rooms: Available for 2-hour reservations

**Extended Hours During Finals:**
• Open 24/7 during final exam week
• Coffee cart available in evenings

The library also offers online resources accessible 24/7 from anywhere!`
            };
        }
        
        // Campus services
        if (lowerMessage.includes('campus') || lowerMessage.includes('service') || lowerMessage.includes('facility')) {
            return {
                reply: `We have many campus services to support your success:

**Academic Support:**
• Writing Center (Mon-Fri, 9 AM-5 PM)
• Math Lab (Mon-Thu, 10 AM-8 PM)
• Tutoring Services (by appointment)
• Academic Advising

**Health & Wellness:**
• Student Health Center (Mon-Fri, 8 AM-5 PM)
• Counseling Services (confidential, free)
• Fitness Center (6 AM-11 PM daily)
• Recreation Center

**Student Life:**
• Student Union (7 AM-12 AM daily)
• Career Services (Mon-Fri, 9 AM-5 PM)
• International Student Office
• Disability Services

**Technology:**
• IT Help Desk (24/7 support)
• Computer Labs (various locations)
• WiFi throughout campus

What specific service are you looking for?`
            };
        }
        
        // Student life
        if (lowerMessage.includes('student life') || lowerMessage.includes('club') || lowerMessage.includes('activity') || lowerMessage.includes('event')) {
            return {
                reply: `Campus life is vibrant and engaging! Here's what's happening:

**Student Organizations (100+ clubs):**
• Academic clubs (Math Club, Science Society)
• Cultural organizations (International Student Association)
• Service groups (Community Service Club)
• Special interest (Photography Club, Gaming Club)

**Campus Events:**
• Welcome Week (August)
• Homecoming (October)
• Spring Festival (April)
• Cultural celebrations throughout the year

**Recreation:**
• Intramural sports
• Outdoor adventure trips
• Fitness classes
• Movie nights

**Leadership Opportunities:**
• Student Government
• Resident Assistant positions
• Peer mentoring programs

Getting involved is a great way to make friends and build your resume!`
            };
        }
        
        // Technical support
        if (lowerMessage.includes('technical') || lowerMessage.includes('computer') || lowerMessage.includes('software') || lowerMessage.includes('wifi')) {
            return {
                reply: `Need tech help? We've got you covered:

**IT Support Services:**
• 24/7 Help Desk: (555) 123-4567
• Email: helpdesk@college.edu
• Live chat available on our website

**Common Issues & Solutions:**
• WiFi: Connect to "College_Network" with your student ID
• Email: Use your college email (username@college.edu)
• Software: Free access to Microsoft Office, Adobe Creative Suite
• Printing: 100 free pages per semester

**Computer Labs:**
• Main Library: 50+ computers
• Science Building: Specialized software
• Business School: Financial modeling tools

**Device Support:**
• Laptop/desktop troubleshooting
• Mobile device setup
• Software installation help

What specific tech issue are you experiencing?`
            };
        }
        
        // Academic calendar
        if (lowerMessage.includes('calendar') || lowerMessage.includes('deadline') || lowerMessage.includes('exam') || lowerMessage.includes('break')) {
            return {
                reply: `Here are the key dates for this academic year:

**Fall Semester 2024:**
• Classes begin: August 26
• Labor Day (no classes): September 2
• Fall Break: October 14-15
• Thanksgiving Break: November 27-29
• Finals Week: December 16-20
• Semester ends: December 20

**Spring Semester 2025:**
• Classes begin: January 13
• Martin Luther King Day (no classes): January 20
• Spring Break: March 10-14
• Easter Break: April 18-20
• Finals Week: May 5-9
• Commencement: May 10

**Important Deadlines:**
• Add/Drop period: First 2 weeks of classes
• Withdrawal deadline: 75% of semester completed
• Graduation application: March 1st

Need specific dates for your program?`
            };
        }
        
        // Default response
        return {
            reply: `Thank you for your question! I'm here to help with college-related inquiries. 

I can assist with:
• Admission requirements and applications
• Course information and academic programs
• Financial aid and scholarships
• Campus services and facilities
• Student life and activities
• Technical support
• Academic calendar and deadlines

Could you please rephrase your question or ask about something specific? I want to make sure I provide you with the most helpful information.`
        };
    }
    
    addMessageToChat(message) {
        this.chatHistory.push(message);
        this.saveChatHistory();
        
        const messageElement = this.createMessageElement(message);
        this.chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Update quick actions visibility
        this.updateQuickActions();
    }
    
    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.type}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (message.type === 'bot') {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        } else {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        }
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = message.content;
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = this.formatTime(message.timestamp);
        
        content.appendChild(time);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        return messageDiv;
    }
    
    formatTime(timestamp) {
        const now = new Date();
        const messageTime = new Date(timestamp);
        
        if (now.toDateString() === messageTime.toDateString()) {
            return messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else {
            return messageTime.toLocaleDateString() + ' ' + messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.sendBtn.disabled = true;
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
        this.sendBtn.disabled = false;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    updateQuickActions() {
        // Hide quick actions after first message
        if (this.chatHistory.length > 1) {
            this.quickActions.style.display = 'none';
        }
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.chatHistory = [];
            this.chatMessages.innerHTML = '';
            this.quickActions.style.display = 'block';
            this.saveChatHistory();
            this.displayWelcomeMessage();
        }
    }
    
    saveChatHistory() {
        try {
            localStorage.setItem('cllgChatbotHistory', JSON.stringify(this.chatHistory));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }
    
    loadChatHistory() {
        try {
            const saved = localStorage.getItem('cllgChatbotHistory');
            if (saved) {
                this.chatHistory = JSON.parse(saved);
                this.chatHistory.forEach(message => {
                    this.addMessageToChat(message);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CllgChatbot();
});

// Add some interactive features
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling
    const smoothScroll = (target, duration) => {
        const targetPosition = target.getBoundingClientRect().top;
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        let startTime = null;
        
        const animation = currentTime => {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = ease(timeElapsed, startPosition, distance, duration);
            window.scrollTo(0, run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        };
        
        const ease = (t, b, c, d) => {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        };
        
        requestAnimationFrame(animation);
    };
    
    // Smooth scroll to features section
    const featuresSection = document.querySelector('.features-section');
    if (featuresSection) {
        featuresSection.addEventListener('click', () => {
            smoothScroll(featuresSection, 1000);
        });
    }
    
    // Add loading animation for quick actions
    const quickBtns = document.querySelectorAll('.quick-btn');
    quickBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                btn.style.transform = 'scale(1)';
            }, 150);
        });
    });
}); 