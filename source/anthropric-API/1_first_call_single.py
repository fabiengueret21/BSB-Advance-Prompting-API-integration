from dataclasses import dataclass
from typing import List
import os

from dotenv import load_dotenv
import anthropic    
from anthropic import Anthropic
from anthropic.types import TextBlock


# Config

load_dotenv()

@dataclass
class Settings:
    api_key: str
    model: str = "claude-sonnet-5"  # Recommended standard production model


def get_settings() -> Settings:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
    return Settings(api_key=api_key)

# Initialize the client. It automatically looks for the ANTHROPIC_API_KEY environment variable.
def get_client() -> Anthropic:
    settings = get_settings()
    return Anthropic(api_key=settings.api_key)

def send_message_to_claude(message: str) -> str:
    settings = get_settings()
    client = get_client()

    response = client.messages.create(
        model=settings.model,
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": message
            }
        ]
    )
    text_blocks: List[TextBlock] = [
        block for block in response.content if isinstance(block, TextBlock)
    ]
    if not text_blocks:
        return "[Claude returned no text blocks in the response.]"
    combined_text = " ".join(block.text for block in text_blocks)
    return combined_text


def main() ->None:
    print("Checking API key and testing connection to the Anthropic API...")
    
    try:
        # step 1: try creating the client
        client = get_client()
        # step 2: Make small test request
        test_prompt = "Test message: please confirm the API connection"
        response = send_message_to_claude(test_prompt)

        # Extract and print the text content from the response 
        print("API key loaded successfully. Connection to the Anthropic API is working.")
        print("\n--- Test Response ---")
        print(response)
        print("-------------------------")

    except Exception as error:
        print(f"\nAn error occurred: {error}")

if __name__ == "__main__":
    main()
