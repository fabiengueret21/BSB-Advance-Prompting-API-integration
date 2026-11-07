import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic,APIError,RateLimitError

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
exit(1)

client = Anthropic(api_key=API_KEY)

MODEL_NAME = "claude-sonnet-5-5"

SYSTEM_PROMPT = """
You are AURA, an engaging, friendly AI mentor.

Style:
- Sound natural and conversational, like a helpful human
- Use simple, clear language. Avoid being too formal or robotic.
- Ask follow-up questions to better understand the user before giving long answers.
- Especially for planning tasks (like timetable, study plan, routines), ask 1-3 quick clarifying questions.
- Keep answers focused and structured, but not like a strict textbook.
- Encourage the user and keep the tone positive and motivating.

Behavior:
- start conversation with a warm greeting if the user seems to say "hi" or "hello" or similar.
- When the user ask for help (eg timetable, learning plan, project help), do:
1) Ask clarifying questions (like duration, goals, current level)
2) the nsuggest a clear, step-wise plan.
- if you need more info, say so instead of guessing
- if the user seems stuck or confused, reassure them and explain slowly.

Safety:
- avoid unsage, harmful or disallowed content
- if user asks something unsfae, gently refuse and redirect to something helpful.
"""

conversation_history=[]

def trim_history(max_messages: int = 20):

    global conversation_history
    if len(conversation_history)>max_messages:
        conversation_history = conversation_history[-max_messages:]

def print_welcome():
    print(" AURA an engaging CLaude Chatbot")
    print("talk to me naturally, like a friend and mentor")
    print("Commands:")
    print(" /reset -> clear conversation")
    print(" /exit -> quit")
    print("good luck")

def chatbot_loop():
    print_welcome()

    while True:
        try: 
            user_input = input("You: ").strip()
        except (KeyboardInterrupt,EOFError):
            print("Bot: Bye now and take care")
            break
        if not user_input:
            print("Bot: Say anything - a question, idea or problem. I'm listening ")
            continue
        if user_input.lower() == "/exit":
            print("Bot: Bye!! Nice chatting with you")
            break
        if user_input.lower() == "/reset":
            conversation_history.clear()
            print("Bot: Chat reset. Let's start fresh! What's on your mind now?")
            continue

        conversation_history.append({"role":"user", "content": user_input})
        trim_history()

        try:
            response = client.messages.create(
                model = MODEL_NAME,
                max_tokens = 600,
                system = SYSTEM_PROMPT,
                messages = conversation_history,
            )
            bot_reply = response.content[0].text
            conversation_history.append({"role":"assistant", "content": bot_reply})

            print(f"Bot: {bot_reply}\n")
        except RateLimitError:
            print(" I'm getting a lot of traffic right now. Let me take a short pause")
            time.sleep(2)
            continue
        except APIError as e:
            print(f"API Error: {e}")
            print("Bot: something went wrong talking to the model. Try again in a moment")
            continue
        except Exception as e:
            print(f"unexpected error: {e}")
            print("Bot: i hit an unexpected issue")
            continue
if __name__ == "__main__":
    chatbot_loop()