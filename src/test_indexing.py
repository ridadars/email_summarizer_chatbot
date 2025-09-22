#!/usr/bin/env python3
"""
Test script to verify email indexing is working correctly
"""

from .gmail_chatbot import GmailChatbot

def test_email_indexing():
    print("🔧 Testing Email Indexing System")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = GmailChatbot()
    
    # Setup
    print("\n1️⃣ Setting up...")
    if not chatbot.fetch_and_process_emails(max_emails=10):
        print("❌ Failed to fetch emails")
        return
    
    if not chatbot.build_index():
        print("❌ Failed to build index")
        return
        
    if not chatbot.setup_chat_engine():
        print("❌ Failed to setup chat engine")
        return
    
    print(f"✅ Successfully indexed {len(chatbot.documents)} emails")
    
    # Test queries
    test_queries = [
        "What is the most recent email?",
        "What is the last email I received?", 
        "How many emails total?",
        "List all email subjects",
        "What is email #1?",
        "What is the oldest email?",
        "Show me email #10"
    ]
    
    print("\n2️⃣ Testing Queries:")
    print("-" * 30)
    
    for query in test_queries:
        print(f"\n🤔 Query: {query}")
        try:
            response = chatbot.chat(query)
            # Limit response for readability
            if len(response) > 200:
                response = response[:200] + "..."
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Show document metadata
    print(f"\n3️⃣ Document Metadata Check:")
    print("-" * 30)
    for i, doc in enumerate(chatbot.documents[:3]):  # Show first 3
        print(f"Document {i+1}:")
        print(f"  Subject: {doc.metadata.get('subject', 'Unknown')}")
        print(f"  Position: {doc.metadata.get('email_position', 'Unknown')}")
        print(f"  Is Most Recent: {doc.metadata.get('is_most_recent', False)}")
        print(f"  Total Emails: {doc.metadata.get('total_emails', 'Unknown')}")
        print()

if __name__ == "__main__":
    test_email_indexing()
