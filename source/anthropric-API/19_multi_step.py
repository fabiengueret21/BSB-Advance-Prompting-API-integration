import os
import re

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock
from typing import List

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


def extract_point_limit(user_prompt:str)->int:
    # Detect if the user explicitly asks for X points
    # If not defaults to 5
    match = re.search(r"(\d+)\s*ppints?",user_prompt.lower())
    if match:
        return int(match.group(1))
    return 5

def wants_points(user_prompt: str)->bool:
    # Check if the user want to answer in bullet points
    text= user_prompt.lower()
    return ("point" in text) or ("bullet" in text) or ("list" in text)

def is_elaboration_request(user_prompt: str)-> bool:
    # check if user is asking to elaborate on previous answer
    text= user_prompt.lower()
    return any(
        phrase in text
        for phrase in [
            "elaborate",
            "explain more",
            "explain me more",
            "more detail",
            "continue",
            "tell me more"
        ]
    )
def build_system_prompt(point_limit:int,use_points:bool)->str:
    mode_instruction =""
    if use_points:
        mode_instruction=f"""
For this user message, the user either asked for bullets or your reply would be clearer  in bullet points.

You must:
- Answer in exactly {point_limit} bullet points unless the suer clearly asks for a different number.
- Keep each bullet point short and focused.
- Avoid long paragraphs.
"""
    else:
        mode_instruction ="""
For this user message,the suer did not explicitly ask for bullet points.
You must:
- Answer breifly in 2-3 concise sentences
- Do no create bullet lists unless the user clearly ask for them. 
"""

    return f"""
You are an assistant designed to optimize token usage in a multi step conversation.
Global rules that always apply:
- Be concise and avoid unnecessary verbosity.
- Never write long essays unless the suer explicitly requests it.
- If the user says elaborate or explain maore continue or similar
you must elaborate on the topic of the previous assistant response
instead of asking what they mean.

{mode_instruction}
Always follow those rules strictly
"""



def call_api(client: Anthropic, system_prompt: str, messages: list):
    response = client.messages.create(
        model = MODEL_NAME,
        max_tokens = 400,
        system= system_prompt,
        messages  = messages 
                )
    output_text = get_combined_text(response.content)

    input_tokens = response.usage.input_tokens
    output_tokens =response.usage.output_tokens
    total_tokens = input_tokens+output_tokens
    usage ={
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }
    return output_text,usage


def main():
    client = get_client()
    print(" Mutli steps Workflow Demo/ Type exit to end")

    conversation_history = []
    while True:
        user_input = input("You: ")

        if user_input.lower().strip() == "exit":
            print("Ending. Goodbye")

        use_points  = wants_points(user_input) or is_elaboration_request(user_input)
        point_limit = extract_point_limit(user_input) if use_points else 5

        system_prompt = build_system_prompt(point_limit,use_points)

        conversation_history.append({"role":"user","content": user_input})

        try:
            assistant_reply,usage = call_api(client,system_prompt,conversation_history)

            conversation_history.append({"role":"assistant","content":assistant_reply})

            print("Assistant : ", assistant_reply)
            print(f"Input tokens : {usage["input_tokens"]}")
            print(f"Output tokens : {usage["output_tokens"]}")

        except Exception as e:
            print("API Error: ",e )
if "__name__" =="__main__":
    main() 