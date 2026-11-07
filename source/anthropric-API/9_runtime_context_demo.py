import os
import json
from datetime import datetime

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock

MODEL_NAME= "claude-sonnet-5-5"

def get_client() -> Anthropic:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is missing")
    return Anthropic(api_key=api_key)

def build_runtime_context(user_name: str) -> dict:
    now = datetime.now(datetime.timezone.utc).isoformat() + "Z"
    context = {
        "user": { 
            "name": user_name,
            "id": f"user-{user_name.lower().replace(" ","-")}"
        },
        "request": {
            "timestamp_utc": now,
            "channel": "cli",
            "request_id" : f"req-{int(datetime.now(datetime.timezone.utc).timestamp())}"
        }
    }
    return context

def main():
    user_name  = input("Please enter your name").strip() or "Guest"
    user_question = input("Briefly describe your question or issue").strip()

    if not user_question:
        print("No question? Exiting")
        return
    runtime_context = build_runtime_context(user_name)
    context_json = json.dumps(runtime_context,indent = 2)

    print(context_json)

    client = get_client()

    user_message = f"""
                    You are a helpful assistant.
                    You will receive: 
                    1. a user quesion
                    2. some runtime context as JSON

                    Use the context to make your response more personalized.

                    User question:
                    {user_question}

                    Runtime context (JSON)
                    {context_json}
             """.strip()

    print("sending request to Claude with runtime context")

    response = client.messages.create(
        model = MODEL_NAME,
        max_tokens = 400,
        messages = [
            { 
                "role":"user",
                "content": user_message,
            }
        ]
    )

    text_blocks =[
            block for block in response.content if isinstance(block, TextBlock)

    ]
    if not text_blocks:
        print(" Claude returned no text content")
        return

    answer = "\n".join(block.text for block in text_blocks)
    print(answer)

if "__name__" =="__main__":
    main()