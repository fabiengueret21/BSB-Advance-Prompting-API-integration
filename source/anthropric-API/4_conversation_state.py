# conversation_state.py

import os
from dotenv import load_dotenv
from anthropic import Anthropic 
from anthropic.types import TextBlock

def choose_model():

    default_model = "claude-sonnet-5-5"
    # ask user for model choice
    print(f"\nEnter model name (enter for default: {default_model}):")
    model_name = input("> ").strip()
    if model_name =="":
        model_name = default_model
    print(f"\nUsing model: {model_name}\n")
    return model_name

def get_system_instruction(default_text):
    # ask user for system instruction
    print(f"\nEnter system instruction (enter for a simple default):")
    system_instruction = input("> ").strip()
    if system_instruction =="":
        system_instruction = default_text
    print(f"\nUsing system instruction: {system_instruction}\n")
    return system_instruction

def run_stateless_example(client,model_name):
    # illustrate a stateless example with no conversation history
    print("\nRunning stateless example with no conversation history...\n")
    default_system_instruction = "You are a helpful assistant."
    system_instruction = get_system_instruction(default_system_instruction)
    # first user input
    user_input = input("\nEnter your prompt: ").strip()

    if not user_input:
        print("first_message was empty. Using I have a cat and a dog> as the default first message.")
        user_input = "I have a cat and a dog."


    response = client.messages.create(
        model=model_name,
        max_tokens=150,
        system=system_instruction,
        messages=[{
                            "role": "user",
                            "content": user_input
                        }
                    ]
    )
    print("\n First response from Claude: ",response.content[0].thinking,"\n")

    # second user message
    user_input2 = input("\nEnter your second prompt: ").strip()
    if not user_input2:
        print("second_message was empty. defaulting to <what did I tell you earlier>")
        user_input2 = "what did I tell you earlier?"
    response2 = client.messages.create(
        model=model_name,
        max_tokens=150,
        system=system_instruction,
        messages=[
            {
                "role": "user",
                "content": user_input2
            }
        ]
    )
    print("\n Second stateless response from Claude: ",response2.content[0].thinking,"\n")


def run_stateful_chat_loop(client,model_name):
    # we will maintain a conversation history list and send it for every request to Claude. This is a stateful chat loop.
    print("\nRunning stateful chat loop with conversation history...\n")
    default_system_instruction = ["You are a helpful, friendly assistant.",
                                  "Always remember the context of the conversation and respond accordingly."]
    system_instruction = get_system_instruction(default_system_instruction)

    print(" Type 'exit' to quit the loop=chat.")
    print(" Type you prompt and press enter to send it to Claude.\n")
    
    messages =[]
    while True:
        user_input = input("\nEnter your prompt: ").strip()
        # exit condition
        if user_input.lower() in ["exit","quit","bye"]:
            print("Exiting the conversation loop.")
            break   

        if not user_input:
            print("User input was empty. Please enter a prompt.")
            continue

        # add user input to conversation history
        messages.append({ "role": "user",  "content": user_input })
         # send msg to Claude with conversation history
        
        response = client.messages.create(
            model="claude-sonnet-5-5",  # swap for any current model string
            max_tokens=200,
            system="you are a helpful assistant.",
            messages=messages,
        )
        text_blocks= [
        block for block in response.content if isinstance(block, TextBlock)
        ]

        assistant_response = " ".join(block.text for block in text_blocks)


        # add assistant response to conversation history
        messages.append({ "role": "assistant", "content": assistant_response})
        print("\nClaude: ", assistant_response, "\n")
        '''
        # conversation history
        print("\nConversation History:")
        for msg in conversation_history:
            print(f"  {msg['role'].capitalize()}: {msg['content']}")
        '''

def main():
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")

    client = Anthropic(api_key=api_key)

    model_name = choose_model()

    # run stateless example
   # run_stateless_example(client, model_name)
    # run stateful chat loop
    run_stateful_chat_loop(client, model_name)

if __name__ == "__main__":
    main()