#!/usr/bin/env python3
"""
Demo script for Gmail Q&A Chatbot
Run this to see the chatbot in action with sample queries
"""

from gmail_chatbot import GmailChatbot

def main():
    print("🤖 Gmail Q&A Chatbot Demo")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = GmailChatbot()
    
    # Setup process
    print("\n1️⃣ Setting up Gmail Chatbot...")
    
    if not chatbot.fetch_and_process_emails(max_emails=5):
        print("❌ Failed to fetch emails. Please check your Gmail setup.")
        return
    
    if not chatbot.build_index():
        print("❌ Failed to build index.")
        return
        
    if not chatbot.setup_chat_engine():
        print("❌ Failed to setup chat engine.")
        return
    
    # Show stats
    stats = chatbot.get_email_stats()
    print(f"\n📊 Email Stats:")
    print(f"  • Total emails processed: {stats['total_emails']}")
    print(f"  • Recent subjects: {', '.join(stats['subjects'][:3])}...")
    
    # Demo queries
    demo_queries = [
        "What emails did I receive today?",
        "Are there any urgent emails?",
        "Tell me about work-related emails",
        "What are the main topics in my emails?",
        "Any emails about deadlines or meetings?"
    ]
    
    print("\n💬 Demo Questions & Answers:")
    print("=" * 50)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. 🤔 {query}")
        print("🤖 Assistant:", end=" ")
        
        try:
            response = chatbot.chat(query)
            # Limit response length for demo
            if len(response) > 200:
                response = response[:200] + "..."
            print(response)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n✅ Demo completed! The chatbot successfully:")
    print(f"  • Processed {stats['total_emails']} emails")
    print(f"  • Built a searchable knowledge base")
    print(f"  • Answered questions about email content")
    print(f"  • Used AI to understand context and provide relevant answers")
    
    print(f"\n🚀 To use interactively, run: python -m src.gmail_chatbot")

if __name__ == "__main__":
    main()
