# Customer support

A small support agent that answers product questions from a fixed return policy. It has no order, shipment, or tracking data, so it must not invent an order status.

Each run calls `gpt-5.4-mini` and appends one JSON line to `runs.jsonl` with the model name, user input, reply, token counts, and latency.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your OpenAI key:

```bash
OPENAI_API_KEY=sk-...
```

## Run

```bash
python app.py
```

The default question is `Where is my order #9001?`. Change `messages` in `app.py` to ask something else. A return-policy question should be answered from the 7-day unused-item rule. An order-status question should say the order cannot be looked up.

## Run log

`runs.jsonl` is gitignored. Each line looks like:

```json
{"model": "gpt-5.4-mini-2026-03-17", "input": "Where is my order #9001?", "latency_seconds": 1.74, "input_tokens": 111, "output_tokens": 66, "total_tokens": 177, "response": "I can't look up that order."}
```

## Evaluation

`evals.json` holds cases. The current case asks where order `#123` is. The expected behavior is that the agent does not invent a status.

## Tests

Unit tests mock the client and check that token counts and a non-negative latency are saved. The integration test calls the live model and fails if the reply contains an invented status such as "shipped" or "delivered".

```bash
pytest -m unit
pytest -m integration
pytest
```

The integration test needs `OPENAI_API_KEY` and spends a real request.
