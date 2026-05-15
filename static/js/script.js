// Cllg Chatbot - Frontend JavaScript
class CllgChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearChatBtn = document.getElementById('clearChat');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.quickActions = document.getElementById('quickActions');
        this.locationSelect = document.getElementById('locationSelect');
        this.travelMode = document.getElementById('travelMode');
        this.getDirectionsBtn = document.getElementById('getDirectionsBtn');
        this.locationsCache = [];
        this.lastSuggestedDest = null;
        this.lastSuggestedName = null;
        
        this.chatHistory = [];
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadChatHistory();
        // Only display welcome message if no chat history exists
        if (this.chatHistory.length === 0) {
            this.displayWelcomeMessage();
        }
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

        // Directions widget
        if (this.getDirectionsBtn) {
            this.getDirectionsBtn.addEventListener('click', () => this.openDirections());
        }

        // Inline directions buttons inside chat
        this.chatMessages.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action="directions"]');
            if (btn) {
                const dest = btn.getAttribute('data-dest') || '';
                const mode = btn.getAttribute('data-mode') || 'walking';
                this.openDirectionsTo(dest, mode);
            }
        });
    }
    
    displayWelcomeMessage() {
        // Check if welcome message already exists in chat history
        const welcomeContent = `Hello! I'm your AI college assistant. I'm here to help you 24/7 with any questions about college life, academics, campus services, and more. How can I assist you today?`;
        
        // Only add if no welcome message exists
        const hasWelcomeMessage = this.chatHistory.some(msg => 
            msg.type === 'bot' && msg.content === welcomeContent
        );
        
        if (!hasWelcomeMessage) {
            const welcomeMessage = {
                type: 'bot',
                content: welcomeContent,
                timestamp: new Date()
            };
            
            this.addMessageToChat(welcomeMessage);
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // If user says yes/okay/etc right after a suggestion, open directions immediately
        if (this.lastSuggestedDest && this.isAffirmative(message)) {
            // Echo user message
            const userMessage = { type: 'user', content: message, timestamp: new Date() };
            this.addMessageToChat(userMessage);
            this.messageInput.value = '';
            try {
                await this.openDirectionsTo(this.lastSuggestedDest, 'walking');
                const confirm = {
                    type: 'bot',
                    content: `Opening Google Maps for directions to <strong>${this.escapeHtml(this.lastSuggestedName || 'destination')}</strong>...`,
                    timestamp: new Date()
                };
                this.addMessageToChat(confirm);
            } catch (_) {}
            return;
        }
        
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
            const source = response.source;
            let content = this.formatContent(response.reply);
            if (source && source.type === 'admin') {
                const parts = [];
                if (source.title) parts.push(source.title);
                if (source.source_pdf) parts.push(source.source_pdf);
                const label = parts.join(' • ');
                content += `\n\n<div class="small" style="color:#64748b">Source: ${label}</div>`;
            }
            const botMessage = { type: 'bot', content, timestamp: new Date() };
            
            this.addMessageToChat(botMessage);

            // If user asked for a known location, suggest directions inline
            try {
                const matched = this.findMatchingLocation(message);
                if (matched) {
                    const dest = (matched.latitude != null && matched.longitude != null) ? `${matched.latitude},${matched.longitude}` : (matched.maps_query || matched.name);
                    this.lastSuggestedDest = dest;
                    this.lastSuggestedName = matched.name || null;
                    const hint = {
                        type: 'bot',
                        content: `<div style="margin-top:8px;">Would you like directions to <strong>${this.escapeHtml(matched.name)}</strong>? <button data-action="directions" data-dest="${this.escapeHtml(dest)}" data-mode="walking" class="btn-secondary" style="margin-left:8px; padding:6px 10px;">Get Directions</button></div>`,
                        timestamp: new Date()
                    };
                    this.addMessageToChat(hint);
                }
            } catch (_) {}
            
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
    
    // Convert numeric-heavy blocks into a simple HTML table for readability
    formatContent(raw) {
        if (!raw) return '';
        const text = String(raw);
        // Heuristic: if there are at least 3 lines that each contain 3+ commas or 3+ numbers, try to tabularize
        const lines = text.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0);
        const numericLines = lines.filter(l => (l.match(/\d+/g) || []).length >= 3);
        const commaRich = lines.filter(l => (l.match(/,/g) || []).length >= 3);
        const shouldTabularize = numericLines.length >= 3 || commaRich.length >= 3;
        if (!shouldTabularize) return text.replace(/\n/g, '<br/>');
        // Build rows by splitting on commas first, then on 2+ spaces as fallback
        const rows = lines
            .map(l => l.replace(/\s{2,}/g, ' ').replace(/\s*\,\s*/g, ',').trim())
            .map(l => l.includes(',') ? l.split(',') : l.split(' '))
            .map(cols => cols.map(c => c.trim()).filter(c => c.length > 0));
        // Filter out rows that are too short
        const filtered = rows.filter(r => r.length >= 2);
        if (filtered.length < 2) return text.replace(/\n/g, '<br/>');
        const maxCols = Math.max(...filtered.map(r => r.length));
        const tableHead = `<tr>${new Array(maxCols).fill(0).map((_, i) => `<th>Col ${i+1}</th>`).join('')}</tr>`;
        const tableBody = filtered.map(r => {
            const cells = r.slice(0, maxCols);
            while (cells.length < maxCols) cells.push('');
            return `<tr>${cells.map(c => `<td>${this.escapeHtml(c)}</td>`).join('')}</tr>`;
        }).join('');
        const tableHtml = `
<div style="overflow:auto; max-height:360px;">
  <table style="width:100%; border-collapse:collapse; font-size:14px;">
    <thead>${tableHead}</thead>
    <tbody>${tableBody}</tbody>
  </table>
</div>`;
        // Minimal styling via inline CSS
        return tableHtml
            .replace(/<table /, '<table border="1" ') // add borders
            ;
    }

    escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
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
                reply: `We have comprehensive campus services to support your academic and personal success:

**Academic Support Services:**
• **Writing Center** (Mon-Fri, 9 AM-5 PM, Library 2nd Floor)
  - One-on-one writing consultations
  - Essay and research paper assistance
  - Citation and formatting help
  - Online appointment booking available

• **Math Lab** (Mon-Thu, 10 AM-8 PM, Science Building Room 105)
  - Drop-in tutoring for all math levels
  - Calculus, statistics, and algebra support
  - Practice exams and study materials
  - Group study sessions available

• **Tutoring Services** (by appointment, Student Success Center)
  - Subject-specific tutoring in 20+ disciplines
  - Peer tutoring and professional tutors
  - Study skills workshops
  - Online tutoring options

• **Academic Advising** (Mon-Fri, 8 AM-6 PM)
  - Major and minor planning
  - Course selection guidance
  - Graduation requirements tracking
  - Transfer credit evaluation

**Health & Wellness Services:**
• **Student Health Center** (Mon-Fri, 8 AM-5 PM, Wellness Building)
  - Primary care and urgent care
  - Immunizations and physicals
  - Mental health screenings
  - Health education programs

• **Counseling Services** (confidential, free, Wellness Building 2nd Floor)
  - Individual and group therapy
  - Crisis intervention
  - Stress management workshops
  - 24/7 crisis hotline: (555) 123-4569

• **Fitness Center** (6 AM-11 PM daily, Recreation Center)
  - Cardio and strength training equipment
  - Group fitness classes (yoga, Zumba, cycling)
  - Personal training sessions
  - Indoor pool and racquetball courts

• **Recreation Center** (7 AM-12 AM daily)
  - Intramural sports leagues
  - Outdoor adventure trips
  - Equipment rental (bikes, camping gear)
  - Climbing wall and challenge course

**Student Life Services:**
• **Student Union** (7 AM-12 AM daily, Main Campus)
  - Food court with diverse dining options
  - Meeting rooms and event spaces
  - Game room and lounge areas
  - Information desk and lost & found

• **Career Services** (Mon-Fri, 9 AM-5 PM, Career Center)
  - Resume and cover letter assistance
  - Mock interviews and career counseling
  - Job and internship postings
  - Career fairs and networking events

• **International Student Office** (Mon-Fri, 8 AM-5 PM)
  - Visa and immigration support
  - Cultural adjustment assistance
  - English language support
  - International student orientation

• **Disability Services** (Mon-Fri, 8 AM-5 PM)
  - Academic accommodations
  - Assistive technology support
  - Note-taking services
  - Accessibility advocacy

**Technology & Infrastructure:**
• **IT Help Desk** (24/7 support, Tech Support Building)
  - Phone: (555) 123-4567
  - Email: helpdesk@college.edu
  - Live chat on college website
  - Walk-in support (Mon-Fri, 8 AM-8 PM)

• **Computer Labs** (various locations across campus)
  - Main Library: 50+ computers with specialized software
  - Science Building: Lab computers with scientific applications
  - Business School: Financial modeling and analysis tools
  - Arts Center: Creative software (Adobe Suite, Final Cut Pro)

• **WiFi & Network** (campus-wide coverage)
  - Connect to "College_Network" with student ID
  - High-speed internet in all buildings
  - Secure network with VPN access
  - Guest WiFi available for visitors

**Additional Services:**
• **Transportation Services** (shuttle routes, bike share, carpool matching)
• **Safety & Security** (24/7 campus police, emergency phones, escort service)
• **Dining Services** (meal plans, dietary accommodations, food trucks)
• **Housing & Residence Life** (room assignments, maintenance requests, RA support)

What specific service would you like more information about? I can provide detailed hours, locations, and contact information for any of these services.`
            };
        }
        
        // Student life
        if (lowerMessage.includes('student life') || lowerMessage.includes('club') || lowerMessage.includes('activity') || lowerMessage.includes('event')) {
            return {
                reply: `Campus life is vibrant and engaging! Here's everything you need to know about getting involved:

**Student Organizations (100+ Active Clubs):**
• **Academic & Professional Clubs:**
  - Math Club (meets Wednesdays, 6 PM, Science Building)
  - Science Society (monthly meetings, research presentations)
  - Business Students Association (networking events, guest speakers)
  - Pre-Med Society (MCAT prep, medical school visits)
  - Engineering Club (robotics competitions, industry tours)

• **Cultural & International Organizations:**
  - International Student Association (cultural nights, language exchange)
  - Black Student Union (advocacy, cultural celebrations)
  - Latinx Student Association (heritage month events)
  - Asian Student Alliance (cultural festivals, mentorship)
  - LGBTQ+ Student Union (support groups, awareness events)

• **Service & Community Groups:**
  - Community Service Club (volunteer opportunities, food drives)
  - Environmental Club (campus sustainability, local cleanups)
  - Habitat for Humanity (home building projects)
  - Red Cross Club (blood drives, disaster relief training)

• **Special Interest & Hobby Clubs:**
  - Photography Club (exhibitions, workshops, photo walks)
  - Gaming Club (esports tournaments, board game nights)
  - Anime & Manga Society (conventions, screenings)
  - Chess Club (tournaments, strategy sessions)
  - Outdoor Adventure Club (hiking, camping, rock climbing)

**Major Campus Events & Traditions:**
• **August: Welcome Week**
  - New student orientation and campus tours
  - Club fair and involvement showcase
  - Welcome concert and social events
  - Residence hall move-in assistance

• **October: Homecoming Week**
  - Alumni reunions and networking
  - Football game and tailgate parties
  - Parade and spirit competitions
  - Class reunions and awards ceremonies

• **November: International Education Week**
  - Cultural performances and food festivals
  - Study abroad information sessions
  - International student spotlight events
  - Language learning workshops

• **February: Black History Month**
  - Guest speakers and cultural performances
  - Historical exhibits and film screenings
  - Community discussions and workshops
  - Art and music celebrations

• **March: Women's History Month**
  - Leadership conferences and workshops
  - Women in STEM panels
  - Feminist film series
  - Career development seminars

• **April: Spring Festival**
  - Campus-wide celebration with live music
  - Food trucks and vendor fair
  - Student talent shows and competitions
  - Environmental awareness activities

**Recreation & Sports:**
• **Intramural Sports (year-round):**
  - Fall: Flag football, soccer, volleyball
  - Winter: Basketball, indoor soccer, dodgeball
  - Spring: Softball, ultimate frisbee, tennis
  - Summer: Beach volleyball, swimming, track

• **Outdoor Adventure Program:**
  - Weekend hiking trips to nearby mountains
  - Spring break adventure excursions
  - Equipment rental (tents, kayaks, climbing gear)
  - Outdoor skills workshops and certifications

• **Fitness & Wellness:**
  - 50+ group fitness classes weekly
  - Personal training sessions ($25/hour)
  - Yoga and meditation workshops
  - Nutrition counseling and meal planning

• **Entertainment & Social:**
  - Movie nights in the student center
  - Karaoke and open mic nights
  - Game tournaments and trivia nights
  - Holiday parties and themed events

**Leadership & Professional Development:**
• **Student Government:**
  - Student Senate (elected representatives)
  - Executive Board positions (President, VP, Treasurer)
  - Committee leadership opportunities
  - Budget allocation and policy making

• **Residence Life Leadership:**
  - Resident Assistant positions (paid, includes room & board)
  - Hall Council leadership roles
  - Community building and programming
  - Crisis response and peer support

• **Peer Mentoring Programs:**
  - First-year student mentors
  - Academic subject tutors
  - Career exploration guides
  - International student buddies

• **Professional Development:**
  - Leadership workshops and retreats
  - Public speaking and presentation skills
  - Conflict resolution and team building
  - Resume building and interview prep

**Getting Involved:**
• **Club Fair:** First week of each semester
• **New Member Orientations:** Ongoing throughout the year
• **Leadership Applications:** Due in March for next academic year
• **Volunteer Opportunities:** Posted weekly on student portal

**Benefits of Involvement:**
• Build lasting friendships and professional networks
• Develop leadership and communication skills
• Enhance your resume and graduate school applications
• Gain real-world experience in your field of interest
• Access to exclusive events and opportunities

**Contact Information:**
• **Student Activities Office:** (555) 123-4570
• **Leadership Development:** leadership@college.edu
• **Volunteer Services:** volunteer@college.edu
• **Event Planning:** events@college.edu

Ready to get involved? I can help you find specific clubs, upcoming events, or leadership opportunities that match your interests!`
            };
        }
        
        // Technical support
        if (lowerMessage.includes('technical') || lowerMessage.includes('computer') || lowerMessage.includes('software') || lowerMessage.includes('wifi')) {
            return {
                reply: `Need tech help? We've got comprehensive IT support to keep you connected and productive:

**IT Support Services (24/7 Availability):**
• **Help Desk Hotline:** (555) 123-4567
• **Email Support:** helpdesk@college.edu
• **Live Chat:** Available on college website and student portal
• **Walk-in Support:** Tech Support Building (Mon-Fri, 8 AM-8 PM)
• **Emergency Support:** After-hours critical issues only

**Network & WiFi Support:**
• **WiFi Connection:**
  - Network: "College_Network"
  - Username: Your student ID (e.g., 12345678)
  - Password: Your student portal password
  - Security: WPA2 Enterprise encryption

• **WiFi Coverage:**
  - All academic buildings and residence halls
  - Outdoor spaces (quad, athletic fields)
  - Guest WiFi available for visitors
  - VPN access for secure remote connections

• **Common WiFi Issues & Solutions:**
  - Can't connect: Restart device, forget network, reconnect
  - Slow connection: Move closer to access points
  - Authentication errors: Check student ID and password
  - Device limit: Maximum 3 devices per student

**Email & Communication:**
• **Student Email Setup:**
  - Address: username@college.edu
  - Webmail: mail.college.edu
  - Mobile setup: Use IMAP/SMTP settings
  - Storage: 50GB mailbox storage

• **Email Features:**
  - Microsoft Outlook integration
  - Calendar and scheduling tools
  - OneDrive cloud storage (1TB)
  - Teams for collaboration

**Software & Applications:**
• **Free Software for Students:**
  - Microsoft Office 365 (Word, Excel, PowerPoint, Access)
  - Adobe Creative Suite (Photoshop, Illustrator, InDesign)
  - Statistical software (SPSS, SAS, R, MATLAB)
  - Programming tools (Visual Studio, Eclipse, PyCharm)
  - Antivirus software (McAfee, free download)

• **Software Installation:**
  - Download from student portal
  - Installation guides and tutorials available
  - Remote installation support for complex software
  - License management and renewal assistance

**Computer Labs & Equipment:**
• **Main Library Computer Lab (Room 101):**
  - 50+ Windows workstations
  - High-speed internet and printing
  - Scanning and document services
  - Extended hours during finals (24/7)

• **Science Building Lab (Room 205):**
  - 30 specialized computers
  - Scientific software (MATLAB, R, Python)
  - Data analysis and visualization tools
  - Research project support

• **Business School Lab (Room 150):**
  - 25 financial modeling workstations
  - Bloomberg Terminal access
  - Excel and financial software training
  - Case study analysis tools

• **Arts Center Lab (Room 75):**
  - 20 Mac workstations
  - Adobe Creative Suite (full version)
  - Video editing and animation software
  - Digital art and design tools

**Printing & Document Services:**
• **Printing Quotas:**
  - Free pages: 100 per semester
  - Additional pages: $0.10 per page
  - Color printing: $0.25 per page
  - Large format: $2.00 per page

• **Printing Locations:**
  - Main Library (24/7 with student ID)
  - Student Center (7 AM-11 PM)
  - Residence Halls (lobby areas)
  - Academic buildings (designated printers)

• **Document Services:**
  - Scanning: Free (up to 50 pages per day)
  - Binding: $2.00 per document
  - Laminating: $1.00 per page
  - Business cards: $10.00 per 100

**Device Support & Troubleshooting:**
• **Laptop/Desktop Support:**
  - Operating system issues (Windows, macOS, Linux)
  - Hardware diagnostics and repair referrals
  - Virus and malware removal
  - Data backup and recovery

• **Mobile Device Support:**
  - Smartphone and tablet setup
  - Email and calendar configuration
  - App installation and troubleshooting
  - Security and privacy settings

• **Software Installation Help:**
  - Step-by-step installation guides
  - Compatibility checking
  - Driver updates and troubleshooting
  - License activation assistance

**Online Learning Support:**
• **Learning Management System (Canvas):**
  - Course access and navigation
  - Assignment submission
  - Discussion board participation
  - Grade checking and feedback

• **Video Conferencing:**
  - Zoom account setup and training
  - Teams meeting scheduling
  - Recording and sharing options
  - Technical troubleshooting during sessions

**Security & Privacy:**
• **Account Security:**
  - Two-factor authentication setup
  - Password management and reset
  - Account lockout assistance
  - Security awareness training

• **Data Protection:**
  - Regular backup recommendations
  - Encryption tools and guidance
  - Safe browsing practices
  - Phishing awareness and reporting

**Training & Resources:**
• **IT Workshops (Free):**
  - Basic computer skills (weekly)
  - Software training (monthly)
  - Cybersecurity awareness (quarterly)
  - Online learning tools (as needed)

• **Self-Service Resources:**
  - Knowledge base articles
  - Video tutorials and guides
  - FAQ database
  - Community forums

**Contact & Support Hours:**
• **24/7 Phone Support:** (555) 123-4567
• **Email Response:** Within 4 hours during business hours
• **Walk-in Support:** Mon-Fri, 8 AM-8 PM
• **Emergency Support:** After-hours critical issues only
• **Online Chat:** Available 24/7 on website

**Escalation Process:**
• Level 1: Basic troubleshooting and guidance
• Level 2: Advanced technical support
• Level 3: Specialist consultation
• Level 4: Vendor escalation if needed

What specific technical issue are you experiencing? I can provide step-by-step solutions or connect you with the appropriate support team.`
            };
        }
        
        // Academic calendar
        if (lowerMessage.includes('calendar') || lowerMessage.includes('deadline') || lowerMessage.includes('exam') || lowerMessage.includes('break')) {
            return {
                reply: `Here's the comprehensive academic calendar for the 2024-2025 academic year:

**Fall Semester 2024 (August 26 - December 20):**
• **August 26** - Classes begin
• **August 26-September 6** - Add/Drop period (100% refund)
• **September 2** - Labor Day (no classes, campus closed)
• **September 9-13** - Late registration period (50% refund)
• **September 16-20** - Withdrawal period (25% refund)
• **October 14-15** - Fall Break (no classes)
• **October 21** - Midterm grades due
• **November 11** - Veterans Day (no classes)
• **November 27-29** - Thanksgiving Break (no classes, campus closed)
• **December 2-6** - Last week of classes
• **December 9-13** - Reading/Study days
• **December 16-20** - Final examinations
• **December 20** - Fall semester ends
• **December 21** - Commencement (Fall graduates)

**Spring Semester 2025 (January 13 - May 10):**
• **January 13** - Classes begin
• **January 13-24** - Add/Drop period (100% refund)
• **January 20** - Martin Luther King Day (no classes)
• **January 27-31** - Late registration period (50% refund)
• **February 3-7** - Withdrawal period (25% refund)
• **February 17** - Presidents' Day (no classes)
• **March 3-7** - Midterm grades due
• **March 10-14** - Spring Break (no classes)
• **April 18-20** - Easter Break (no classes)
• **April 28** - Last day to withdraw from classes
• **May 5-9** - Final examinations
• **May 10** - Spring semester ends & Commencement

**Summer Sessions 2025:**
• **May 19-June 27** - Summer Session I (6 weeks)
• **June 30-August 8** - Summer Session II (6 weeks)
• **May 19-August 8** - Summer Session III (12 weeks)

**Important Academic Deadlines:**
• **Graduation Application Deadlines:**
  - Fall graduation: July 1st
  - Spring graduation: March 1st
  - Summer graduation: April 1st

• **Financial Aid Deadlines:**
  - FAFSA priority deadline: March 1st
  - Scholarship applications: February 15th
  - Work-study applications: May 1st

• **Housing Deadlines:**
  - Fall housing application: May 1st
  - Spring housing application: November 1st
  - Housing deposit: $200 due with application

• **Registration Deadlines:**
  - Priority registration: April (for Fall), November (for Spring)
  - Open registration: May-August (for Fall), December-January (for Spring)
  - Late registration fee: $100 after classes begin

**Special Academic Periods:**
• **Advising Week:** Week before registration opens
• **Finals Week:** Extended library hours (24/7)
• **Grade Posting:** 48 hours after final exam completion
• **Transcript Requests:** Available 5 business days after grades post

**Holiday Closures (Campus Closed):**
• Labor Day, Thanksgiving, Christmas Eve/Day, New Year's Day
• Martin Luther King Day, Presidents' Day, Memorial Day, Independence Day

**Academic Policies:**
• **Attendance:** Required for all classes
• **Grading:** A-F scale with plus/minus options
• **Academic Standing:** GPA requirements for good standing
• **Academic Integrity:** Honor code enforcement

Need specific dates for your program, major requirements, or other academic information? I can also help you find your academic advisor or check your degree progress.`
            };
        }
        
        // Housing information
        if (lowerMessage.includes('housing') || lowerMessage.includes('dorm') || lowerMessage.includes('residence') || lowerMessage.includes('room') || lowerMessage.includes('accommodation')) {
            return {
                reply: `We offer excellent on-campus housing options for students:

**Residence Halls:**
• Traditional dorms: $4,500/semester
• Suite-style: $5,200/semester
• Apartment-style: $6,000/semester

**Amenities Included:**
• High-speed WiFi
• Laundry facilities
• Study lounges
• 24/7 security
• Meal plan options

**Application Process:**
1. Submit housing application by May 1st
2. Pay $200 housing deposit
3. Room selection in June
4. Move-in day: August 24th

**Living Learning Communities:**
• Honors Hall - Academic focus
• Global Village - International students
• STEM House - Science & engineering
• Arts Collective - Creative students

Would you like information about specific residence halls or off-campus options?`
            };
        }
        
        // Parking and transportation
        if (lowerMessage.includes('parking') || lowerMessage.includes('car') || lowerMessage.includes('vehicle') || lowerMessage.includes('transportation') || lowerMessage.includes('commute')) {
            return {
                reply: `Here's everything you need to know about parking and transportation:

**Student Parking Permits:**
• Annual permit: $300
• Semester permit: $180
• Daily parking: $5/day

**Parking Lots:**
• North Campus: 500 spaces
• South Campus: 300 spaces
• East Campus: 200 spaces
• Visitor parking: 50 spaces

**Free Shuttle Service:**
• Runs every 15 minutes
• 7:00 AM - 11:00 PM daily
• Connects all campus areas
• Real-time tracking app available

**Alternative Transportation:**
• City bus routes (free with student ID)
• Bike share program
• Carpool matching service

Need help with permit application or shuttle routes?`
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
            // Add welcome message to history and display it
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
                // Clear any existing displayed messages first
                this.chatMessages.innerHTML = '';
                // Display existing messages without adding them to history again
                this.chatHistory.forEach(message => {
                    this.displayMessageOnly(message);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    displayMessageOnly(message) {
        // Display message without adding to chat history
        const messageElement = this.createMessageElement(message);
        this.chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Update quick actions visibility
        this.updateQuickActions();
    }

    async loadLocationsIntoSelect() {
        try {
            if (!this.locationSelect) return;
            const res = await fetch('/api/locations');
            if (!res.ok) return;
            const data = await res.json();
            const locs = data.locations || [];
            this.locationsCache = locs;
            // Clear existing except placeholder
            this.locationSelect.querySelectorAll('option:not(:first-child)').forEach(o => o.remove());
            locs.forEach(loc => {
                const opt = document.createElement('option');
                opt.value = loc.id;
                const dest = (loc.latitude != null && loc.longitude != null) ? `${loc.latitude},${loc.longitude}` : (loc.maps_query || loc.name);
                opt.setAttribute('data-dest', dest);
                opt.textContent = (loc.name || 'Location') + (loc.category ? ` (${loc.category})` : '');
                this.locationSelect.appendChild(opt);
            });
        } catch (_) {}
    }

    async openDirections() {
        if (!this.locationSelect) return;
        const selected = this.locationSelect.options[this.locationSelect.selectedIndex];
        const destRaw = selected ? selected.getAttribute('data-dest') : '';
        if (!destRaw) { alert('Please select a destination.'); return; }
        const mode = this.travelMode ? (this.travelMode.value || 'walking') : 'walking';
        const openMaps = (originParam) => {
            const base = 'https://www.google.com/maps/dir/?api=1';
            const params = new URLSearchParams();
            if (originParam) params.set('origin', originParam);
            params.set('destination', destRaw);
            params.set('travelmode', mode);
            const url = `${base}&${params.toString()}`;
            window.open(url, '_blank');
        };
        if (navigator.geolocation) {
            try {
                const pos = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 });
                });
                const { latitude, longitude } = pos.coords;
                openMaps(`${latitude},${longitude}`);
            } catch (_) {
                openMaps('');
            }
        } else {
            openMaps('');
        }
    }

    async openDirectionsTo(destRaw, mode = 'walking') {
        const openMaps = (originParam) => {
            const base = 'https://www.google.com/maps/dir/?api=1';
            const params = new URLSearchParams();
            if (originParam) params.set('origin', originParam);
            params.set('destination', destRaw);
            params.set('travelmode', mode);
            const url = `${base}&${params.toString()}`;
            window.open(url, '_blank');
        };
        if (navigator.geolocation) {
            try {
                const pos = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 });
                });
                const { latitude, longitude } = pos.coords;
                openMaps(`${latitude},${longitude}`);
            } catch (_) {
                openMaps('');
            }
        } else {
            openMaps('');
        }
    }

    findMatchingLocation(userText) {
        if (!userText || !this.locationsCache || !this.locationsCache.length) return null;
        const txt = userText.toLowerCase();
        // simple contains match on name and category
        const exact = this.locationsCache.find(l => (l.name || '').toLowerCase() === txt);
        if (exact) return exact;
        return this.locationsCache.find(l =>
            (l.name && txt.includes(l.name.toLowerCase())) ||
            (l.category && txt.includes(l.category.toLowerCase()))
        ) || null;
    }

    isAffirmative(text) {
        const t = (text || '').trim().toLowerCase();
        if (!t) return false;
        const words = ['yes','yeah','yep','ok','okay','sure','please','do it','go ahead','proceed','ya','yup'];
        return words.some(w => t === w || t.includes(w));
    }
}

// Initialize chatbot and add interactive features when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the chatbot
    const bot = new CllgChatbot();
    bot.loadLocationsIntoSelect();
    
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