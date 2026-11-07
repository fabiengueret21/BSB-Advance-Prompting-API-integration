import os
import asyncio
import sys

from dotenv import load_dotenv
import anthropic
from anthropic import AsyncAnthropic

MODEL_NAME = "claude-sonnet-5-5"

async def stream_once(client: AsyncAnthropic,prompt:str)-> None:
    print("Claude:",end=" ",flush=True)

    try: 
        async with client.message.stream(
            model = MODEL_NAME,
            max_tokens = 512,
            messages = [{"role":"user", "content": prompt}]
        ) as stream:
            async for text in stream.text_stream:
                print(text,end="",flush=True)
            print()
            final_message =  await stream.get_final_message()
    except anthropic.APIConnectionError as e:
        print("Connection Error", file =sys.stderr)
        print(e.__cause__, file=sys.stderr)
    except anthropic.RateLimitError:
        print("Rate limit hit", file =sys.stderr)
    except anthropic.APIStatusError as e:
        print("API error {e.status_code}: {e.response}",file = sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}",file=sys.stderr)

async def chat_loop() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("API key missing", file = sys.stderr)
        return

    client = AsyncAnthropic(api_key = api_key)
    print("Type a prompt and press enter, 'exit' to stop")
    try:
        while True:
            try:
                user_input = input("You : ").strip()
            except(EOFError, KeyboardInterrupt):
                print("Exiting")
                break
            if not user_input:
                continue
            if user_input.lower() in ["exit","quit","q"]:
                print("Goodbye")
                break
            await stream_once(client,user_input)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(chat_loop())                
        