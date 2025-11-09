#!/usr/bin/env python3
"""
Cllg Chatbot - AI-Powered College Student Assistant
Backend server built with Flask
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import re
import random
from datetime import datetime
import logging
import os
import uuid
from typing import List, Dict, Any, Set
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# App config
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Data storage paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
KNOWLEDGE_FILE = os.path.join(DATA_DIR, 'knowledge.json')
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
LOCATIONS_FILE = os.path.join(DATA_DIR, 'locations.json')

# Admin token (simple header auth)
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'changeme')

def ensure_data_dir():
    try:
        if not os.path.isdir(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.isdir(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create data directory: {e}")

def read_json_file(path: str, default: Any):
    try:
        if not os.path.isfile(path):
            return default
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON file {path}: {e}")
        return default

def write_json_file(path: str, data: Any) -> bool:
    try:
        tmp_path = f"{path}.tmp"
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
        return True
    except Exception as e:
        logger.error(f"Failed to write JSON file {path}: {e}")
        return False

class CollegeAI:
    """AI-powered college assistant with knowledge base"""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_history = []
        ensure_data_dir()
        self.admin_knowledge: List[Dict[str, Any]] = self._load_admin_knowledge()
        # Basic stopwords for lightweight keyword scoring
        self._stopwords: Set[str] = set([
            'the','a','an','and','or','but','if','then','else','on','in','at','for','to','from','by','with','of','is','are','was','were','be','been','it','this','that','these','those','as','about','into','over','under','after','before','between','how','what','when','where','which','who','whom','why','can','do','does','did','will','would','should','could','may','might','you','your','yours','we','our','ours','they','their','theirs','i','me','my','mine'
        ])
        
    def _load_knowledge_base(self):
        """Load comprehensive knowledge base for college information"""
        return {
            'admission': {
                'keywords': ['admission', 'requirements', 'apply', 'application', 'enroll', 'enrollment'],
                'responses': [
                    "Here are the general admission requirements for our college:\n\n"
                    "• High school diploma or equivalent (GED)\n"
                    "• Completed application form with $50 application fee\n"
                    "• Official high school transcripts\n"
                    "• SAT or ACT scores (recommended)\n"
                    "• Personal statement or essay\n"
                    "• Letters of recommendation (2 required)\n"
                    "• Application deadline: March 1st for Fall semester\n\n"
                    "For specific programs, additional requirements may apply. Would you like me to provide details about a particular major or program?",
                    
                    "To apply to our college, you'll need:\n\n"
                    "**Required Documents:**\n"
                    "• Application form (online or paper)\n"
                    "• $50 non-refundable application fee\n"
                    "• High school transcripts\n"
                    "• Standardized test scores\n\n"
                    "**Recommended:**\n"
                    "• Personal essay (500-750 words)\n"
                    "• Letters of recommendation\n"
                    "• Resume of activities\n\n"
                    "The application process typically takes 4-6 weeks for review."
                ]
            },
            
            'courses': {
                'keywords': ['course', 'class', 'major', 'program', 'curriculum', 'syllabus'],
                'responses': [
                    "We offer a wide range of courses across various disciplines:\n\n"
                    "**Arts & Humanities:**\n"
                    "• English Literature, Creative Writing, History, Philosophy, Art History\n\n"
                    "**Business & Economics:**\n"
                    "• Business Administration, Marketing, Finance, Economics, Entrepreneurship\n\n"
                    "**Science & Technology:**\n"
                    "• Computer Science, Biology, Chemistry, Physics, Mathematics, Engineering\n\n"
                    "**Social Sciences:**\n"
                    "• Psychology, Sociology, Political Science, Anthropology, Education\n\n"
                    "**Health Sciences:**\n"
                    "• Nursing, Public Health, Nutrition, Exercise Science\n\n"
                    "Each major has specific course requirements and electives. What field interests you most?",
                    
                    "Our academic programs are designed to provide comprehensive education:\n\n"
                    "**Undergraduate Programs:**\n"
                    "• Bachelor of Arts (BA)\n"
                    "• Bachelor of Science (BS)\n"
                    "• Bachelor of Business Administration (BBA)\n\n"
                    "**Graduate Programs:**\n"
                    "• Master of Arts (MA)\n"
                    "• Master of Science (MS)\n"
                    "• Master of Business Administration (MBA)\n\n"
                    "**Special Features:**\n"
                    "• Honors Program\n"
                    "• Study Abroad opportunities\n"
                    "• Internship programs\n"
                    "• Research opportunities"
                ]
            },
            
            'financial_aid': {
                'keywords': ['financial', 'aid', 'scholarship', 'cost', 'tuition', 'fee', 'money', 'payment'],
                'responses': [
                    "We're committed to making education affordable! Here's information about financial aid:\n\n"
                    "**Tuition & Fees:**\n"
                    "• Full-time tuition: $12,500 per semester\n"
                    "• Room & board: $8,000 per semester\n"
                    "• Books & supplies: ~$1,200 per semester\n\n"
                    "**Financial Aid Options:**\n"
                    "• Federal Pell Grants (up to $6,895/year)\n"
                    "• Federal Direct Loans\n"
                    "• Work-study programs\n"
                    "• Institutional scholarships\n"
                    "• State grants\n\n"
                    "**Application Process:**\n"
                    "1. Complete FAFSA (Free Application for Federal Student Aid)\n"
                    "2. Submit by March 1st priority deadline\n"
                    "3. Review your financial aid package\n"
                    "4. Accept/decline offers\n\n"
                    "Our financial aid office can help you explore all options. Would you like me to connect you with them?",
                    
                    "Understanding college costs is important! Here's a breakdown:\n\n"
                    "**Annual Costs (Full-time):**\n"
                    "• Tuition: $25,000\n"
                    "• Room & Board: $16,000\n"
                    "• Books & Supplies: $2,400\n"
                    "• Personal Expenses: $3,000\n"
                    "• **Total: ~$46,400/year**\n\n"
                    "**Ways to Reduce Costs:**\n"
                    "• Apply for scholarships early\n"
                    "• Consider community college for first 2 years\n"
                    "• Live off-campus (may be cheaper)\n"
                    "• Buy used textbooks\n"
                    "• Apply for work-study positions"
                ]
            },
            
            'library': {
                'keywords': ['library', 'hours', 'study', 'book', 'resource', 'research'],
                'responses': [
                    "Our library is a great place to study! Here are the current hours:\n\n"
                    "**Main Library Hours:**\n"
                    "• Monday-Thursday: 7:00 AM - 11:00 PM\n"
                    "• Friday: 7:00 AM - 8:00 PM\n"
                    "• Saturday: 9:00 AM - 6:00 PM\n"
                    "• Sunday: 12:00 PM - 11:00 PM\n\n"
                    "**Special Collections:**\n"
                    "• Rare Books Room: By appointment only\n"
                    "• Media Center: Same as main library\n"
                    "• Study Rooms: Available for 2-hour reservations\n\n"
                    "**Extended Hours During Finals:**\n"
                    "• Open 24/7 during final exam week\n"
                    "• Coffee cart available in evenings\n\n"
                    "The library also offers online resources accessible 24/7 from anywhere!",
                    
                    "The library provides comprehensive academic support:\n\n"
                    "**Physical Resources:**\n"
                    "• 500,000+ books and journals\n"
                    "• 50+ study rooms\n"
                    "• Computer workstations\n"
                    "• Printing services (100 free pages/semester)\n\n"
                    "**Online Resources:**\n"
                    "• E-books and databases\n"
                    "• Research guides\n"
                    "• Citation tools\n"
                    "• 24/7 chat support\n\n"
                    "**Services:**\n"
                    "• Research consultations\n"
                    "• Interlibrary loan\n"
                    "• Course reserves\n"
                    "• Technology help"
                ]
            },
            
            'campus_services': {
                'keywords': ['campus', 'service', 'facility', 'center', 'office', 'help'],
                'responses': [
                    "We have comprehensive campus services to support your academic and personal success:\n\n"
                    "**Academic Support Services:**\n"
                    "• **Writing Center** (Mon-Fri, 9 AM-5 PM, Library 2nd Floor)\n"
                    "  - One-on-one writing consultations\n"
                    "  - Essay and research paper assistance\n"
                    "  - Citation and formatting help\n"
                    "  - Online appointment booking available\n\n"
                    "• **Math Lab** (Mon-Thu, 10 AM-8 PM, Science Building Room 105)\n"
                    "  - Drop-in tutoring for all math levels\n"
                    "  - Calculus, statistics, and algebra support\n"
                    "  - Practice exams and study materials\n"
                    "  - Group study sessions available\n\n"
                    "**Health & Wellness Services:**\n"
                    "• **Student Health Center** (Mon-Fri, 8 AM-5 PM, Wellness Building)\n"
                    "• **Counseling Services** (confidential, free, 24/7 crisis hotline)\n"
                    "• **Fitness Center** (6 AM-11 PM daily, Recreation Center)\n"
                    "• **Recreation Center** (7 AM-12 AM daily)\n\n"
                    "**Student Life Services:**\n"
                    "• **Student Union** (7 AM-12 AM daily, Main Campus)\n"
                    "• **Career Services** (Mon-Fri, 9 AM-5 PM, Career Center)\n"
                    "• **International Student Office** (Mon-Fri, 8 AM-5 PM)\n"
                    "• **Disability Services** (Mon-Fri, 8 AM-5 PM)\n\n"
                    "What specific service would you like more information about?",
                    
                    "Our campus is designed to meet all your needs:\n\n"
                    "**Learning Spaces:**\n"
                    "• Modern classrooms with smart technology\n"
                    "• Collaborative study areas\n"
                    "• Quiet study zones\n"
                    "• Outdoor learning spaces\n\n"
                    "**Wellness Facilities:**\n"
                    "• Olympic-size swimming pool\n"
                    "• Fitness center with personal trainers\n"
                    "• Meditation garden\n"
                    "• Health clinic with pharmacy\n\n"
                    "**Student Support:**\n"
                    "• 24/7 campus security\n"
                    "• Emergency response team\n"
                    "• Lost and found office\n"
                    "• Information desk"
                ]
            },
            
            'student_life': {
                'keywords': ['student life', 'club', 'activity', 'event', 'organization', 'social'],
                'responses': [
                    "Campus life is vibrant and engaging! Here's everything you need to know about getting involved:\n\n"
                    "**Student Organizations (100+ Active Clubs):**\n"
                    "• **Academic & Professional Clubs:**\n"
                    "  - Math Club (meets Wednesdays, 6 PM, Science Building)\n"
                    "  - Science Society (monthly meetings, research presentations)\n"
                    "  - Business Students Association (networking events, guest speakers)\n"
                    "  - Pre-Med Society (MCAT prep, medical school visits)\n"
                    "  - Engineering Club (robotics competitions, industry tours)\n\n"
                    "**Cultural & International Organizations:**\n"
                    "• International Student Association (cultural nights, language exchange)\n"
                    "• Black Student Union (advocacy, cultural celebrations)\n"
                    "• Latinx Student Association (heritage month events)\n"
                    "• Asian Student Alliance (cultural festivals, mentorship)\n"
                    "• LGBTQ+ Student Union (support groups, awareness events)\n\n"
                    "**Major Campus Events & Traditions:**\n"
                    "• **August:** Welcome Week (orientation, club fair, welcome concert)\n"
                    "• **October:** Homecoming Week (alumni reunions, football game, parade)\n"
                    "• **November:** International Education Week (cultural performances, study abroad info)\n"
                    "• **February:** Black History Month (guest speakers, cultural celebrations)\n"
                    "• **March:** Women's History Month (leadership conferences, career development)\n"
                    "• **April:** Spring Festival (live music, food trucks, talent shows)\n\n"
                    "**Recreation & Sports:**\n"
                    "• Intramural sports (year-round leagues)\n"
                    "• Outdoor adventure program (hiking, camping, rock climbing)\n"
                    "• Fitness classes (50+ weekly options)\n"
                    "• Entertainment (movie nights, karaoke, game tournaments)\n\n"
                    "Getting involved is a great way to make friends and build your resume!",
                    
                    "There's never a dull moment on campus!\n\n"
                    "**Weekly Activities:**\n"
                    "• Monday: Movie Night\n"
                    "• Tuesday: Trivia Night\n"
                    "• Wednesday: Wellness Wednesday\n"
                    "• Thursday: Live Music\n"
                    "• Friday: Game Night\n"
                    "• Weekend: Outdoor adventures\n\n"
                    "**Special Programs:**\n"
                    "• Leadership development workshops\n"
                    "• Career networking events\n"
                    "• Cultural heritage celebrations\n"
                    "• Community service projects\n\n"
                    "**Athletics:**\n"
                    "• Varsity sports teams\n"
                    "• Club sports\n"
                    "• Intramural leagues\n"
                    "• Fitness challenges"
                ]
            },
            
            'technical_support': {
                'keywords': ['technical', 'computer', 'software', 'wifi', 'internet', 'technology', 'it'],
                'responses': [
                    "Need tech help? We've got comprehensive IT support to keep you connected and productive:\n\n"
                    "**IT Support Services (24/7 Availability):**\n"
                    "• **Help Desk Hotline:** (555) 123-4567\n"
                    "• **Email Support:** helpdesk@college.edu\n"
                    "• **Live Chat:** Available on college website and student portal\n"
                    "• **Walk-in Support:** Tech Support Building (Mon-Fri, 8 AM-8 PM)\n"
                    "• **Emergency Support:** After-hours critical issues only\n\n"
                    "**Network & WiFi Support:**\n"
                    "• **WiFi Connection:** Network: 'College_Network', Username: Your student ID\n"
                    "• **WiFi Coverage:** All academic buildings, residence halls, outdoor spaces\n"
                    "• **Common Issues:** Restart device, check credentials, move closer to access points\n\n"
                    "**Software & Applications:**\n"
                    "• **Free Software:** Microsoft Office 365, Adobe Creative Suite, SPSS, MATLAB\n"
                    "• **Installation:** Download from student portal, guides available, remote support\n\n"
                    "**Computer Labs & Equipment:**\n"
                    "• **Main Library:** 50+ Windows workstations, printing, scanning\n"
                    "• **Science Building:** 30 specialized computers, scientific software\n"
                    "• **Business School:** 25 financial modeling workstations, Bloomberg Terminal\n"
                    "• **Arts Center:** 20 Mac workstations, Adobe Suite, video editing tools\n\n"
                    "What specific technical issue are you experiencing? I can provide step-by-step solutions.",
                    
                    "Technology is essential for modern education:\n\n"
                    "**Available Software:**\n"
                    "• Microsoft Office 365 (free)\n"
                    "• Adobe Creative Suite\n"
                    "• Statistical analysis tools\n"
                    "• Programming environments\n\n"
                    "**Online Platforms:**\n"
                    "• Learning Management System\n"
                    "• Student portal\n"
                    "• Library databases\n"
                    "• Career services platform\n\n"
                    "**Support Channels:**\n"
                    "• In-person help desk\n"
                    "• Remote desktop support\n"
                    "• Video tutorials\n"
                    "• Knowledge base articles"
                ]
            },
            
            'academic_calendar': {
                'keywords': ['calendar', 'deadline', 'exam', 'break', 'holiday', 'schedule'],
                'responses': [
                    "Here's the comprehensive academic calendar for the 2024-2025 academic year:\n\n"
                    "**Fall Semester 2024 (August 26 - December 20):**\n"
                    "• **August 26** - Classes begin\n"
                    "• **August 26-September 6** - Add/Drop period (100% refund)\n"
                    "• **September 2** - Labor Day (no classes, campus closed)\n"
                    "• **September 9-13** - Late registration period (50% refund)\n"
                    "• **October 14-15** - Fall Break (no classes)\n"
                    "• **October 21** - Midterm grades due\n"
                    "• **November 27-29** - Thanksgiving Break (no classes, campus closed)\n"
                    "• **December 16-20** - Final examinations\n"
                    "• **December 20** - Fall semester ends\n\n"
                    "**Spring Semester 2025 (January 13 - May 10):**\n"
                    "• **January 13** - Classes begin\n"
                    "• **January 13-24** - Add/Drop period (100% refund)\n"
                    "• **January 20** - Martin Luther King Day (no classes)\n"
                    "• **March 10-14** - Spring Break (no classes)\n"
                    "• **May 5-9** - Final examinations\n"
                    "• **May 10** - Spring semester ends & Commencement\n\n"
                    "**Important Academic Deadlines:**\n"
                    "• **Graduation Application:** Fall (July 1st), Spring (March 1st), Summer (April 1st)\n"
                    "• **Financial Aid:** FAFSA priority deadline March 1st\n"
                    "• **Housing:** Fall application May 1st, Spring application November 1st\n"
                    "• **Registration:** Priority registration April (Fall), November (Spring)\n\n"
                    "Need specific dates for your program, major requirements, or other academic information?",
                    
                    "Stay organized with our academic calendar:\n\n"
                    "**Registration Periods:**\n"
                    "• Fall registration: April 1-30\n"
                    "• Spring registration: November 1-30\n"
                    "• Summer registration: March 1-31\n\n"
                    "**Academic Deadlines:**\n"
                    "• Course withdrawal: 75% of semester\n"
                    "• Grade change requests: 30 days after grades posted\n"
                    "• Incomplete grade completion: Next semester\n"
                    "• Academic appeal: 10 business days\n\n"
                    "**Special Events:**\n"
                    "• Academic advising week\n"
                    "• Career fair\n"
                    "• Research symposium\n"
                    "• Honors convocation"
                ]
            },
            
            'housing': {
                'keywords': ['housing', 'dorm', 'residence', 'room', 'accommodation', 'living', 'apartment'],
                'responses': [
                    "We offer excellent on-campus housing options for students:\n\n"
                    "**Residence Halls:**\n"
                    "• Traditional dorms: $4,500/semester\n"
                    "• Suite-style: $5,200/semester\n"
                    "• Apartment-style: $6,000/semester\n\n"
                    "**Amenities Included:**\n"
                    "• High-speed WiFi\n"
                    "• Laundry facilities\n"
                    "• Study lounges\n"
                    "• 24/7 security\n"
                    "• Meal plan options\n\n"
                    "**Application Process:**\n"
                    "1. Submit housing application by May 1st\n"
                    "2. Pay $200 housing deposit\n"
                    "3. Room selection in June\n"
                    "4. Move-in day: August 24th\n\n"
                    "Would you like information about specific residence halls or off-campus options?",
                    
                    "Our housing options are designed for student success:\n\n"
                    "**Living Learning Communities:**\n"
                    "• Honors Hall - Academic focus\n"
                    "• Global Village - International students\n"
                    "• STEM House - Science & engineering\n"
                    "• Arts Collective - Creative students\n\n"
                    "**Off-Campus Resources:**\n"
                    "• Approved apartment complexes\n"
                    "• Homestay programs\n"
                    "• Commuter parking permits\n"
                    "• Shuttle service to campus\n\n"
                    "**Housing Office Contact:**\n"
                    "• Phone: (555) 123-4568\n"
                    "• Email: housing@college.edu\n"
                    "• Office: Student Center, Room 201"
                ]
            },
            
            'parking': {
                'keywords': ['parking', 'car', 'vehicle', 'transportation', 'commute', 'shuttle', 'bus'],
                'responses': [
                    "Here's everything you need to know about parking and transportation:\n\n"
                    "**Student Parking Permits:**\n"
                    "• Annual permit: $300\n"
                    "• Semester permit: $180\n"
                    "• Daily parking: $5/day\n\n"
                    "**Parking Lots:**\n"
                    "• North Campus: 500 spaces\n"
                    "• South Campus: 300 spaces\n"
                    "• East Campus: 200 spaces\n"
                    "• Visitor parking: 50 spaces\n\n"
                    "**Free Shuttle Service:**\n"
                    "• Runs every 15 minutes\n"
                    "• 7:00 AM - 11:00 PM daily\n"
                    "• Connects all campus areas\n"
                    "• Real-time tracking app available\n\n"
                    "**Alternative Transportation:**\n"
                    "• City bus routes (free with student ID)\n"
                    "• Bike share program\n"
                    "• Carpool matching service\n\n"
                    "Need help with permit application or shuttle routes?"
                ]
            }
        }

    def _load_admin_knowledge(self) -> List[Dict[str, Any]]:
        """Load admin-provided knowledge entries from JSON file."""
        data = read_json_file(KNOWLEDGE_FILE, default={"entries": []})
        entries = data.get("entries", [])
        # Normalize entries
        normalized = []
        for entry in entries:
            keywords = entry.get('keywords', []) or []
            responses = entry.get('responses')
            response = entry.get('response')
            if responses is None and response is not None:
                responses = [response]
            if not isinstance(responses, list):
                responses = []
            normalized.append({
                'id': entry.get('id') or str(uuid.uuid4()),
                'title': entry.get('title') or 'Custom',
                'keywords': [str(k).lower() for k in keywords if isinstance(k, str)],
                'responses': [str(r) for r in responses if isinstance(r, str)],
                'created_at': entry.get('created_at') or datetime.now().isoformat()
            })
        return normalized
    
    def _tokenize(self, text: str) -> List[str]:
        # Alphanumeric tokens only, lowercase
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return [t for t in tokens if t and t not in self._stopwords]

    def _score_entry_match(self, user_message_lower: str, user_tokens: Set[str], entry: Dict[str, Any]) -> int:
        # 1) Exact keyword presence in message (weighted)
        keywords: List[str] = entry.get('keywords', []) or []
        keyword_hits = sum(1 for k in keywords if k and k in user_message_lower)
        score = keyword_hits * 3
        # 2) Token overlap with keywords
        keyword_tokens = set()
        for k in keywords:
            keyword_tokens.update(self._tokenize(k))
        score += min(len(user_tokens & keyword_tokens), 4)
        # 3) Token overlap with entry title
        title = entry.get('title') or ''
        title_tokens = set(self._tokenize(title))
        score += min(len(user_tokens & title_tokens), 2)
        # 4) Light overlap with response snippets (first two responses only for perf)
        responses: List[str] = entry.get('responses') or []
        sample = " \n ".join(responses[:2])
        resp_tokens = set(self._tokenize(sample))
        score += min(len(user_tokens & resp_tokens), 5)
        return score

    def get_response(self, user_message):
        """Generate AI response based on user message"""
        user_message_lower = user_message.lower()
        user_tokens = set(self._tokenize(user_message))
        
        # Store conversation
        self.conversation_history.append({
            'user': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # First, try to match admin-provided knowledge
        best_admin = None
        best_admin_score = 0
        for entry in self.admin_knowledge:
            score = self._score_entry_match(user_message_lower, user_tokens, entry)
            if score > best_admin_score:
                best_admin_score = score
                best_admin = entry

        if best_admin and best_admin_score > 0 and best_admin.get('responses'):
            response = random.choice(best_admin['responses'])
            if '?' in user_message and response and not response.strip().endswith('?'):
                response += "\n\nIs there anything else you'd like to know?"
            # Store bot response
            self.conversation_history.append({
                'bot': response,
                'timestamp': datetime.now().isoformat()
            })
            return response

        # Otherwise, find the best matching built-in category
        best_match = None
        highest_score = 0
        
        for category, data in self.knowledge_base.items():
            score = sum(1 for keyword in data['keywords'] if keyword in user_message_lower)
            if score > highest_score:
                highest_score = score
                best_match = category
        
        # Generate response
        if best_match and highest_score > 0:
            responses = self.knowledge_base[best_match]['responses']
            response = random.choice(responses)
            
            # Add some personalization
            if '?' in user_message:
                response += "\n\nIs there anything else you'd like to know?"
            
        else:
            # Default response for unrecognized queries
            response = self._get_default_response(user_message)
        
        # Store bot response
        self.conversation_history.append({
            'bot': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return response

    def get_response_with_meta(self, user_message):
        """Generate response and include metadata if matched from admin knowledge."""
        user_message_lower = user_message.lower()
        user_tokens = set(self._tokenize(user_message))
        # Try admin first
        best_admin = None
        best_admin_score = 0
        for entry in self.admin_knowledge:
            score = self._score_entry_match(user_message_lower, user_tokens, entry)
            if score > best_admin_score:
                best_admin_score = score
                best_admin = entry
        if best_admin and best_admin_score > 0 and best_admin.get('responses'):
            text = random.choice(best_admin['responses'])
            if '?' in user_message and text and not text.strip().endswith('?'):
                text += "\n\nIs there anything else you'd like to know?"
            self.conversation_history.append({'user': user_message, 'timestamp': datetime.now().isoformat()})
            self.conversation_history.append({'bot': text, 'timestamp': datetime.now().isoformat()})
            return {
                'text': text,
                'source': {
                    'type': 'admin',
                    'id': best_admin.get('id'),
                    'title': best_admin.get('title'),
                    'source_pdf': best_admin.get('source_pdf')
                }
            }
        # Fallback to built-in
        text = self.get_response(user_message)
        return { 'text': text, 'source': None }
    
    def _get_default_response(self, user_message):
        """Generate default response for unrecognized queries"""
        default_responses = [
            "Thank you for your question! I'm here to help with college-related inquiries.\n\n"
            "I can assist with:\n"
            "• Admission requirements and applications\n"
            "• Course information and academic programs\n"
            "• Financial aid and scholarships\n"
            "• Campus services and facilities\n"
            "• Student life and activities\n"
            "• Technical support\n"
            "• Academic calendar and deadlines\n\n"
            "Could you please rephrase your question or ask about something specific? I want to make sure I provide you with the most helpful information.",
            
            "I appreciate your question! While I'm designed to help with college-related topics, I want to make sure I understand exactly what you need.\n\n"
            "Try asking about:\n"
            "• How to apply to college\n"
            "• What courses are available\n"
            "• How much does college cost\n"
            "• What services are available on campus\n"
            "• When are important deadlines\n\n"
            "Or feel free to ask your question in a different way!",
            
            "I'm here to help with college questions! Sometimes I need a bit more context to provide the best answer.\n\n"
            "You can ask me about:\n"
            "• Academic programs and requirements\n"
            "• Financial aid and costs\n"
            "• Campus life and activities\n"
            "• Student services and support\n"
            "• Important dates and deadlines\n\n"
            "What would you like to know more about?"
        ]
        
        return random.choice(default_responses)
    
    def get_conversation_history(self):
        """Return conversation history for analysis"""
        return self.conversation_history

# Initialize AI assistant
ai_assistant = CollegeAI()

# ------------------------------
# Locations storage & helpers
# ------------------------------

def _load_locations() -> List[Dict[str, Any]]:
    data = read_json_file(LOCATIONS_FILE, default={"locations": []})
    raw = data.get("locations") or []
    normalized: List[Dict[str, Any]] = []
    for loc in raw:
        normalized.append({
            'id': loc.get('id') or str(uuid.uuid4()),
            'name': str(loc.get('name') or 'Unnamed Location'),
            'category': str(loc.get('category') or 'General'),
            'description': str(loc.get('description') or ''),
            'maps_query': str(loc.get('maps_query') or ''),
            'latitude': loc.get('latitude'),
            'longitude': loc.get('longitude'),
            'created_at': loc.get('created_at') or datetime.now().isoformat()
        })
    return normalized

def _save_locations(locations: List[Dict[str, Any]]) -> bool:
    ensure_data_dir()
    payload = {"locations": locations}
    return write_json_file(LOCATIONS_FILE, payload)

# In-memory cache
locations_store: List[Dict[str, Any]] = _load_locations()

@app.route('/')
def index():
    """Serve the main chatbot interface"""
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    """Serve the admin dashboard interface"""
    return render_template('admin.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return AI responses"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get AI response with optional metadata
        result = ai_assistant.get_response_with_meta(user_message)
        ai_response = result['text']
        
        # Log the interaction
        logger.info(f"User: {user_message}")
        logger.info(f"AI: {ai_response[:100]}...")
        
        return jsonify({
            'reply': ai_response,
            'source': result.get('source'),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong. Please try again.'
        }), 500

def _require_admin(req: Any) -> bool:
    token = req.headers.get('X-Admin-Token') or req.args.get('admin_token')
    return token == ADMIN_TOKEN

def _save_admin_entries(entries: List[Dict[str, Any]]) -> bool:
    ensure_data_dir()
    payload = {"entries": entries}
    return write_json_file(KNOWLEDGE_FILE, payload)

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    """Get combined knowledge: built-in categories and admin entries metadata."""
    try:
        built_in = list(ai_assistant.knowledge_base.keys())
        admin_entries = ai_assistant.admin_knowledge
        return jsonify({
            'built_in_categories': built_in,
            'admin_entries': admin_entries,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting knowledge: {e}")
        return jsonify({'error': 'Failed to get knowledge'}), 500

@app.route('/api/knowledge', methods=['POST'])
def add_knowledge():
    """Add a new admin knowledge entry. Requires X-Admin-Token header."""
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        body = request.get_json() or {}
        keywords = body.get('keywords') or []
        responses = body.get('responses')
        response = body.get('response')
        title = body.get('title') or 'Custom'
        if responses is None and response is not None:
            responses = [response]
        if not isinstance(keywords, list) or not keywords:
            return jsonify({'error': 'keywords must be a non-empty array'}), 400
        if not isinstance(responses, list) or not responses:
            return jsonify({'error': 'responses must be a non-empty array'}), 400

        entry = {
            'id': str(uuid.uuid4()),
            'title': str(title),
            'keywords': [str(k).lower() for k in keywords],
            'responses': [str(r) for r in responses],
            'created_at': datetime.now().isoformat()
        }
        entries = ai_assistant.admin_knowledge.copy()
        entries.append(entry)
        if not _save_admin_entries(entries):
            return jsonify({'error': 'Failed to save entry'}), 500
        # Reload into memory
        ai_assistant.admin_knowledge = entries
        return jsonify({'entry': entry, 'status': 'success'})
    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        return jsonify({'error': 'Failed to add knowledge'}), 500

@app.route('/api/knowledge/<entry_id>', methods=['PUT'])
def update_knowledge(entry_id: str):
    """Update an existing admin knowledge entry by id. Requires X-Admin-Token."""
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        body = request.get_json() or {}
        entries = ai_assistant.admin_knowledge.copy()
        found = None
        for e in entries:
            if e.get('id') == entry_id:
                found = e
                break
        if not found:
            return jsonify({'error': 'Entry not found'}), 404
        if 'title' in body:
            found['title'] = str(body['title'])
        if 'keywords' in body and isinstance(body['keywords'], list) and body['keywords']:
            found['keywords'] = [str(k).lower() for k in body['keywords']]
        if 'responses' in body and isinstance(body['responses'], list) and body['responses']:
            found['responses'] = [str(r) for r in body['responses']]
        if not _save_admin_entries(entries):
            return jsonify({'error': 'Failed to save entry'}), 500
        ai_assistant.admin_knowledge = entries
        return jsonify({'entry': found, 'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating knowledge: {e}")
        return jsonify({'error': 'Failed to update knowledge'}), 500

@app.route('/api/knowledge/<entry_id>', methods=['DELETE'])
def delete_knowledge(entry_id: str):
    """Delete an admin knowledge entry by id. Requires X-Admin-Token."""
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        entries = [e for e in ai_assistant.admin_knowledge if e.get('id') != entry_id]
        if len(entries) == len(ai_assistant.admin_knowledge):
            return jsonify({'error': 'Entry not found'}), 404
        if not _save_admin_entries(entries):
            return jsonify({'error': 'Failed to delete entry'}), 500
        ai_assistant.admin_knowledge = entries
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error deleting knowledge: {e}")
        return jsonify({'error': 'Failed to delete knowledge'}), 500

@app.route('/api/knowledge/pdf', methods=['POST'])
def upload_pdf_knowledge():
    """Upload a PDF, extract text, and create a knowledge entry. Requires X-Admin-Token."""
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        ensure_data_dir()
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'Empty file'}), 400
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400

        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_DIR, filename)
        file.save(save_path)

        # Extract text from PDF
        extracted_text = ''
        try:
            from PyPDF2 import PdfReader
            with open(save_path, 'rb') as f:
                reader = PdfReader(f)
                # Try to decrypt if encrypted with empty password
                try:
                    if getattr(reader, 'is_encrypted', False):
                        try:
                            reader.decrypt("")
                        except Exception:
                            pass
                except Exception:
                    pass

                page_texts: List[str] = []
                for page in reader.pages:
                    try:
                        text = page.extract_text() or ''
                    except Exception:
                        text = ''
                    if text:
                        page_texts.append(text)
                extracted_text = '\n\n'.join(page_texts)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return jsonify({'error': f'Failed to extract PDF text: {str(e)}'}), 500

        # Build responses from extracted text (chunk into ~500 char segments, max 10)
        def chunk_text(text: str, size: int = 500) -> List[str]:
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            segments: List[str] = []
            for para in paragraphs:
                start = 0
                while start < len(para):
                    segment = para[start:start+size]
                    segments.append(segment)
                    start += size
            return [s for s in segments if s]

        # Clean extracted text
        extracted_text = re.sub(r"\u0000", "", extracted_text)
        responses = chunk_text(extracted_text, size=800)[:10]
        if not responses:
            return jsonify({'error': 'No selectable text found in PDF (likely scanned). Please upload a text-based PDF or provide a text file instead.'}), 400

        title = request.form.get('title') or os.path.splitext(filename)[0]
        raw_keywords = request.form.get('keywords') or ''
        keywords = [k.strip().lower() for k in raw_keywords.split(',') if k.strip()]
        # Auto-augment keywords from title/filename and frequent tokens from extracted text
        def tokenize(text: str) -> List[str]:
            return [t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if t]
        title_tokens = [t for t in tokenize(title) if len(t) > 2]
        base_tokens = set(keywords)
        base_tokens.update(title_tokens[:5])
        # Add top frequent tokens from the extracted text (excluding very common words)
        tmp_ai = ai_assistant  # reuse stopwords if available
        stopwords = getattr(tmp_ai, '_stopwords', set())
        freq: Dict[str, int] = {}
        for tok in tokenize(extracted_text):
            if len(tok) <= 2 or tok in stopwords:
                continue
            freq[tok] = freq.get(tok, 0) + 1
        # pick top 10 tokens by frequency
        frequent = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        for tok, _ in frequent[:10]:
            base_tokens.add(tok)
        # Finalize keywords list, keep at most 25 to avoid bloat
        keywords = [k for k in list(base_tokens) if k]
        keywords = keywords[:25]
        if not keywords:
            return jsonify({'error': 'keywords is required (comma separated)'}), 400

        entry = {
            'id': str(uuid.uuid4()),
            'title': str(title),
            'keywords': keywords,
            'responses': responses,
            'created_at': datetime.now().isoformat(),
            'source_pdf': filename
        }
        entries = ai_assistant.admin_knowledge.copy()
        entries.append(entry)
        if not _save_admin_entries(entries):
            return jsonify({'error': 'Failed to save entry'}), 500
        ai_assistant.admin_knowledge = entries
        return jsonify({'entry': entry, 'status': 'success', 'extracted_preview': responses[0][:200]})
    except Exception as e:
        logger.error(f"Error uploading PDF knowledge: {e}")
        return jsonify({'error': 'Failed to upload PDF knowledge'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Cllg Chatbot API'
    })

@app.route('/api/stats')
def get_stats():
    """Get chatbot usage statistics"""
    try:
        conversation_count = len(ai_assistant.conversation_history) // 2  # Each conversation has user + bot message
        return jsonify({
            'total_conversations': conversation_count,
            'last_activity': ai_assistant.conversation_history[-1]['timestamp'] if ai_assistant.conversation_history else None,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    try:
        ai_assistant.conversation_history.clear()
        logger.info("Conversation history cleared")
        return jsonify({'message': 'History cleared successfully', 'status': 'success'})
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        return jsonify({'error': 'Failed to clear history'}), 500

# ------------------------------
# Locations API
# ------------------------------

@app.route('/api/locations', methods=['GET'])
def list_locations():
    try:
        return jsonify({'locations': locations_store, 'status': 'success'})
    except Exception as e:
        logger.error(f"Error listing locations: {e}")
        return jsonify({'error': 'Failed to list locations'}), 500

@app.route('/api/locations', methods=['POST'])
def add_location():
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        body = request.get_json() or {}
        name = str(body.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'name is required'}), 400
        category = str(body.get('category') or 'General')
        description = str(body.get('description') or '')
        maps_query = str(body.get('maps_query') or '')
        latitude = body.get('latitude')
        longitude = body.get('longitude')
        # sanitize lat/lng
        def to_float_or_none(v):
            try:
                return float(v)
            except Exception:
                return None
        latitude = to_float_or_none(latitude)
        longitude = to_float_or_none(longitude)

        entry = {
            'id': str(uuid.uuid4()),
            'name': name,
            'category': category,
            'description': description,
            'maps_query': maps_query,
            'latitude': latitude,
            'longitude': longitude,
            'created_at': datetime.now().isoformat()
        }
        tmp = list(locations_store)
        tmp.append(entry)
        if not _save_locations(tmp):
            return jsonify({'error': 'Failed to save location'}), 500
        locations_store.clear()
        locations_store.extend(tmp)
        return jsonify({'location': entry, 'status': 'success'})
    except Exception as e:
        logger.error(f"Error adding location: {e}")
        return jsonify({'error': 'Failed to add location'}), 500

@app.route('/api/locations/<loc_id>', methods=['PUT'])
def update_location(loc_id: str):
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        body = request.get_json() or {}
        tmp = list(locations_store)
        found = None
        for loc in tmp:
            if loc.get('id') == loc_id:
                found = loc
                break
        if not found:
            return jsonify({'error': 'Location not found'}), 404
        if 'name' in body and str(body.get('name') or '').strip():
            found['name'] = str(body['name']).strip()
        if 'category' in body and body.get('category') is not None:
            found['category'] = str(body['category'])
        if 'description' in body and body.get('description') is not None:
            found['description'] = str(body['description'])
        if 'maps_query' in body and body.get('maps_query') is not None:
            found['maps_query'] = str(body['maps_query'])
        if 'latitude' in body:
            try:
                found['latitude'] = float(body['latitude']) if body['latitude'] is not None else None
            except Exception:
                pass
        if 'longitude' in body:
            try:
                found['longitude'] = float(body['longitude']) if body['longitude'] is not None else None
            except Exception:
                pass
        if not _save_locations(tmp):
            return jsonify({'error': 'Failed to save location'}), 500
        locations_store.clear()
        locations_store.extend(tmp)
        return jsonify({'location': found, 'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        return jsonify({'error': 'Failed to update location'}), 500

@app.route('/api/locations/<loc_id>', methods=['DELETE'])
def delete_location(loc_id: str):
    if not _require_admin(request):
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        tmp = [l for l in locations_store if l.get('id') != loc_id]
        if len(tmp) == len(locations_store):
            return jsonify({'error': 'Location not found'}), 404
        if not _save_locations(tmp):
            return jsonify({'error': 'Failed to delete location'}), 500
        locations_store.clear()
        locations_store.extend(tmp)
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error deleting location: {e}")
        return jsonify({'error': 'Failed to delete location'}), 500

if __name__ == '__main__':
    print("🚀 Starting Cllg Chatbot Server...")
    print("📚 AI-Powered College Student Assistant")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔧 API endpoints:")
    print("   - POST /api/chat - Send messages")
    print("   - GET  /api/health - Health check")
    print("   - GET  /api/stats - Usage statistics")
    print("   - POST /api/clear-history - Clear chat history")
    print("\n" + "="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 