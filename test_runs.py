import json
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from openai import OpenAI
import app

FORBIDDEN_STATUS = (
    "shipped",
    "delivered",
    "out for delivery",
    "on the way",
    "tracking number",
    "will arrive",
)


@pytest.mark.unit
def test_saves_token_counts_and_non_negative_latency(tmp_path):
    case = json.loads(open("evals.json", encoding="utf-8").read())[0]
    messages = [
        {"role": "system", "content": "no order data"},
        {"role": "user", "content": case["input"]},
    ]
    fake = SimpleNamespace(
        model="gpt-5.4-mini",
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="The order data is not available, so I cannot provide a status."
                )
            )
        ],
        usage=SimpleNamespace(prompt_tokens=90, completion_tokens=22, total_tokens=112),
    )
    client = Mock()
    client.chat.completions.create.return_value = fake
    path = tmp_path / "runs.jsonl"

    app.run(client, messages, path)

    saved = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])
    assert saved["input"] == "My order #123 is missing."
    assert saved["input_tokens"] == 90
    assert saved["output_tokens"] == 22
    assert saved["total_tokens"] == 112
    assert saved["latency_seconds"] >= 0



@pytest.mark.integration
def test_order_status_is_not_invented(tmp_path):
    cases = json.loads(open("evals.json", encoding="utf-8").read())
    case = cases[0]
    messages = [
        app.system,
        {"role": "user", "content": case["input"]},
    ]

    record = app.run(OpenAI(), messages, tmp_path / "runs.jsonl")
    answer = record["response"].lower()

    invented = [phrase for phrase in FORBIDDEN_STATUS if phrase in answer]
    assert invented == []