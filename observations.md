# WSCI exercise observations

Question: A student changed their university password. Their Windows laptop
cannot connect to campus Wi-Fi, but their phone still can.

Model: local `qwen3:8b` through Ollama. The runs used the course knowledge
files and did not use external information.

| Program | Context given to the answer call | Result |
| --- | ---: | --- |
| `bad_wsci.py` | 4,189 characters from all seven files | Qwen suggested forgetting eduroam, reconnecting with the new password, and checking the account if that fails. |
| `manual_wsci.py` | 2,163 characters from three selected files | Qwen gave essentially the same diagnosis and steps. |
| `smarter_wsci.py` | 2,163 selected characters, compressed to 1,047 in the first run | Qwen returned structured JSON diagnosing cached old credentials, recommending an eduroam reset and reconnection, with `needs_escalation: false`. |

The selected files were `wifi_setup.txt`, `password_changes.txt`, and
`service_status.txt`. On a second run, the program read the prior diagnostic
result from `state.json`; compression produced 927 characters and the
structured diagnosis remained the same. The separate `report_context` was
not sent to the diagnostic call.

These outputs are model-generated, so their exact wording and character
counts may vary on another run.

The programs were also rerun with the official `ollama` Python package 0.6.2
from `ollama_practice/.venv` and the supplied `ollama-models` directory.
All three completed; the structured run compressed the selected context to
1,009 characters and returned the same diagnosis.
