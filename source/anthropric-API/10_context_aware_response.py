import os
import json
from typing import List

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

def get_combined_text(blocks : List[TextBlock]) -> str:
    text_blocks : List[TextBlock] = [b for b in blocks if b.type  == "text"]
    if not text_blocks:
        return "[Claude returned no text content]"
    return "\n".join(block.text for block in text_blocks)



def main():
    client = get_client()
    name = input("Enter your name: ").strip() or "Friend"
    skill_level = input("Your skill level with technology (beginner/intermediate/advanced)").strip() or "beginner"
    mood = input(" how are you feeling right now? (eg tired, excited, stressed)").strip() or "curious"
    user_question = input("Now your question?").strip()
    if not user_question:
        print(" No question entered. Ending the activity")
        return

    context = {
        "user_profile" : {
            "name":name,
            "skill_level": skill_level,
            "interest": [
                "movies", "coding", "productivity","learning new skills"
            ],
        },
        "session_context" : {
                "mood": mood,
                "language": "English",
                "assistant_role": "helpful coach and friendly guide",
            },
            }
    prompt_text= (
        " You are an AI assistant that always uses the JSON context below to tailr your answer.\n"
        "The context contains information about the user and the current session.\n"
        "Here is the context: \n"
        f"{json.dumps(context,indent = 2)}\n"
        "Now, based on this context answer the user's question in a way that: \n"
        "matches their skill level\n"
        "respects their current mood\n"
        "feels personalized and friendly\n"
        f"User's question : {user_question}\n"
    )
    response = client.messages.create(
        model = MODEL_NAME,
        max_tokens = 400,
        messages = [
            { 
                "role":"user",
                "content": prompt_text,
            }
        ]
    )

    final_text = get_combined_text(response.content)
    print(final_text)

if "__name__" =="__main__":
    main()