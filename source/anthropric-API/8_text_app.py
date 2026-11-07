import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("API key missing")
    exit()

client = Anthropic(api_key = api_key)
MODEL = "claude-sonnet-5-5"

def ask_claude(user_text,instruction):
    
    prompt = f"""
        You are a text processing assistant.
        Here's the suer's text:
        --- START OF TEXT ---
        {user_text}
        --- END OF TEXT ---

        The user wants:
        {instruction}

        Now perform the instruction based on the provided text

        """
    response = client.messages.create(
            model = MODEL,
            max_tokens = 800,
            messages =[{"role":"user","content":prompt}]


    )
    return response.content[0].text

def main():
    print("Advanced Text Processor")
    print("paste your full content below")

    try:
        user_text =""
        while True:
            line = input()
            user_text += line +"\n"
    except EOFError:
        pass

    print("content received")

    print("now tell me what you want to do with it")

    while True:
        instruction = input("Your instructions or exit to stop")
        if instruction.lower() in ["exit","quit"]:
            print("bye bye")
            break
        print("Processing")
        result  = ask_claude(user_text,instruction)
        print("Result")
        print(result)

if __name__ =="__main__":
    main()