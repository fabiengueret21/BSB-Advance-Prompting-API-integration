import os

from dotenv import load_dotenv
from anthropic import Anthropic



def main():

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")


    client = Anthropic(api_key=api_key)

    # ask use for inputs
    print("Enter system instructions:")
    system_instruction = input("> ").strip()
    print("\nEnter user message:")
    user_message = input("> ").strip()
    # let user choose model
    print("\nEnter model (enter for default):")
    model_name = input("> ").strip()
    if model_name=="":
        model_name = "claude-sonnet-5"

    response = client.messages.create(
        model=model_name,
        max_tokens=256,
        system=system_instruction,
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )
    

    # print de result
    print("\n === MODEL RESPONSE ===")
    print(response.content[0].text)


if __name__ == "__main__":
    main()
