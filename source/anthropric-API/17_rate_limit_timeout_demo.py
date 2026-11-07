import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic, RateLimitError,APITimeoutError,APIConnectionError
from anthropic.types import TextBlock

from typing import List

MAX_TOKENS = 256
MAX_RETRIES = 3
MODEL_NAME = "claude-sonnet-5-5"

def get_client() -> Anthropic:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is missing")
    return Anthropic(api_key=api_key, timeout=20.0 )


def extract_text(blocks : List[TextBlock]) -> str:
    text_blocks : List[TextBlock] = [b for b in blocks if b.type  == "text"]
    if not text_blocks:
        return "[Claude returned no text content]"
    return "\n".join(block.text for block in text_blocks)



def ask_claude_with_retries(client: Anthropic,user_message: str)->str:
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            print("Attempt {attempt} of {MAX_RETRIES}")
            response = client.messages.create(
                model = MODEL_NAME,
                max_tokens  = MAX_TOKENS,
                messages = [{
                    "role": "user",
                    "content": user_message
                }]
            )
            return extract_text(response.content)

        except RateLimitError as e:
            wait_time = attempt * 2
            print(f"Rate Limit error on attempt {attempt}.Retrying in {wait_time} seconds")
            print(f"Details: {e}")
            time.sleep(wait_time)

        except APITimeoutError as e:
            wait_time = attempt * 2
            print(f"Request timed out on attempt {attempt}.Retrying in {wait_time} seconds")
            print(f"Details: {e}")
            time.sleep(wait_time)

        except APIConnectionError as e:
            wait_time = attempt * 2
            print(f"Network issue on attempt {attempt}.Retrying in {wait_time} seconds")
            print(f"Details: {e}")
            time.sleep(wait_time)


    return "All retries failed. We keep hitting rate limits, timeout or connection issues"

def main():
    client = get_client()
    user_message = input(">").strip()
    if not user_message:
        user_message = " Explain what API rate limits are and why they exist"
    reply = ask_claude_with_retries(client, user_message)
    print("Final Result")
    print(reply)

if __name__ == "__main__":
    main()