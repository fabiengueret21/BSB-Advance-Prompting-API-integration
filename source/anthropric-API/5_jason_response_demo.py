import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import TextBlock

def main():
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
   
    client = Anthropic(api_key=api_key)

    messages = []  # the API is stateless, so you keep the history yourself

    print("Describe a simple task, issue or future request")

    user_description = input("Your description: ").strip()

    if not user_description:
        print("No description provided. Exiting.")
        return

    # System instruction to force JSON outout

    system_instruction = """
      You are a helpful assistant. 
      Please respond in JSON format only.
      Do not use markdown.
      Do not use code fences.
      Do not use backticks.
      Use exactly this schema:
      { "title" : string,
        "category" : "bug"|"feature"|"question",
        "priority" : "low"|"medium"|"high",
        "summary" : string, 
        "steps" : [string]
          }
    
    Rules:
    - The 'title' should be a concise summary of the task, issue, or request
    - The 'category' should be inferred from the description 
    - The 'priority' should be inferred from urgency and impact
    - The 'summary' 1-3 sentences 
    - The 'steps' 3-7 concrete steps

    Do not include any fields other than those specified in the schema.
    Do not add any explanation outside of the JSON object.

      """
 
    response = client.messages.create(
            model="claude-sonnet-5-5",  # swap for any current model string
            max_tokens=1024,
            system=system_instruction,
            messages=[{"role": "user", "content": user_description}],
        )

    if not response.content:
        print("No response received from the model.")
        return

    text_block = next((block for block in response.content if isinstance(block, TextBlock)), None)

    if text_block is None:
        print("Claude returned no text blocks")

    raw_json = text_block.text

    print(" Raw JSON from Claude")
    print(raw_json)

    clean_json = raw_json.strip()
    clean_json =clean_json.replace("```json","").replace("```","").strip()
    
    try:
        data = json.loads(clean_json)
    except json.JSONDecodeError as e:
        print("Error failed to parse JSON from Claude")
        print("details : ",e)
        return

    print(" Parsed JSON ")
    print("Title : {data.get('title')}")
    print("Category : {data.get('category')}")
    print("Priority : {data.get('priority')}")
    print("Summary : {data.get('summary')}")
    print("Steps")
    for idx, step in enumerate(data.get("steps",[]),start = 1):
        print(f"{idx},{step}")


if __name__ == "__main__":
  main()