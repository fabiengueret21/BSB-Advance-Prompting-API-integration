import os
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock
from typing import List

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


def run_variant(client: Anthropic, variant_name: str, system_prompt: str, user_task: str, max_tokens: int):
    print(f"Variant name: {variant_name.upper()} RUN")

    response = client.messages.create(
            model = MODEL_NAME,
            max_tokens = max_tokens,
            system = system_prompt,
            messages =[{ "role":"user","content": user_task}]
    )
    assistant_text = get_combined_text(response.content)
    print("Assistant reply (first 800 characters)\n")
    print(assistant_text[:800])
    if len(assistant_text)>800: print("\n truncated")

    # token usage
    usage = response.usage
    input_tokens = usage.cache_read_input_tokens
    output_tokens =usage.output_tokens
    total_tokens = input_tokens+output_tokens

    print("Token usage")
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Total tokens: {total_tokens}")

    return input_tokens,output_tokens,total_tokens


def main():
    client = get_client()
    print(" Demo: reducing token usage in API calls")

    user_task ="""
I am in my 4th year of engineering and I have 6 months to prepare for a data engineer 
role at a big tech company.
Create a preparation roadmap that covers:
- Core CS and data engineering subjects
- Weekly milestones
- Daily practise activities
- Practise resources / platforms

Make it realistic and focused on interview preparation
""".strip()

    naive_system ="""
You are a very detailed, verbose, senior career coaching assistant for software and data engineering
Your job is to create very detailed, long-form, highly structured answers with headings, subheadings, tables,
bullet points, examples and extensive elaboration.

Whenever a user asks for a study pla, roadmap or learning strategy, you must
1. Explain the high-level mindset and philosophy behind the plan in detail.
2. Provide a long contextual explanation  of why each topic is important.
3. Provide multiple alternative strategies (at least 2-3 paths) and explain each path.
4. Add motivational advice, mindset tips and general career guidance.
5. Avoid beign concise. Prefer long explanations over short one.
6. Do not limit number of bullet points or work count.

Always respond with as much helpful details as possible.

""".strip()

    optimized_system ="""
You are a focused career planning assistant.

Goal: produce a clear, concise 6-month roadmap for a data engineering interview.

Constraints:
- Use at most 6 bullet points
- Under each main bullet, add at most 3 sub-bullets
- Maximum ~250 words
- No long motivational speeches, only practical steps.
""".strip()

    naive_tokens = run_variant(client, naive_system,user_task,800)

    optimized_tokens = run_variant(client, optimized_system,user_task,300)

    print("Let's compare")
    print(f"Naive total tokens: {naive_tokens[3]}")
    print(f"Opti total tokens: {optimized_tokens[3]}")

    if optimized_tokens[3] < naive_tokens[3]:
        savings =  naive_tokens[3] - ptimized_tokens[3] 
        percent = savings / naive_tokens *100  if naive_tokens[3]>0 else 0
        print(f"Total savings: {savings} tokens (~{percent:.1f}% reduction)")
    else:
        print("No reduction in this run")

if "__name__" =="__main__":
    main() 