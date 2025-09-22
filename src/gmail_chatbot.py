import os
import json
import email.header
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from llama_index.core import Document, VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms.callbacks import llm_completion_callback
from typing import List, Any, Optional

# Import our Gmail functionality
try:
    from .gmail_summarizer import get_gmail_service, get_email_content, analyze_with_gemini, get_llm
except ImportError:
    # Fallback for when running as script
    from gmail_summarizer import get_gmail_service, get_email_content, analyze_with_gemini, get_llm

load_dotenv()

def decode_email_subject(subject):
    """Decode email subject from encoded format to readable text"""
    if not subject:
        return "No Subject"
    
    try:
        # Handle multiple encoded parts
        decoded_parts = email.header.decode_header(subject)
        decoded_subject = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_subject += part.decode(encoding)
                else:
                    decoded_subject += part.decode('utf-8', errors='ignore')
            else:
                decoded_subject += part
        
        # Clean up any remaining encoded artifacts
        decoded_subject = re.sub(r'=\?[^?]+\?[QB]\?[^?]+\?=', '', decoded_subject)
        decoded_subject = decoded_subject.strip()
        
        return decoded_subject if decoded_subject else "No Subject"
        
    except Exception as e:
        # Fallback: try basic cleanup
        cleaned = re.sub(r'=\?[^?]+\?[QB]\?[^?]+\?=', '', subject)
        return cleaned.strip() if cleaned.strip() else "No Subject"

class GeminiLLMWrapper(CustomLLM):
    """Wrapper to make Langchain's Gemini compatible with LlamaIndex"""
    
    context_window: int = 4096
    num_output: int = 256
    model_name: str = "gemini-1.5-flash"
    
    def __init__(self):
        super().__init__()
        self._llm = get_llm()
    
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )
    
    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        response = self._llm.invoke(prompt)
        text = response.content if hasattr(response, 'content') else str(response)
        return CompletionResponse(text=text)
    
    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs):
        # For streaming, we'll just return the complete response
        response = self.complete(prompt, **kwargs)
        yield response

class SimpleEmbedding(BaseEmbedding):
    """Simple embedding class for demonstration"""
    
    def __init__(self):
        super().__init__()
    
    def _get_embedding(self, text: str) -> List[float]:
        # Simple hash-based embedding for demo purposes
        # In production, you'd use proper embeddings like OpenAI or Hugging Face
        embedding_dim = 384  # Standard embedding dimension
        text_hash = hash(text)
        return [float((text_hash + i) % 1000) / 1000 for i in range(embedding_dim)]
    
    def _get_text_embedding(self, text: str) -> List[float]:
        return self._get_embedding(text)
    
    def _get_query_embedding(self, query: str) -> List[float]:
        return self._get_embedding(query)
    
    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

class GmailChatbot:
    def __init__(self):
        self.llm_wrapper = GeminiLLMWrapper()
        self.embedding = SimpleEmbedding()
        
        # Configure LlamaIndex settings
        Settings.llm = self.llm_wrapper
        Settings.embed_model = self.embedding
        
        self.documents = []
        self.index = None
        self.chat_engine = None
        self.gmail_service = None
        
    def fetch_and_process_emails(self, max_emails: int = 20):
        """Fetch emails and create documents for indexing"""
        print("🔄 Fetching emails...")
        
        try:
            self.gmail_service = get_gmail_service()
            llm = get_llm()
            
            # Get recent emails
            results = self.gmail_service.users().messages().list(
                userId="me", 
                maxResults=max_emails
            ).execute()
            messages = results.get("messages", [])
            
            print(f"📧 Processing {len(messages)} emails...")
            
            for i, msg in enumerate(messages):
                try:
                    subject, body = get_email_content(self.gmail_service, msg["id"])
                    # Decode the subject to make it readable
                    clean_subject = decode_email_subject(subject)
                    analysis = analyze_with_gemini(llm, clean_subject, body)
                    
                    # Create document with email content and analysis
                    doc_text = f"""
Email #{i+1} of {len(messages)}
Subject: {clean_subject}
Email ID: {msg["id"]}

Email Content:
{body[:1000]}...

AI Analysis:
{analysis}

Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Email Position: {i+1} out of {len(messages)} (1 = most recent, {len(messages)} = oldest)
"""
                    
                    document = Document(
                        text=doc_text,
                        metadata={
                            "subject": clean_subject,
                            "raw_subject": subject,  # Keep original for reference
                            "email_id": msg["id"],
                            "analysis": analysis,
                            "processed_date": datetime.now().isoformat(),
                            "email_position": i+1,
                            "total_emails": len(messages),
                            "is_most_recent": i == 0,
                            "is_oldest": i == len(messages) - 1
                        }
                    )
                    
                    self.documents.append(document)
                    print(f"✅ Processed email {i+1}/{len(messages)}: {clean_subject[:50]}...")
                    
                except Exception as e:
                    print(f"⚠️ Error processing email {i+1}: {str(e)}")
                    continue
            
            print(f"✅ Successfully processed {len(self.documents)} emails")
            
        except Exception as e:
            print(f"❌ Error fetching emails: {str(e)}")
            return False
            
        return True
    
    def build_index(self):
        """Build the vector index from documents"""
        if not self.documents:
            print("❌ No documents to index. Please fetch emails first.")
            return False
            
        print("🔄 Building knowledge index...")
        
        try:
            # Create index from documents
            self.index = VectorStoreIndex.from_documents(self.documents)
            print("✅ Index built successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error building index: {str(e)}")
            return False
    
    def setup_chat_engine(self):
        """Setup the chat engine for Q&A"""
        if not self.index:
            print("❌ No index available. Please build index first.")
            return False
            
        try:
            # Create chat engine with memory
            memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
            
            self.chat_engine = self.index.as_chat_engine(
                chat_mode="best",  # Use best retrieval mode
                memory=memory,
                similarity_top_k=len(self.documents),  # Retrieve ALL documents
                response_mode="tree_summarize",  # Better for multiple documents
                system_prompt="""You are a friendly, helpful AI assistant that specializes in helping users understand and manage their Gmail emails. You should communicate in a warm, conversational, and professional manner.

PERSONALITY & TONE:
- Be friendly, warm, and conversational
- Use natural language, not technical jargon
- Show enthusiasm when helping
- Be empathetic and understanding
- Use emojis sparingly but appropriately
- Address the user directly and personally

EMAIL INFORMATION CONTEXT:
- You have access to {} processed emails
- Email #1 is the MOST RECENT email
- Email #{} is the OLDEST email
- When users ask about "recent" or "latest" emails, refer to lower-numbered emails (Email #1, #2, etc.)
- When users ask about "old" or "first" emails, refer to higher-numbered emails

RESPONSE GUIDELINES:
1. Always start with a friendly greeting or acknowledgment
2. Present information in a clear, organized way
3. Use bullet points or numbered lists when appropriate
4. Decode and clean up any encoded email subjects to show proper, readable titles
5. Provide helpful context and insights
6. When showing email subjects, make them human-readable
7. Suggest follow-up actions when relevant
8. End responses helpfully, asking if they need more information
9. When users ask to "write a reply" or "draft a response", provide actual helpful draft content
10. Use context from previous conversation to understand what "this email" refers to
11. Be proactive in offering practical help like drafting replies, summarizing action items, etc.
12. If asked about writing replies, always provide a sample response based on the email content

FORMATTING RULES:
- Clean up encoded subjects like "=?UTF-8?Q?..." to show the actual readable title
- Present email information in an easy-to-read format
- Use proper spacing and organization
- Highlight important information clearly

EXAMPLE GOOD RESPONSES:
- "I'd be happy to help you with that! Your most recent email is..."
- "Looking at your emails, I can see that..."
- "Great question! Here's what I found in your inbox..."
- "I've analyzed your emails and here's a summary..."

SPECIAL INSTRUCTIONS FOR REPLY WRITING:
When users ask to "write a reply" or "draft a response":
1. ALWAYS provide actual draft content - never say you can't do it
2. Use the email content and context to create a relevant response
3. Include proper greeting, main message, and professional closing
4. Match the tone of the original email (professional, casual, etc.)
5. For LinkedIn invitations: suggest accepting and a brief professional message
6. For job emails: provide professional interest and next steps
7. For notifications: acknowledge and ask for clarification if needed

EXAMPLE REPLY RESPONSES:
- "I'd be happy to help you draft a reply! Here's a suggested response: [actual draft content]"
- "Based on this LinkedIn invitation, here's a professional response you could send: [draft]"
- "For this job opportunity, here's a response that shows your interest: [draft]"

Remember: Be helpful, friendly, and make the user feel like they're talking to a knowledgeable friend who cares about helping them manage their email effectively. Always provide practical, actionable help!
""".format(len(self.documents), len(self.documents))
            )
            
            print("✅ Chat engine ready!")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up chat engine: {str(e)}")
            return False
    
    def chat(self, query: str) -> str:
        """Chat with the assistant about emails"""
        if not self.chat_engine:
            return "❌ Chat engine not initialized. Please run setup first."
        
        # Handle special queries that need comprehensive data
        query_lower = query.lower()
        if any(phrase in query_lower for phrase in ["all emails", "summarize emails", "show me all", "complete summary", "all subjects"]):
            return self.get_all_emails_summary()
        
        try:
            # Add friendly context about email ordering and total count
            context_info = f"""
IMPORTANT CONTEXT FOR FRIENDLY RESPONSE:
- User has {len(self.documents)} emails total
- Email #1 is the MOST RECENT (newest)
- Email #{len(self.documents)} is the OLDEST
- Remember to be friendly, conversational, and helpful
- Always decode and clean up any encoded subjects
- Use natural, warm language in your response
- If user asks to write a reply or response, provide actual helpful draft content
- Use context from the conversation to understand references like "this email"

USER QUERY: """
            
            # Handle specific chronological queries with clear guidance
            if any(phrase in query_lower for phrase in ["last email", "most recent", "latest email", "newest email"]):
                context_info += "The user wants information about the MOST RECENT email (Email #1). Be warm and helpful in your response. "
            elif any(phrase in query_lower for phrase in ["first email", "oldest email", "earliest email"]):
                context_info += f"The user wants information about the OLDEST email (Email #{len(self.documents)}). Be friendly and informative. "
            elif any(phrase in query_lower for phrase in ["write a reply", "draft a response", "reply to", "respond to", "write back"]):
                context_info += """The user wants help writing a reply to an email. Based on the previous conversation context:
                - If they just asked about a specific email, help them write a reply to that email
                - Provide actual draft content, not just say you can't do it
                - Make the reply professional and appropriate for the email type
                - Include greeting, main message, and closing
                - Be helpful and provide real value. """
            
            full_query = context_info + query
            response = self.chat_engine.chat(full_query)
            return str(response)
        except Exception as e:
            return f"I'm sorry, I encountered an issue while processing your request: {str(e)}. Please try asking in a different way, and I'll do my best to help!"
    
    def draft_email_reply(self, email_content: str, email_type: str = "general") -> str:
        """Helper method to draft email replies based on content and type"""
        
        # LinkedIn invitation template
        if "linkedin" in email_content.lower() and "invitation" in email_content.lower():
            return """Hi there,

Thank you for the LinkedIn invitation! I'd be happy to connect with you.

Looking forward to staying in touch and potentially collaborating in the future.

Best regards,
[Your Name]"""
        
        # Job opportunity template
        if any(word in email_content.lower() for word in ["job", "position", "career", "hiring", "opportunity"]):
            return """Hello,

Thank you for reaching out about this opportunity. I'm very interested in learning more about the position.

Could you please provide additional details about:
- Job responsibilities and requirements
- Team structure and company culture
- Next steps in the application process

I'd appreciate the chance to discuss how my skills and experience align with your needs.

Best regards,
[Your Name]"""
        
        # Course/Learning template
        if any(word in email_content.lower() for word in ["course", "learning", "education", "training"]):
            return """Hello,

Thank you for sharing this learning opportunity. I'm interested in expanding my skills in this area.

Could you provide more information about:
- Course curriculum and duration
- Prerequisites or requirements
- Enrollment process

Looking forward to your response.

Best regards,
[Your Name]"""
        
        # General professional template
        return """Hello,

Thank you for your email. I appreciate you reaching out.

I'd like to learn more about this. Could you please provide additional details?

Looking forward to hearing from you.

Best regards,
[Your Name]"""
    
    def get_email_stats(self) -> dict:
        """Get statistics about processed emails"""
        if not self.documents:
            return {"error": "No emails processed"}
        
        stats = {
            "total_emails": len(self.documents),
            "subjects": [doc.metadata.get("subject", "Unknown") for doc in self.documents[:5]],
            "all_subjects": [doc.metadata.get("subject", "Unknown") for doc in self.documents],
            "processed_date": datetime.now().isoformat()
        }
        
        return stats
    
    def get_all_emails_summary(self) -> str:
        """Get a comprehensive summary of all processed emails"""
        if not self.documents:
            return "No emails have been processed yet."
        
        summary_parts = []
        summary_parts.append(f"📧 **Total Emails Processed: {len(self.documents)}**\n")
        
        for i, doc in enumerate(self.documents, 1):
            subject = doc.metadata.get("subject", "Unknown Subject")
            email_id = doc.metadata.get("email_id", "Unknown")
            
            # Extract a brief snippet from the document text
            text_lines = doc.text.split('\n')
            analysis_line = None
            for line in text_lines:
                if line.startswith("AI Analysis:"):
                    analysis_line = text_lines[text_lines.index(line) + 1] if text_lines.index(line) + 1 < len(text_lines) else None
                    break
            
            summary_parts.append(f"{i}. **{subject}**")
            if analysis_line and analysis_line.strip():
                summary_parts.append(f"   {analysis_line.strip()}")
            summary_parts.append(f"   Email ID: {email_id}\n")
        
        return "\n".join(summary_parts)

def main():
    print("🤖 Gmail Q&A Chatbot")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = GmailChatbot()
    
    # Setup process
    print("\n1️⃣ Setting up Gmail Chatbot...")
    
    if not chatbot.fetch_and_process_emails(max_emails=10):
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
    
    # Show all emails summary
    print("\n📋 All Emails Overview:")
    print("-" * 30)
    all_summary = chatbot.get_all_emails_summary()
    print(all_summary)
    
    # Interactive chat loop
    print("\n💬 Chat with your emails! (type 'quit' to exit)")
    print("💡 Try: 'summarize all emails', 'show me all email subjects', 'what emails did I get?'")
    print("=" * 50)
    
    while True:
        try:
            query = input("\n🤔 Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not query:
                continue
                
            print("🤖 Assistant:", end=" ")
            response = chatbot.chat(query)
            print(response)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
