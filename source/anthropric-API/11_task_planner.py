import os

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock

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

SYSTEM = """
You are a fully interactive, dynamic TASK PLANNING AGENT.
Your behaviour rules:
1. When the user gives a goal:
    - do not immediately generate a plan
    - Ask only the most important clarifying question first
    - Base each next question only on the user's last answer
    - Do not repeat questions
    - Do not follow a template
    - Adapt your questions to the goal, domain, timeline, skill level and context

2. Continue asking question until you have enough information
    - Usually 2 to 4 questions

    - Stop early if the user already gave enough details
3. After you have enough clarity
    - Generate the final task plan

4. Final output
    If FORMAT= JSON:
    - return only valid json
    - Include goal, profile summary, phases, tasks,dependencies
    If FORMAT= TEXT
    - return a readable, personalized, structured plan with phases+ tasks

5. Very important:
    - never ask the same wuestion twice
    - never ask irrelevent questions
    - Choose questions that actually matter for building a good plan

6. After giving the plan:
    - Stop aksing questions and wait for the user's next goal
"""



def main():
    client = get_client()

    while True:
        user_goal = input("Your goal: ").strip()
        if user_goal.lower() in  ("exit","quit","q"):
            print("Good bye")
            break
        fmt = input("Format? (1=JSON 2=Test, default = Text)").strip()
        fmt = "json" if fmt == 1 else "text"
        messages = [ { 
                    "role":"user",
                    "content": f"GOAL: {user_goal}\nFORMAT: {fmt}"
                }

    ]
        while True:
        
            response = client.messages.create(
                model = MODEL_NAME,
                max_tokens = 1000,
                messages = messages
            )
            agent_reply =  get_combined_text(response.content)
            print(agent_reply)
            if ("PHASE" in agent_reply.upper()) or agent_reply.strip().startswith("{"):
                break
        user_answer = input("> ")
        messages.append({"role":"assistant","content": agent_reply})
        messages.append({"role":"user","content": user_answer})                            

if "__name__" =="__main__":
    main() 