from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict
import json
import os
import shutil
import asyncio
from dotenv import load_dotenv
from uagents import Context, Model, Protocol, Agent
from hyperon import MeTTa

env_path = os.path.join(os.path.dirname(__file__), '.env')
env_loaded = load_dotenv(env_path)

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from metta.investment_rag import InvestmentRAG
from metta.knowledge import initialize_investment_knowledge
from metta.utils import LLM, process_query
from metta.scheduler import ScheduledTaskManager
from metta.email_service import email_service
from metta.stock_monitor import stock_monitor

agent = Agent(name="Semiconductor Market Intelligence Agent", port=8008, mailbox=True, publish_agent_details=True, readme_path = "README.md")

class InvestmentQuery(Model):
    query: str
    intent: str
    keyword: str

def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )

# Initialize core components
metta = MeTTa()
initialize_investment_knowledge(metta)
rag = InvestmentRAG(metta)
llm = LLM(api_key=os.getenv("ASI_ONE_API_KEY"))

# Initialize scheduled task manager
task_manager = ScheduledTaskManager(rag, llm)

chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id),
    )

    terminal_width = shutil.get_terminal_size().columns
    separator = "=" * terminal_width
    dash_line = "-" * terminal_width

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
            print(f"\n{separator}")
            print("🚀 NEW SESSION STARTED")
            print(f"📧 From: {sender}")
            print(f"{separator}\n")
            continue
        elif isinstance(item, TextContent):
            user_query = item.text.strip()
            ctx.logger.info(f"Got a semiconductor market query from {sender}: {user_query}")
            
            print(f"\n{separator}")
            print("📩 NEW REQUEST RECEIVED")
            print(separator)
            print(f"👤 From: {sender}")
            print(f"❓ Query: {user_query}")
            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(dash_line)
            
            try:
                print("🔍 Processing query...")
                response = process_query(user_query, rag, llm)
                
                print("\n✅ RESPONSE GENERATED")
                print(dash_line)
                
                if isinstance(response, dict):
                    selected_q = response.get('selected_question', user_query)
                    answer = response.get('humanized_answer', 'I apologize, but I could not process your query.')
                    
                    print(f"📌 Question: {selected_q}")
                    print(f"\n💡 Answer:\n{answer}")
                    
                    # Use raw response directly without formatting
                    answer_text = f"🔹 {selected_q}\n\n{answer}"
                else:
                    # Use raw response directly without formatting
                    answer_text = str(response)
                    print(f"💡 Response:\n{answer_text}")
                
                print(dash_line)
                print("✉️  Sending response to user...")
                await ctx.send(sender, create_text_chat(answer_text))
                print("✅ Response sent successfully!")
                print(f"{separator}\n")
                
            except Exception as e:
                ctx.logger.error(f"Error processing semiconductor market query: {e}")
                print("\n❌ ERROR OCCURRED")
                print(dash_line)
                print(f"⚠️  Error: {str(e)}")
                print(dash_line)
                
                await ctx.send(
                    sender, 
                    create_text_chat("I apologize, but I encountered an error processing your semiconductor market query. Please try again.")
                )
                print("✉️  Error message sent to user")
                print(f"{separator}\n")
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")
            print(f"⚠️  Unexpected content type from {sender}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}")

@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialization when the agent starts"""
    print("\n" + "="*60)
    print("🚀 SEMICONDUCTOR MARKET INTELLIGENCE AGENT")
    print("="*60)
    print(f"🤖 Agent Name: {agent.name}")
    print(f"🌐 Agent Address: {agent.address}")
    print("="*60)
    
    # Check email configuration
    if email_service.email_user and email_service.email_password and email_service.recipient_email:
        print("📧 Email service: ✅ Configured")
        print(f"📨 Reports will be sent to: {email_service.recipient_email}")
        
        # Send startup notification email
        print("📮 Sending startup notification email...")
        startup_success = email_service.send_startup_notification()
        if startup_success:
            print("✅ Startup notification email sent successfully!")
        else:
            print("❌ Failed to send startup notification email")
    else:
        print("📧 Email service: ⚠️  Not configured")
        print("   Set EMAIL_USER, EMAIL_PASSWORD, RECIPIENT_EMAIL in .env file")
    
    # Start scheduled task manager
    print("\n📅 Starting scheduled task manager...")
    task_manager.start()
    
    print("\n✅ Agent startup complete!")
    print("💬 Ready to receive queries via Agentverse chat interface")
    print("="*60 + "\n")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """Cleanup when the agent shuts down"""
    print("\n⏸️  Shutting down Semiconductor Market Intelligence Agent...")
    task_manager.stop()
    print("✅ Shutdown complete")

agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()