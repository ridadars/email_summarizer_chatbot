# 🤖 Gmail Q&A Chatbot

> **An intelligent AI-powered assistant that transforms your Gmail into an interactive, conversational experience.**

Transform the way you interact with your email! This modern web application connects to your Gmail account, analyzes your emails using cutting-edge AI, and provides an intuitive chat interface where you can ask questions about your email content in natural language.

![Gmail Q&A Chatbot](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![AI](https://img.shields.io/badge/AI-Gemini%20%2B%20LlamaIndex-purple) ![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🎯 **Core Capabilities**
- **🔗 Gmail Integration**: Securely connects to your Gmail account using OAuth2
- **🧠 AI Analysis**: Powered by Google Gemini for intelligent email understanding
- **💬 Natural Conversations**: Chat with your emails using everyday language
- **🔍 Smart Search**: LlamaIndex-powered semantic search across all your emails
- **📊 Visual Analytics**: Beautiful charts and insights about your email patterns

### 🎨 **Modern Web Interface**
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices
- **🎨 Professional UI**: Clean, modern interface with smooth animations
- **⚡ Real-time Chat**: WhatsApp-style chat interface with instant responses
- **📈 Interactive Charts**: Email category breakdowns and timeline analysis
- **🎯 Quick Actions**: Pre-built question suggestions for instant insights

### 🔐 **Privacy & Security**
- **🔒 Secure Authentication**: OAuth2 implementation for Gmail access
- **🛡️ Data Privacy**: No permanent storage of email content
- **🔐 Local Processing**: All data processing happens locally on your machine
- **✅ Trusted APIs**: Uses official Google and AI service APIs

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** installed on your system
- **Gmail account** with API access enabled
- **Google API credentials** (we'll help you set this up)

### 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd week5-agent-solution
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Gmail API credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth2 credentials
   - Download credentials as `credentials.json` and place in project root

### 🎯 Launch the Application

**Option 1: Easy Launcher**
```bash
python run_web_app.py
```

**Option 2: Direct Streamlit**
```bash
streamlit run src/streamlit_app.py --server.port 8501
```

**Option 3: Command Line Interface**
```bash
python -m src.gmail_chatbot
```

Then open your browser and navigate to: **http://localhost:8501**

## 📖 How to Use

### 1. **First Time Setup**
1. 📂 Launch the web application
2. 👆 Click "**Load Gmail Data**" in the sidebar
3. 🔐 Authenticate with your Google account (first time only)
4. ⚙️ Choose how many emails to analyze (5-20)
5. ⏳ Wait for processing to complete
6. 🎉 Start chatting with your emails!

### 2. **Chatting with Your Emails**
Once your emails are loaded, you can ask questions like:

#### 📧 **Email Discovery**
- *"What is my most recent email?"*
- *"Show me emails from last week"*
- *"What's in my inbox today?"*

#### 🔍 **Smart Filtering**
- *"Find all work-related emails"*
- *"Show me emails about job opportunities"*
- *"What emails mention courses or learning?"*

#### 📊 **Insights & Analysis**
- *"How many emails did I receive today?"*
- *"Summarize my important emails"*
- *"What are the main topics in my inbox?"*

#### ⚡ **Quick Actions**
- *"Any urgent emails I should know about?"*
- *"Show me LinkedIn invitations"*
- *"Find emails with attachments"*

### 3. **Using the Interface**

#### 🎛️ **Sidebar Controls**
- **📥 Email Configuration**: Set number of emails to process
- **📊 Status Indicators**: See connection and processing status
- **⚡ Quick Actions**: Clear chat, refresh data
- **❓ Help Section**: Built-in usage guide

#### 💬 **Chat Area**
- **Chat Input**: Type questions naturally
- **Suggested Questions**: Click pre-made questions for instant results
- **Message History**: Scroll through your conversation
- **Loading Indicators**: See when AI is processing

#### 📈 **Analytics Panel**
- **Quick Stats**: Email counts and processing time
- **Recent Emails**: Preview of latest messages
- **Category Charts**: Visual breakdown by email type
- **Timeline View**: Email activity over time

## 🔧 Advanced Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Google Gemini Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-flash
TEMPERATURE=0.2

# Optional: Custom settings
MAX_EMAILS=20
CACHE_TIMEOUT=3600
```

### Custom Email Processing
Modify email processing in `src/gmail_chatbot.py`:

```python
# Adjust email filtering
max_emails = 50  # Process more emails

# Customize AI analysis
custom_prompt = "Analyze this email for sentiment and priority..."
```

## 🏗️ Architecture

### 🧩 **Core Components**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit + Custom CSS | Modern web interface |
| **AI Engine** | Google Gemini via LangChain | Email analysis and chat |
| **Search** | LlamaIndex | Semantic email search |
| **Email API** | Gmail API + OAuth2 | Secure email access |
| **Visualization** | Plotly | Interactive charts |

### 📁 **Project Structure**
```
week5-agent-solution/
├── 📁 src/
│   ├── 🤖 gmail_chatbot.py      # Main chatbot logic
│   ├── 🌐 streamlit_app.py      # Web interface
│   ├── 📧 gmail_summarizer.py   # Email processing
│   └── 🔧 agent.py              # AI configuration
├── 📋 requirements.txt          # Dependencies
├── 🚀 run_web_app.py           # Easy launcher
├── 📖 README.md                # This file
└── 🔐 .env                     # Configuration (create this)
```

## 🎨 Screenshots & Examples

### 🖥️ **Main Interface**
- Clean, professional design with gradient colors
- Intuitive sidebar for controls and status
- WhatsApp-style chat bubbles for conversations
- Interactive analytics panel with charts

### 💬 **Chat Examples**
```
You: What's my most recent email?
🤖 Assistant: Your most recent email is from HR Ways about a "Junior Buyer (REMOTE)" position. It's a job opportunity email that highlights remote work and includes application details.

You: How many work emails did I get?
🤖 Assistant: I found 3 work-related emails in your recent messages:
• Junior Buyer position from HR Ways
• LinkedIn invitation from a professional contact
• Competition announcement from MABe Challenge
```

## 🐛 Troubleshooting

### Common Issues

**🔐 Authentication Problems**
```bash
# Clear stored credentials
rm token.pickle
# Re-run the application
```

**⚠️ API Limits**
- Gemini free tier: 15 requests/minute
- Solution: Wait or upgrade to paid plan

**📧 No Emails Loading**
- Check Gmail API is enabled
- Verify credentials.json is in root directory
- Ensure internet connection

**💬 Empty Chat Responses**
- Check API key in .env file
- Try asking simpler questions
- Use the debug panel in sidebar

### 🆘 **Getting Help**

1. **Check the built-in help** in the sidebar
2. **Use the debug panel** to see technical details
3. **Try the command line version** for more detailed error messages
4. **Check terminal output** for specific error messages

## 🔄 Updates & Maintenance

### Keeping Up to Date
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Clear cache if needed
rm -rf __pycache__ src/__pycache__
```

### Performance Tips
- **Limit email count** for faster processing
- **Use specific questions** for better responses
- **Clear chat history** periodically
- **Restart app** if experiencing slowdowns

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🐛 Report Bugs**: Open an issue with details
2. **💡 Suggest Features**: Share your ideas
3. **🔧 Submit Pull Requests**: Improve the code
4. **📖 Improve Documentation**: Help others understand

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Run tests
pytest tests/

# Format code
black src/
```

### Output
<img width="1438" height="749" alt="Screenshot 2025-09-23 at 12 12 07 AM" src="https://github.com/user-attachments/assets/e830aceb-ec1d-4404-b8aa-963eba9e4ca8" />
<img width="1436" height="744" alt="Screenshot 2025-09-23 at 12 13 52 AM" src="https://github.com/user-attachments/assets/0e96be79-749c-43b0-a927-96fdcafe640e" />
<img width="1433" height="741" alt="Screenshot 2025-09-23 at 12 13 59 AM" src="https://github.com/user-attachments/assets/ac07d064-1391-4d8b-9ca3-e247a56bbdff" />


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with love using these amazing technologies:
- **🚀 Streamlit** - For the beautiful web interface
- **🧠 Google Gemini** - For AI-powered email analysis
- **🔍 LlamaIndex** - For semantic search capabilities
- **📧 Gmail API** - For secure email access
- **📊 Plotly** - For interactive visualizations

---

<div align="center">

**🌟 Star this repo if you found it helpful!**

**Made with ❤️ for smarter email management**

*Transform your inbox into an intelligent assistant today!*

</div>
