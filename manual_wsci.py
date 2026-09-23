"""Manually select context for the Wi-Fi and password problem."""

import os
from pathlib import Path


question = (
    "I changed my university password this morning. Now my Windows laptop "
    "won't connect to campus Wi-Fi, but my phone still works."
)
selected_files = [
    "wifi_setup.txt",
    "password_changes.txt",
    "service_status.txt",
]


def main():
    from ollama import chat

    knowledge = Path(__file__).parent / "knowledge"
    context = ""
    for filename in selected_files:
        file = knowledge / filename
        context += f"\n[{filename}]\n{file.read_text(encoding='utf-8')}\n"
    response = chat(
        model=os.environ.get("OLLAMA_MODEL", "qwen3:8b"),
        messages=[
            {"role": "system", "content": "Answer using only the selected university knowledge."},
            {"role": "user", "content": f"Knowledge:\n{context}\nQuestion:\n{question}"},
        ],
    )
    print("Context characters:", len(context))
    print(response.message.content)


if __name__ == "__main__":
    main()
