"""Demonstrate WRITE, SELECT, COMPRESS, and ISOLATE with Qwen."""

import json
import os
from pathlib import Path


ROOT = Path(__file__).parent
MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
question = (
    "I changed my university password this morning. Now my Windows laptop "
    "won't connect to campus Wi-Fi, but my phone still works."
)


def select_context(question):
    text = question.casefold()
    names = []
    groups = [
        (("wi-fi", "wifi", "eduroam", "network"), "wifi_setup.txt"),
        (("password", "credential", "login"), "password_changes.txt"),
        (("wi-fi", "wifi", "eduroam", "outage", "status"), "service_status.txt"),
        (("print", "printer"), "printing.txt"),
        (("email", "mail"), "email_setup.txt"),
        (("vpn",), "vpn.txt"),
        (("projector", "display", "hdmi"), "classroom_projectors.txt"),
    ]
    for keywords, filename in groups:
        if any(keyword in text for keyword in keywords):
            names.append(ROOT / "knowledge" / filename)
    return names


def compress_context(context, question):
    from ollama import chat

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract only university knowledge relevant to the question. "
                    "Preserve concrete steps and service status. Do not add facts."
                ),
            },
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nSelected knowledge:\n{context}",
            },
        ],
    )
    return response.message.content.strip()


def load_state():
    path = ROOT / "state.json"
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    return {"diagnostic_context": {}, "report_context": {}}


def save_state(state):
    with (ROOT / "state.json").open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)


def answer_question(question, compressed_context, prior_diagnostic):
    from ollama import chat

    response = chat(
        model=MODEL,
        format="json",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a university IT support assistant. Use only the "
                    "given knowledge and relevant earlier diagnostic facts. "
                    "Return one JSON object with exactly diagnosis (string), "
                    "recommended_steps (list of strings), and "
                    "needs_escalation (boolean). No markdown."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question:\n{question}\n\nRelevant knowledge:\n"
                    f"{compressed_context}\n\nEarlier facts for this question:\n"
                    f"{json.dumps(prior_diagnostic, ensure_ascii=False)}"
                ),
            },
        ],
    )
    result = json.loads(response.message.content)
    if (
        not isinstance(result, dict)
        or set(result) != {"diagnosis", "recommended_steps", "needs_escalation"}
        or not isinstance(result["diagnosis"], str)
        or not isinstance(result["recommended_steps"], list)
        or not all(isinstance(step, str) for step in result["recommended_steps"])
        or not isinstance(result["needs_escalation"], bool)
    ):
        raise ValueError("Qwen did not return the required structured response.")
    return result


def main():
    # SELECT: read only knowledge files relevant to this student's question.
    selected_files = select_context(question)
    context = ""
    for file in selected_files:
        context += f"\n[{file.name}]\n{file.read_text(encoding='utf-8')}\n"
    print("Selected files:", [file.name for file in selected_files])
    print("Selected context characters:", len(context))

    # COMPRESS: ask Qwen to extract the useful parts from the selected files.
    compressed_context = compress_context(context, question)
    print("Compressed context characters:", len(compressed_context))

    # ISOLATE: this call sees diagnostic state, never unrelated report state.
    state = load_state()
    previous = state.get("diagnostic_context", {})
    prior_diagnostic = previous.get("result", {}) if previous.get("question") == question else {}
    result = answer_question(question, compressed_context, prior_diagnostic)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # WRITE: persist reusable diagnostic findings for a later model call.
    state["diagnostic_context"] = {
        "question": question,
        "selected_files": [file.name for file in selected_files],
        "result": result,
    }
    state.setdefault("report_context", {})
    save_state(state)
    print("Diagnostic state saved to state.json")


if __name__ == "__main__":
    main()
