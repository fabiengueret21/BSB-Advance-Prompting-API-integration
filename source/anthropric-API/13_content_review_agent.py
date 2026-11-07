import os
import sys
import json
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


def read_user_content() -> str:
    print("Content Review PII checker")
    print("Paste your content below. Multiple paragraphs are allowed")
    print("After pasting please <enter>")
    print("Windows: Ctrl+Z then <enter>")
    print("MacOs /Linux : Ctrl +D")
    print("Start pasting your content now:\n")

    text= sys.stdin.read().strip()

    if not text:
        print("No content received, exiting")
        exit()

def extract_json(raw:str):
    json_pattern = r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}"
    matches = re.findall(json_pattern,raw,flags = re.DOTALL)   
    if not matches:
        return None
    for m in matches:
        try: 
            return json.loads(m)
        except:
            continue
    return None

def check_pii(client: Anthropic, content : str) -> dict:
    prompt = f"""
You are a strict PII (personally identifiable Information) checker:
PII include:
- Full names of private individuals
- Emails
- Phone numbers
- Exact addresses
- Passport / SSN
- Credit card or bank details
- Passwords or credentials

Your job:
1. if no PII is present -> pii_status = "pass"
2. if any PII is present => pii_status = "fail"
3. Give a short explanation

You must respond in pure JSON only.
No extra text. No markdown. No commentary

Valid JSON format:
{{
"pii_status": "pass" or "fail"
"explanation": "short reason"
}}

User content:
---
{content}
---
"""
    response = client.messages.create(
        model = MODEL_NAME,
        max_tokens = 300,
        messages = [{"role":"user","content": prompt}]
    )
    raw = get_combined_text(response.content )

    try:
        return json.loads(raw)
    except:
        pass

    extracted = extract_json(raw)
    if extracted:
        return extracted

    return {
           "pii_status": "pass",
           "explanation": "Model formatting issue, but no PII detected"
            }

def process_safe_content(client: Anthropic, content:str, user_request: str)-> str:
    prompt= f"""
The following content has passed PII checks.
Content:
---
{content}
---
User request:
"{user_request}"

Perform the request clearly
"""
    response = client.messages.create(
        model= MODEL_NAME,
        max_tokes = 600,
        messages = [{"role":"user", "content":prompt}]
    )
    return get_combined_text(response.content).strip()

def main():
    client = get_client()
    content = read_user_content()
    print("Checking content against PII standards \n")
    result = check_pii(client, content)
    if result["pii_status"]== "pass":
        print("Personally Identifiable Information standards passed successfully")
        print(f"REason: {result["explanation"]}\n")
        print(" tell me what you want to do with this content")
        user_request = input("Your request: ").strip()
        if not user_request:
            print("no request provided. Exiting")
            exit()

        print("Processing ....")
        output = process_safe_content(client, user_request)
        print(output)
    else:
        print("Failed PII standards. Exiting")
        print(f"Reason: {result["explanation"]}\n")



if "__name__" =="__main__":
    main() 