import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import with absolute path to avoid relative import issues
import gmail_chatbot
GmailChatbot = gmail_chatbot.GmailChatbot

# Configure Streamlit page
st.set_page_config(
    page_title="Gmail Q&A Chatbot",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, user-friendly styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        padding: 1rem 0;
    }
    
    /* Welcome Card */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Chat Container */
    .chat-container {
        background: #f8fafc;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        min-height: 400px;
        border: 1px solid #e2e8f0;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin: 0.8rem 0;
        max-width: 85%;
        font-size: 0.95rem;
        line-height: 1.5;
        animation: fadeIn 0.3s ease-in;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }
    
    .bot-message {
        background: white;
        color: #2d3748;
        border: 1px solid #e2e8f0;
        margin-right: auto;
        border-bottom-left-radius: 5px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Stats Cards */
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    /* Email Preview */
    .email-preview {
        background: linear-gradient(90deg, #f7fafc 0%, #edf2f7 100%);
        border-left: 4px solid #667eea;
        padding: 1rem 1.5rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .email-preview:hover {
        background: linear-gradient(90deg, #edf2f7 0%, #e2e8f0 100%);
        border-left-color: #764ba2;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 25px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Suggestion Buttons */
    .suggestion-btn {
        background: white;
        border: 2px solid #667eea;
        color: #667eea;
        padding: 0.8rem 1.2rem;
        border-radius: 25px;
        margin: 0.3rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        text-align: center;
        display: inline-block;
    }
    
    .suggestion-btn:hover {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Loading Indicator */
    .loading-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }
    
    /* Status Indicators */
    .status-success {
        color: #38a169;
        font-weight: 600;
    }
    
    .status-warning {
        color: #ed8936;
        font-weight: 600;
    }
    
    .status-error {
        color: #e53e3e;
        font-weight: 600;
    }
    
    /* Custom Scrollbar */
    .stVerticalBlock::-webkit-scrollbar {
        width: 8px;
    }
    
    .stVerticalBlock::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .stVerticalBlock::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_chatbot():
    """Initialize the Gmail chatbot and cache it"""
    return GmailChatbot()

@st.cache_data
def load_emails(_chatbot, max_emails=10):
    """Load and process emails with caching"""
    if _chatbot.fetch_and_process_emails(max_emails=max_emails):
        if _chatbot.build_index():
            if _chatbot.setup_chat_engine():
                return True, _chatbot.get_email_stats(), _chatbot.get_all_emails_summary()
    return False, None, None

def create_email_analytics(stats):
    """Create analytics visualizations for emails"""
    
    # Email categories analysis (mock data based on subjects)
    subjects = stats.get('all_subjects', [])
    categories = []
    
    for subject in subjects:
        subject_lower = subject.lower()
        if any(word in subject_lower for word in ['job', 'intern', 'career', 'linkedin']):
            categories.append('Work/Career')
        elif any(word in subject_lower for word in ['course', 'skill', 'learn', 'certificate']):
            categories.append('Education')
        elif any(word in subject_lower for word in ['patch', 'product', 'offer']):
            categories.append('Marketing')
        elif any(word in subject_lower for word in ['event', 'live', 'watch']):
            categories.append('Entertainment')
        else:
            categories.append('Other')
    
    # Create category distribution chart
    category_counts = pd.Series(categories).value_counts()
    
    fig_pie = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Email Categories Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Create timeline chart (mock data)
    timeline_data = pd.DataFrame({
        'Email': [f'Email #{i+1}' for i in range(len(subjects))],
        'Position': list(range(1, len(subjects) + 1)),
        'Category': categories
    })
    
    fig_timeline = px.bar(
        timeline_data,
        x='Email',
        y='Position',
        color='Category',
        title="Email Timeline (1 = Most Recent)",
        labels={'Position': 'Email Order'}
    )
    
    return fig_pie, fig_timeline

def main():
    # Header with welcome message
    st.markdown('<h1 class="main-header">📧 Gmail Q&A Chatbot</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
        st.session_state.emails_loaded = False
        st.session_state.chat_history = []
        st.session_state.stats = None
        st.session_state.email_summary = None
    
    # Welcome card for new users
    if not st.session_state.emails_loaded:
        st.markdown("""
        <div class="welcome-card fade-in">
            <h2>🎉 Welcome to Your Personal Email Assistant!</h2>
            <p style="font-size: 1.1rem; margin: 1rem 0;">
                Connect your Gmail and start having intelligent conversations about your emails. 
                Ask questions, get summaries, and discover insights from your inbox!
            </p>
            <p style="font-size: 0.9rem; opacity: 0.9;">
                👈 Get started by clicking "Load Gmail Data" in the sidebar
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar with improved design
    with st.sidebar:
        st.markdown("### 🔧 **Setup & Controls**")
        st.markdown("---")
        
        # Email loading section with better spacing
        st.markdown("#### 📥 **Email Configuration**")
        
        # Number of emails slider with description
        max_emails = st.slider(
            "Number of emails to process", 
            min_value=5, 
            max_value=20, 
            value=10,
            help="Choose how many recent emails to analyze. More emails = better insights but slower processing."
        )
        
        # Better load button with status feedback
        load_col1, load_col2 = st.columns([3, 1])
        with load_col1:
            if st.button("🔄 **Load Gmail Data**", type="primary", use_container_width=True):
                with st.spinner("🤖 Initializing AI assistant..."):
                    st.session_state.chatbot = initialize_chatbot()
                
                with st.spinner("📧 Fetching and analyzing your emails..."):
                    success, stats, summary = load_emails(st.session_state.chatbot, max_emails)
                    
                    if success:
                        st.session_state.emails_loaded = True
                        st.session_state.stats = stats
                        st.session_state.email_summary = summary
                        st.balloons()  # Celebrate success!
                        st.success(f"🎉 Successfully loaded {stats['total_emails']} emails!")
                    else:
                        st.error("❌ Failed to load emails. Please check your Gmail setup and try again.")
        
        st.markdown("---")
        
        # Status section with better visual indicators
        st.markdown("#### 📊 **Status**")
        if st.session_state.emails_loaded:
            st.markdown(f"""
            <div class="stats-card">
                <div class="status-success">✅ Chatbot Ready</div>
                <div style="margin-top: 0.5rem;">
                    📧 <strong>{st.session_state.stats['total_emails']}</strong> emails loaded<br>
                    🧠 AI assistant is ready to chat
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="stats-card">
                <div class="status-warning">⚠️ Setup Required</div>
                <div style="margin-top: 0.5rem; color: #666;">
                    Load your emails above to start chatting with your AI assistant
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Action buttons section
        st.markdown("#### ⚡ **Quick Actions**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.success("Chat cleared!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Debug section (can be removed later)
        if st.session_state.emails_loaded:
            with st.expander("🔧 Debug Info"):
                st.write(f"Chat history length: {len(st.session_state.chat_history)}")
                if st.session_state.chat_history:
                    st.write("Last message:")
                    st.json(st.session_state.chat_history[-1])
                
                if st.button("Test Simple Query"):
                    try:
                        test_response = st.session_state.chatbot.chat("How many emails total?")
                        st.write(f"Test response: {test_response}")
                    except Exception as e:
                        st.error(f"Test failed: {e}")
        
        # Help section
        st.markdown("---")
        st.markdown("#### ❓ **Need Help?**")
        with st.expander("📖 How to use"):
            st.markdown("""
            **Getting Started:**
            1. Click "Load Gmail Data" above
            2. Wait for your emails to be processed
            3. Start asking questions in the chat!
            
            **Example Questions:**
            - "What's my most recent email?"
            - "Show me work-related emails"
            - "How many emails about courses?"
            - "Summarize today's emails"
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; font-size: 0.8rem; color: #666;">
            🚀 Powered by AI<br>
            Your data stays private
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area with improved layout
    if st.session_state.emails_loaded:
        col1, col2 = st.columns([2.5, 1.5])
    else:
        col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💬 **Chat with Your Emails**")
        
        if not st.session_state.emails_loaded:
            # Show welcome message without the container box
            st.markdown("""
            <div style="text-align: center; padding: 3rem 2rem; color: #666;">
                <h3 style="color: #667eea; margin-bottom: 1rem;">🤖 Your AI Assistant is Ready!</h3>
                <p style="font-size: 1.1rem; margin-bottom: 2rem;">
                    Connect your Gmail from the sidebar to start having intelligent conversations about your emails.
                </p>
                <div style="margin-top: 2rem;">
                    <p style="font-size: 0.9rem; color: #888; margin-bottom: 1rem;">
                        👈 Click "Load Gmail Data" in the sidebar to get started
                    </p>
                    <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                        <div style="background: #f0f2ff; color: #667eea; padding: 0.8rem 1.2rem; border-radius: 20px; font-size: 0.9rem;">
                            💼 Work emails analysis
                        </div>
                        <div style="background: #f0f2ff; color: #667eea; padding: 0.8rem 1.2rem; border-radius: 20px; font-size: 0.9rem;">
                            📚 Learning opportunities
                        </div>
                        <div style="background: #f0f2ff; color: #667eea; padding: 0.8rem 1.2rem; border-radius: 20px; font-size: 0.9rem;">
                            📊 Smart summaries
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display chat history with improved styling and better handling
            if st.session_state.chat_history:
                for i, message in enumerate(st.session_state.chat_history):
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-message user-message fade-in">
                            <strong>You:</strong> {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Ensure the assistant message content is properly handled
                        content = message.get("content", "I'm sorry, I didn't respond properly. Please try asking again!")
                        if not content or content.strip() == "":
                            content = "I apologize, but my response didn't come through properly. Could you please ask your question again?"
                        
                        st.markdown(f"""
                        <div class="chat-message bot-message fade-in">
                            <strong>🤖 Assistant:</strong> {content}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; color: #666;">
                    <h4>👋 Hello! I'm your email assistant</h4>
                    <p>Ask me anything about your emails. I'm here to help!</p>
                    <p style="font-size: 0.9rem; color: #888;">Try asking: "What is my most recent email?" or "Summarize my emails"</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Chat input with placeholder
            query = st.chat_input("💭 Ask me about your emails... (e.g., 'What's my most recent email?')")
            
            if query:
                # Add user message to history
                st.session_state.chat_history.append({"role": "user", "content": query})
                
                # Get response from chatbot with better feedback
                with st.spinner("🤔 Analyzing your emails..."):
                    try:
                        response = st.session_state.chatbot.chat(query)
                        
                        # Ensure response is not empty
                        if response and response.strip():
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                        else:
                            fallback_msg = "I'm sorry, I couldn't generate a proper response to your question. Could you please try asking in a different way? For example, try asking 'What is my most recent email?' or 'Show me a summary of my emails.'"
                            st.session_state.chat_history.append({"role": "assistant", "content": fallback_msg})
                            
                    except Exception as e:
                        error_msg = f"I apologize, but I encountered an issue while processing your request. This might be due to API limits or a temporary connection issue. Please try again in a moment, or try asking a simpler question like 'What emails did I receive?'"
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                        st.error(f"Technical details: {str(e)}")
                
                st.rerun()
            
            # Suggested questions with better design
            st.markdown("---")
            st.markdown("### 💡 **Quick Questions to Try**")
            
            suggestions = [
                ("📧 Recent Email", "What is my most recent email?"),
                ("💼 Work Emails", "How many work-related emails did I receive?"),
                ("🎯 Job Opportunities", "Show me all job opportunities"),
                ("📚 Learning Content", "What emails are about courses or learning?"),
                ("📊 Email Summary", "Summarize all my emails"),
                ("⏰ Oldest Email", "What is the oldest email?")
            ]
            
            # Create 3 columns for suggestions
            cols = st.columns(3)
            for i, (label, suggestion) in enumerate(suggestions):
                with cols[i % 3]:
                    if st.button(label, key=f"suggestion_{i}", use_container_width=True):
                        # Trigger the suggestion as if user typed it
                        st.session_state.chat_history.append({"role": "user", "content": suggestion})
                        with st.spinner("🤔 Analyzing..."):
                            response = st.session_state.chatbot.chat(suggestion)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
    
    with col2:
        st.markdown("### 📊 **Email Overview**")
        
        if st.session_state.emails_loaded:
            # Quick stats with better design
            stats = st.session_state.stats
            
            st.markdown(f"""
            <div class="stats-card fade-in">
                <h4>📈 Quick Stats</h4>
                <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.8rem; font-weight: bold; color: #667eea;">{stats['total_emails']}</div>
                        <div style="font-size: 0.8rem; color: #666;">Total Emails</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.8rem; font-weight: bold; color: #764ba2;">🤖</div>
                        <div style="font-size: 0.8rem; color: #666;">AI Ready</div>
                    </div>
                </div>
                <div style="font-size: 0.8rem; color: #888; text-align: center;">
                    Processed: {datetime.now().strftime('%m/%d %H:%M')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recent emails preview with better styling
            st.markdown("#### 📋 **Recent Emails**")
            recent_subjects = stats['subjects'][:5]
            for i, subject in enumerate(recent_subjects, 1):
                # Truncate long subjects nicely
                display_subject = subject[:40] + "..." if len(subject) > 40 else subject
                st.markdown(f"""
                <div class="email-preview">
                    <div style="display: flex; align-items: center;">
                        <div style="background: #667eea; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 0.8rem; font-size: 0.8rem; font-weight: bold;">
                            {i}
                        </div>
                        <div style="flex: 1;">
                            <div style="font-weight: 500; font-size: 0.9rem;">{display_subject}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Analytics with improved layout
            if len(stats['all_subjects']) > 0:
                st.markdown("---")
                st.markdown("#### 📈 **Email Analytics**")
                
                # Create tabs for better organization
                tab1, tab2 = st.tabs(["📊 Categories", "📅 Timeline"])
                
                with tab1:
                    fig_pie, fig_timeline = create_email_analytics(stats)
                    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
                
                with tab2:
                    st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})
            
            # Detailed email list with better presentation
            st.markdown("---")
            with st.expander("📝 **View All Email Details**", expanded=False):
                # Format the email summary better
                st.markdown("**Complete Email List:**")
                if st.session_state.email_summary:
                    # Split and format the summary
                    lines = st.session_state.email_summary.split('\n')
                    formatted_summary = ""
                    for line in lines:
                        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                            formatted_summary += f"\n**{line}**\n"
                        elif line.strip().startswith('Email ID:'):
                            formatted_summary += f"*{line}*\n"
                        else:
                            formatted_summary += f"{line}\n"
                    st.markdown(formatted_summary)
        else:
            # Better placeholder when no emails loaded
            st.markdown("""
            <div class="stats-card">
                <div style="text-align: center; padding: 2rem; color: #666;">
                    <h4>📊 Email Insights Await</h4>
                    <p style="margin: 1rem 0;">Once you load your emails, you'll see:</p>
                    <div style="text-align: left; margin: 1rem 0;">
                        <div>📈 Email statistics & counts</div>
                        <div>📋 Recent email previews</div>
                        <div>📊 Category breakdowns</div>
                        <div>📅 Timeline analysis</div>
                    </div>
                    <p style="font-size: 0.9rem; color: #888;">Load your Gmail data to get started!</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer with better styling
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 2rem 1rem; margin-top: 2rem;">
        <div style="margin-bottom: 0.5rem;">
            🚀 Powered by <strong>LlamaIndex</strong> + <strong>Gemini AI</strong> + <strong>Streamlit</strong>
        </div>
        <div style="font-size: 0.9rem;">
            Made with ❤️ for intelligent email management
        </div>
        <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.7;">
            Your email data is processed securely and stays private
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
