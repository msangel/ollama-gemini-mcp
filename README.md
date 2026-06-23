### Prerequirements
Використовуємо unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:UD-Q4_K_XL замість стандартного qwen3-coder:30b Q4_K_M, бо у Qwen3-Coder 30B є відомий баг ненадійного tool calling з пропуском <tool_call> тегу [#475](https://github.com/QwenLM/Qwen3-Coder/issues/475), а Unsloth-збірка містить оновлений template/tool-calling fixes і кращу 4-bit dynamic quantization.
```
ollama pull hf.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:UD-Q4_K_XL
```

### Run project
```
uv venv .venv && \
uv pip install --python .venv/bin/python 'mcp[cli]' google-genai
```

### Raw api sample to search
```
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: YOUR_TOKEN' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
```
#### Raw ollama call with tools
```
curl -s http://localhost:11434/api/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3-coder:30b",
    "stream": false,
    "messages": [
      {
        "role": "user",
        "content": "Use the search tool to find current stable Spring Boot version."
      }
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "google_grounded_search",
          "description": "Search the web using Gemini Google Search grounding.",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {
                "type": "string",
                "description": "Search query"
              }
            },
            "required": ["query"]
          }
        }
      }
    ]
  }' | jq
{
  "model": "qwen3-coder:30b",
  "created_at": "2026-06-22T13:12:06.236734071Z",
  "message": {
    "role": "assistant",
    "content": "",
    "tool_calls": [
      {
        "id": "call_2jfcaqzr",
        "function": {
          "index": 0,
          "name": "google_grounded_search",
          "arguments": {
            "query": "current stable Spring Boot version"
          }
        }
      }
    ]
  },
  "done": true,
  "done_reason": "stop",
  "total_duration": 12957578949,
  "load_duration": 129418226,
  "prompt_eval_count": 301,
  "prompt_eval_duration": 10419830000,
  "eval_count": 28,
  "eval_duration": 2400978000
}
```

### Run with agent
Install agent:
```
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
> Share anonymous usage data to help improve goose?
No
> How would you like to set up your provider?
Manual Configuration
> Which model provider should we use?
Ollama
> Provider Ollama requires OLLAMA_HOST, please enter a value
localhost
> Would you like to configure advanced settings?
Yes
Enter OLLAMA_TIMEOUT (optional, press Enter to skip)
600
> Select a model
qwen3-coder:30b
```
```
goose configure
> What would you like to configure?
Add Extension
> What type of extension would you like to add?
Command-line Extension
> What would you like to call this extension?
ollama-gemini-mcp
> What command should be run?
/home/user/.local/share/ollama-gemini-mcp/start.sh
> Please set the timeout for this tool (in secs):
300
> Enter a description for this extension:
Tool for search information in the internet
> Would you like to add environment variables?
no
```

