from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict
import json
import os
import shutil
from dotenv import load_dotenv
from uagents import Context, Model, Protocol, Agent
from hyperon import MeTTa

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

load_dotenv()

agent = Agent(name="Semiconductor Market Intelligence Agent", port=8008, mailbox=True, publish_agent_details=True)

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

metta = MeTTa()
initialize_investment_knowledge(metta)
rag = InvestmentRAG(metta)
llm = LLM(api_key=os.getenv("ASI_ONE_API_KEY"))

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
                    
                    answer_text = f"**{selected_q}**\n\n{answer}"
                else:
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

agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()