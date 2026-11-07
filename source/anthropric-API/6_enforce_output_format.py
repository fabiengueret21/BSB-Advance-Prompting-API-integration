import os
import json
from typing import List

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock

MODEL_NAME = "claude-sonnet-5-5"

def get_client() -> Anthropic:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
    return Anthropic(api_key=api_key)

def choose_format()-> str:
    print("Choose a format for the output:")
    print("1. JSON")
    print("2. Bullet points")
    print("3. Numbered steps")

    while True:  
        choice = input("Enter the number of your choice: ").strip()    
        if choice == "1":
            return "json"
        elif choice == "2":
            return "bullets"
        elif choice == "3":
            return "steps"
        else:
            print("Invalid choice. Defaulting to plain text.")

def build_system_instruction(output_format: str) -> str:
    if output_format == "json":
        return """
        You are a formatting engine that outputs information in JSON format.
        Do not include any explanations, comments, or markdowns
        Do not warp the JSON in ``` or any kind of code block.
        Output must be a single JSON object.
        Use this schema
        {
            "title": "string",
            "severity": "low"|"medium"|"high",
            "summary": "string",
            "steps": string[]
        """.strip()
    
    elif output_format == "bullets":
        return """
        You are a a formatting engine that outputs information as bullet points only.
        Each line must start with "- " and be a single bullet point.
        Do not include any paragrapgs or prose outside of the bullet points.
        """.strip()

    elif output_format == "steps":
        return """
        You are a formatting engine that outputs information as numbered steps only.
        Each line must start with "1. ", "2. ", etc. and be a single step.
        Do not include any paragraphs or prose outside of the numbered steps.
        """.strip()

    else :
        return """
        You are a formatting engine that outputs information in plain text.
        Do not include any explanations, comments, or markdowns.
        """.strip()

def extract_text(response) -> str:
    text_blocks: List[TextBlock] = [
        block for block in response.content if isinstance(block, TextBlock)
    ]
    if not text_blocks:
        return "Claude returned no text content"
    return "\n".join(block.text for block in text_blocks)

def strip_code_fences(text: str) -> str:
    """removes markdown code fences
    This lets us safely parse json output from Claude without worrying about code fences."""
    stripped = text.strip()
    if not stripped.startswith("```") :
        return stripped
    lines  = stripped.splitlines()
    if lines:
        lines = lines[1:]
    if lines and lines[-1].strip().startswith( "```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()

def main():
    client = get_client()
    output_format = choose_format()
    system_instruction = build_system_instruction(output_format)
    print(system_instruction)
    user_input = input("Enter your prompt: ").strip()

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens = 1024,
        system = system_instruction,
        messages=[
            {"role": "user", "content": user_input},
        ],
  )

    text_output = extract_text(response)
    print(text_output)

    if output_format == "json":
        print("JSON validation check")
        cleaned = strip_code_fences(text_output)    
        try:
            data = json.loads(cleaned)
            print("Valid JSON")
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError as e:
            print("Invalid JSON")
            print("Error details:", e)
            print("Raw output from Claude:")
            print(text_output)

if __name__ == "__main__":
    main()