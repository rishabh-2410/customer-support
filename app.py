import time
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(override=True)

MODEL_NAME = "gpt-5.4-mini"


RETURN_POLICY = """ Unused items can be returned within 7 days of purchase for a full refund. """
SYSTEM_PROMPT = f""" 
    You are a customer support agent for a company that sells software. You are given a question and you need to answer it.
    You have no order, shipment, or tracking data. If the user asks where an order is, say you cannot look it up. Never invent a status, location, or tracking update.
    Here is the return policy: {RETURN_POLICY}.
    """

system = {"role": "system", "content": SYSTEM_PROMPT}


messages = [
    system,
    {"role": "user", "content": "Where is my order #9001?"}
 ]


def run(client, messages, path="runs.jsonl"):
    start = time.perf_counter()
    response = client.chat.completions.create(model=MODEL_NAME, messages=messages)
    end = time.perf_counter()
    elapsed = end - start
    print(response.choices[0].message.content)
    print(f"Latency: {elapsed:.2f} seconds")
    
    usage = response.usage
    record = {
        "model": response.model,
        "input": messages[-1]["content"],
        "latency_seconds": round(elapsed, 2),
        "input_tokens": usage.prompt_tokens if usage else None,
        "output_tokens": usage.completion_tokens if usage else None,
        "total_tokens": usage.total_tokens if usage else None,
        "response": response.choices[0].message.content,
    }

    with Path(path).open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    return record




if __name__ == "__main__":
    client = OpenAI()
    run(client, messages)
