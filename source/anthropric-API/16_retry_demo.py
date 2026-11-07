import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic, APIError
from anthropic.types import TextBlock

from typing import List

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


def send_with_retry(client, model,user_message,max_retries=3, delay =2):

    for attempt in range(1,max_retries +1):
        try:
            print("Attempt {attempt} of {max_retries}")
            response = client.messages.create(
                model = model,
                max_tokens  = 200,
                messages = [{
                    "role": "user",
                    "content": user_message
                }]
            )
            return get_combined_text(response.content)


        except APIError as e:
            print(f"Error: {e}.Retrying in {delay} seconds")
            time.sleep(delay)
    return "All retries failed. Please try again later"

def main():
    client = get_client()
    user_message = input(">").strip()
    MODEL_NAME = "claude-sonnet-5-5"
    result = send_with_retry(client, MODEL_NAME,user_message,3,2)
    print("Final Result")
    print(result)

if __name__ == "__main__":
    main()