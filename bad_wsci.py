"""Baseline: pass every knowledge file to Qwen as context."""

import os
from pathlib import Path


question = (
    "I changed my university password this morning. Now my Windows laptop "
    "won't connect to campus Wi-Fi, but my phone still works."
)


def main():
    from ollama import chat

    knowledge = Path(__file__).parent / "knowledge"
    context = ""
    for file in sorted(knowledge.glob("*.txt")):
        context += f"\n[{file.name}]\n{file.read_text(encoding='utf-8')}\n"
    response = chat(
        model=os.environ.get("OLLAMA_MODEL", "qwen3:8b"),
        messages=[
            {"role": "system", "content": "Answer using only the provided university knowledge."},
            {"role": "user", "content": f"Knowledge:\n{context}\nQuestion:\n{question}"},
        ],
    )
    print("Context characters:", len(context))
    print(response.message.content)


if __name__ == "__main__":
    main()
