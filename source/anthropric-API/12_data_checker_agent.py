import os
import pandas as pd
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

AGENT_INSTRUCTIONS = """
You are a Data checking and Q&A agent for a Disneyland Reviews dataset
You have been given:
- Overall dataset metadata (rows, column names)
- Data types
- Null counts
- Counts of missing placeholder values
- Duplicate row counts
- Duplicate review ID counts
- Summary statistics for numeric fields
- a small sample of rows

Your job:
1. Answer the user's questions about this dataset's quality and structure
2. Use the provided summary to answer things like:
    - Average rating
    - Number of rows and columns
    - which columns have missing values or missing placeholders
    - how many duplicates exist
    - basic quality report
3. If the user asks for something that cannot be answered from the summary,
    clearly say that you only have summary statistics and cannot see individual rows
4. Keep answers short, clear, and focused on the data
"""

def load_csv_auto():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir,"DisneylandReviews.csv")
    if not os.path.exists(csv_path):
        print("Error, file not found in project folder")
        exit()
    try:
        return pd.read_csv(csv_path)
    except:
        try: 
            return pd.read_csv(csv_path,encoding = "latin1")
        except:
            return pd.read_csv(csv_path, encoding= "cp1252")

def build_dataset_summary(df: pd.DataFrame)->str:
    lines =[]
    lines.append(f"Total rows : {len(df)}")
    lines.append(f"Total columns : {len(df.columns)}")
    lines.append(f"Column names : {", ".join(df.columns)}")

    lines.append("\nColumn data types:")
    lines.append(df.dtypes.to_string())

    lines.append("\n Null value counts per column")
    lines.append(df.isna().sum().to_string())

    lines.append("\n Counts of string missing per column:")
    for col in df.columns:
        if df[col].dtype =="object":
            missing_count = (df[col]=="missing").sum()
            if missing_count > 0:
                lines.append(f"  {col}: {missing_count}")
    if all(
        not (df[col].dtype == "object" and (df[col]=="missing").any()) 
        for col in df.columns
    ):
        lines.append("no missing placeholder strings found")

    dup_rows = df.duplicated().sum()
    lines.append(f"\nNumber of completely duplicate rwos: {dup_rows}")

    if "Review_ID" in df.columns:
        dup_ids = df['Reviw_ID'].duplicated().sum()
        lines.append(f"Number of duplicate Review_ID values: {dup_ids}")

    if "Rating" in df.columns:
        lines.append("\n Rating column summary stats : ")
        lines.append(df['Rating'].describe().to_string())

    lines.append("\n Sample of first 5 rows:")
    lines.append(df.head(5).to_string(index=False))

def answer_question(client : Anthropic, dataset_summary: str , question : str) -> str:
    prompt = f"""
{AGENT_INSTRUCTIONS}
Here is the dataset summary:

--- DATASET SUMMARY START ---
{dataset_summary}
--- DATASET SUMMARY END ---

User question:
{question}

Using only the dataset summary above, answer the user's question.
When giving numeric answers, be precise and explain briefly how it relates to the dataset.
If the question cannot be answered with the available information, say so clearly
"""
    response = client.messages.create(
                    model = MODEL_NAME,
                    max_tokens = 800,
                    messages = [{"role":"user","content": prompt}]
                )

    return get_combined_text(response.content)

def main():
    client = get_client()
    df = load_csv_auto()
    dataset_summary = build_dataset_summary(df)

    while True:
        user_q = input("What do you want to know?<Exit> to quit").strip()
        if user_q.lower() in ["exit","quit","q"]:
            print("Good bye")
            break

        if not user_q:
            print("PLease type a question or <exit> to quit")
            continue

        print("Thinking")
        answer = answer_question(client, dataset_summary, user_q)
        print(answer)
                              

                       

if "__name__" =="__main__":
    main() 