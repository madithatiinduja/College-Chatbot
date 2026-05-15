# 🎓 Cllg Chatbot - AI-Powered College Student Assistant

A modern, intelligent chatbot designed to provide 24/7 assistance to college students with their inquiries about campus life, academics, and student services.

## ✨ Features

### 🤖 AI-Powered Responses
- **Intelligent Understanding**: Advanced keyword matching and context awareness
- **Comprehensive Knowledge Base**: Covers all major college topics
- **Natural Language Processing**: Understands various ways students ask questions
- **24/7 Availability**: Always ready to help, day or night

### 🎯 Student Support Areas
- **Admissions & Applications**: Requirements, deadlines, application process
- **Academic Programs**: Course information, majors, curriculum details
- **Financial Aid**: Scholarships, costs, payment options
- **Campus Services**: Library hours, health services, IT support
- **Student Life**: Clubs, activities, events, organizations
- **Academic Calendar**: Important dates, deadlines, breaks
- **Technical Support**: WiFi, software, computer labs

### 💻 Modern Web Interface
- **Responsive Design**: Works perfectly on all devices
- **Beautiful UI**: Modern gradient design with smooth animations
- **Real-time Chat**: Instant messaging with typing indicators
- **Quick Actions**: Pre-built buttons for common questions
- **Chat History**: Persistent storage of conversations

## 🚀 Deployment

### 🌐 Live Link
**[View the Live Demo here!](https://college-chatbot.onrender.com)** *(Replace this with your actual Render URL)*

### 📁 Repository
**[GitHub Repository](https://github.com/madithatiinduja/College-Chatbot)**

### ☁️ Hosting on Render (Full App)
This project is fully configured for [Render](https://render.com/).

1. **Connect GitHub**: Connect your repository to a new Render Web Service.
2. **Settings**:
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
3. **Environment Variables**:
   - `ADMIN_TOKEN`: Your secret admin code (default: `changeme`).
   - `FLASK_SECRET_KEY`: A secure random string.

## �️ Installation & Local Setup

### Frontend (HTML/CSS/JavaScript)
- **HTML5**: Semantic structure and accessibility
- **CSS3**: Modern styling with gradients and animations
- **JavaScript ES6+**: Object-oriented chatbot implementation
- **Responsive Design**: Mobile-first approach
- **Local Storage**: Chat history persistence

### Backend (Python Flask)
- **Flask Framework**: Lightweight web server
- **RESTful API**: Clean endpoint design
- **AI Engine**: Intelligent response generation
- **CORS Support**: Cross-origin resource sharing
- **Logging**: Comprehensive activity tracking

### AI Intelligence
- **Knowledge Base**: Structured college information
- **Keyword Matching**: Smart content categorization
- **Response Variety**: Multiple responses per topic
- **Context Awareness**: Follow-up question handling
- **Fallback Logic**: Graceful handling of unknown queries

## 🔧 Configuration

### Customizing Responses
Edit the `knowledge_base` in `app.py` to modify:
- Response content
- Keyword matching
- Topic categories
- College-specific information

### Styling Changes
Modify `styles.css` to customize:
- Color schemes
- Layout dimensions
- Animation effects
- Typography

### Adding New Features
Extend the JavaScript in `script.js` for:
- New chat features
- Additional UI elements
- Enhanced interactions
- Third-party integrations

## 📱 Usage Examples

### Common Student Questions
```
User: "What are the admission requirements?"
Bot: [Detailed admission information with deadlines]

User: "How much does college cost?"
Bot: [Comprehensive cost breakdown with financial aid options]

User: "What clubs are available?"
Bot: [List of student organizations and activities]

User: "When is spring break?"
Bot: [Academic calendar information]
```

### Quick Action Buttons
- **Admission Requirements**: One-click access to application info
- **Available Courses**: Browse academic programs
- **Financial Aid**: Learn about costs and scholarships
- **Library Hours**: Check study space availability

## 🔒 Security Features

- **Input Validation**: Sanitized user inputs
- **CORS Protection**: Controlled cross-origin access
- **Error Handling**: Graceful failure management
- **Rate Limiting**: Built-in request throttling
- **Logging**: Comprehensive activity monitoring

## 📊 Analytics & Monitoring

### Built-in Statistics
- Total conversation count
- Last activity timestamp
- API health monitoring
- Error tracking and logging

### API Endpoints
```
GET  /api/health      - Server health check
GET  /api/stats       - Usage statistics
POST /api/chat        - Send messages
POST /api/clear-history - Clear chat history
```

## 🧪 Testing

### Manual Testing
1. Open the chatbot interface
2. Test various question types
3. Verify response accuracy
4. Check mobile responsiveness

### Automated Testing
```bash
# Run Python tests (if implemented)
python -m pytest tests/

# Check code quality
flake8 app.py
pylint app.py
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- **Python**: PEP 8 compliance
- **JavaScript**: ES6+ standards
- **CSS**: BEM methodology
- **HTML**: Semantic markup

## 📚 Learning Resources

### Technologies Used
- **Flask**: [Official Documentation](https://flask.palletsprojects.com/)
- **JavaScript**: [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- **CSS3**: [CSS-Tricks](https://css-tricks.com/)
- **HTML5**: [W3Schools](https://www.w3schools.com/html/)

### AI & Chatbot Concepts
- Natural Language Processing
- Intent Recognition
- Response Generation
- Conversation Flow

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
- Check Python version (3.7+ required)
- Verify all dependencies installed
- Check port 5000 availability

**Chatbot not responding:**
- Check browser console for errors
- Verify backend server is running
- Check network connectivity

**Styling issues:**
- Clear browser cache
- Check CSS file loading
- Verify font-awesome CDN access

### Debug Mode
Enable debug mode in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Flask Community**: For the excellent web framework
- **Font Awesome**: For beautiful icons
- **Google Fonts**: For typography
- **Open Source Community**: For inspiration and tools

## 📞 Support

For questions, issues, or contributions:
- **Issues**: Use GitHub issue tracker
- **Discussions**: Start a GitHub discussion
- **Email**: Contact the development team

---

**Made with ❤️ for college students everywhere**

*Empowering education through intelligent assistance* 