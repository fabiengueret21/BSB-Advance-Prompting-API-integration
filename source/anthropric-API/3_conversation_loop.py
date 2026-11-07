# conversation loop

import os
from dotenv import load_dotenv
from anthropic import Anthropic

def main():
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")

    client = Anthropic(api_key=api_key)

    # ask user for inputs
    print("Claude conservation loop starts:")
    print(" Type 'exit' to quit the loop=chat.")

    while True:
        user_input = input("\nEnter your prompt: ").strip()
        # exit condition
        if user_input.lower() in ["exit","quit","bye"]:
            print("Exiting the conversation loop.")
            break   

        # send msg to Claude
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )
        print("\nClaude: ",response.content[0].text,"\n")

if __name__ == "__main__":
    main()