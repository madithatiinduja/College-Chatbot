# Cllg Chatbot Configuration File
# Modify these settings to customize the chatbot for your college

# College Information
COLLEGE_NAME = "Cllg College"
COLLEGE_WEBSITE = "https://www.cllgcollege.edu"
COLLEGE_EMAIL = "info@cllgcollege.edu"
COLLEGE_PHONE = "(555) 123-4567"

# Academic Calendar (Current Year)
ACADEMIC_YEAR = "2024-2025"

# Fall Semester Dates
FALL_SEMESTER = {
    "classes_begin": "August 26, 2024",
    "labor_day": "September 2, 2024",
    "fall_break": "October 14-15, 2024",
    "thanksgiving": "November 27-29, 2024",
    "finals_week": "December 16-20, 2024",
    "semester_ends": "December 20, 2024"
}

# Spring Semester Dates
SPRING_SEMESTER = {
    "classes_begin": "January 13, 2025",
    "mlk_day": "January 20, 2025",
    "spring_break": "March 10-14, 2025",
    "easter_break": "April 18-20, 2025",
    "finals_week": "May 5-9, 2025",
    "commencement": "May 10, 2025"
}

# Tuition and Fees
TUITION_FEES = {
    "full_time_tuition": 12500,
    "room_board": 8000,
    "books_supplies": 1200,
    "application_fee": 50,
    "total_annual": 46400
}

# Library Hours
LIBRARY_HOURS = {
    "monday_thursday": "7:00 AM - 11:00 PM",
    "friday": "7:00 AM - 8:00 PM",
    "saturday": "9:00 AM - 6:00 PM",
    "sunday": "12:00 PM - 11:00 PM"
}

# Campus Services Hours
CAMPUS_SERVICES = {
    "writing_center": "Monday-Friday, 9:00 AM - 5:00 PM",
    "math_lab": "Monday-Thursday, 10:00 AM - 8:00 PM",
    "health_center": "Monday-Friday, 8:00 AM - 5:00 PM",
    "fitness_center": "6:00 AM - 11:00 PM daily",
    "student_union": "7:00 AM - 12:00 AM daily",
    "career_services": "Monday-Friday, 9:00 AM - 5:00 PM"
}

# IT Support
IT_SUPPORT = {
    "help_desk_phone": "(555) 123-4567",
    "help_desk_email": "helpdesk@college.edu",
    "wifi_network": "College_Network",
    "free_printing_pages": 100
}

# Housing Information
HOUSING = {
    "traditional_dorms": 4500,
    "suite_style": 5200,
    "apartment_style": 6000,
    "deposit_amount": 200,
    "application_deadline": "May 1st",
    "move_in_date": "August 24th",
    "housing_office_phone": "(555) 123-4568",
    "housing_office_email": "housing@college.edu",
    "housing_office_location": "Student Center, Room 201"
}

# Parking and Transportation
PARKING = {
    "annual_permit": 300,
    "semester_permit": 180,
    "daily_parking": 5,
    "north_campus_spaces": 500,
    "south_campus_spaces": 300,
    "east_campus_spaces": 200,
    "visitor_spaces": 50,
    "shuttle_frequency": "Every 15 minutes",
    "shuttle_hours": "7:00 AM - 11:00 PM daily"
}

# Available Majors
MAJORS = {
    "arts_humanities": [
        "English Literature",
        "Creative Writing", 
        "History",
        "Philosophy",
        "Art History"
    ],
    "business_economics": [
        "Business Administration",
        "Marketing",
        "Finance",
        "Economics",
        "Entrepreneurship"
    ],
    "science_technology": [
        "Computer Science",
        "Biology",
        "Chemistry",
        "Physics",
        "Mathematics",
        "Engineering"
    ],
    "social_sciences": [
        "Psychology",
        "Sociology",
        "Political Science",
        "Anthropology",
        "Education"
    ],
    "health_sciences": [
        "Nursing",
        "Public Health",
        "Nutrition",
        "Exercise Science"
    ]
}

# Student Organizations
STUDENT_ORGANIZATIONS = {
    "academic": ["Math Club", "Science Society", "History Club", "Philosophy Club"],
    "cultural": ["International Student Association", "Cultural Heritage Club", "Language Exchange"],
    "service": ["Community Service Club", "Environmental Club", "Volunteer Corps"],
    "special_interest": ["Photography Club", "Gaming Club", "Music Club", "Art Club"]
}

# Chatbot Settings
CHATBOT_SETTINGS = {
    "welcome_message": "Hello! I'm your AI college assistant. I'm here to help you 24/7 with any questions about college life, academics, campus services, and more. How can I assist you today?",
    "typing_delay": 1000,  # milliseconds
    "max_message_length": 1000,
    "enable_quick_actions": True,
    "enable_chat_history": True,
    "max_history_items": 100
}

# API Settings
API_SETTINGS = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
    "enable_cors": True,
    "rate_limit": 100,  # requests per minute
    "timeout": 30  # seconds
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "chatbot.log",
    "max_size": "10MB",
    "backup_count": 5
}

# Feature Flags
FEATURES = {
    "enable_analytics": True,
    "enable_user_feedback": True,
    "enable_conversation_export": False,
    "enable_multi_language": False,
    "enable_voice_input": False
}

# Customization Notes:
# 1. Update college information above
# 2. Modify dates and times as needed
# 3. Adjust tuition amounts for your institution
# 4. Update contact information
# 5. Customize available majors and programs
# 6. Modify chatbot behavior settings
# 7. Adjust API and logging configurations

# To use these settings in your code:
# from config import COLLEGE_NAME, TUITION_FEES, etc. 