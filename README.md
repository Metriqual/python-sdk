# Metriqual Python SDK

Official Python client for the [Metriqual](https://metriqual.com) API — a unified LLM proxy supporting chat, audio/TTS, video, image, music generation, and more.

## Installation

```bash
pip install metriqual
```

## Quick Start

```python
from metriqual import MQL

client = MQL(api_key="mql_...")

# Chat completion
response = client.chat.create(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4o",
)
print(response["choices"][0]["message"]["content"])
```

## Streaming

```python
for chunk in client.chat.stream(messages=[{"role": "user", "content": "Tell me a story"}]):
    delta = chunk["choices"][0].get("delta", {})
    content = delta.get("content", "")
    print(content, end="", flush=True)
```

Or collect everything at once:

```python
result = client.chat.stream_to_completion(
    messages=[{"role": "user", "content": "Tell me a story"}],
)
print(result["text"])
```

## Text-to-Speech

```python
# Sync (returns bytes)
audio_bytes = client.audio.speech(input="Hello world", voice="alloy")

# Async with polling
audio_bytes = client.audio.speech_async_and_wait(
    input="Long text...", voice="alloy", model="tts-1-hd"
)

with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

## Image Generation

```python
response = client.images.generate(prompt="A sunset over mountains", model="dall-e-3")

# Just URLs
urls = client.images.generate_urls(prompt="A sunset over mountains")

# MiniMax
response = client.images.generate_minimax(prompt="A futuristic city")
```

## Video Generation

```python
# Submit and poll until complete
status = client.video.create_and_wait(prompt="A drone flying over a city")

# Submit, poll, and download bytes
video_bytes = client.video.create_and_download(prompt="Ocean waves at sunset")

# MiniMax image-to-video
result = client.video.create_from_image(first_frame_image="https://...")
```

## Music Generation

```python
result = client.music.generate_from_prompt("upbeat jazz")
result = client.music.generate_with_lyrics("a sad ballad", "Verse 1: ...")
```

## Voice Cloning

```python
with open("voice_sample.wav", "rb") as f:
    result = client.audio.upload_and_clone_voice(f, voice_id="my-voice")
```

## Embeddings

```python
response = client.embeddings.create(input="Hello world", model="text-embedding-3-small")
```

## Proxy Keys

```python
keys = client.proxy_keys.list()
new_key = client.proxy_keys.create(
    name="production",
    providers=[{"provider": "openai", "api_key": "sk-..."}],
)
```

## Organizations

```python
orgs = client.organizations.list()
client.organizations.invite_member(org_id, email="dev@company.com", role="member")
```

## Analytics

```python
overview = client.analytics.get_overview(start_date="2024-01-01")
timeseries = client.analytics.get_timeseries()
```

## Prompt Hub

```python
prompt = client.prompt_hub.create(name="My Prompt", content="You are a helpful...")
client.prompt_hub.publish(prompt["id"])
public_prompts = client.prompt_hub.discover(category="coding")
```

## Experiments (A/B Testing)

```python
exp = client.experiments.create(name="Model Comparison")
client.experiments.create_variant(exp["id"], name="GPT-4o", model="gpt-4o")
client.experiments.start(exp["id"])
```

## Feedback

```python
client.feedback.submit(request_id="req_123", rating=5, comment="Great response")
analytics = client.feedback.get_analytics()
```

## Webhooks

```python
hook = client.webhooks.create(url="https://example.com/hook", events=["request.completed"])
deliveries = client.webhooks.get_deliveries(hook["id"])
```

## Subscription & Trials

```python
status = client.subscription.get_status()
can_trial = client.subscription.can_start_trial()
remaining = client.subscription.get_remaining_quota("monthlyRequests")
```

## Authentication

```python
# API key (most common)
client = MQL(api_key="mql_...")

# Bearer token (for user-context auth)
client = MQL(token="eyJ...")

# Switch auth on the fly
admin_client = client.with_auth(api_key="mql_admin_key")
```

## Configuration

```python
client = MQL(
    api_key="mql_...",
    base_url="https://api.metriqual.com",  # default
    timeout=30.0,                           # seconds
    max_retries=3,                          # retries on 5xx / network errors
)
```

## Error Handling

```python
from metriqual import MQL, MQLAPIError, MQLTimeoutError

try:
    response = client.chat.create(messages=[{"role": "user", "content": "Hi"}])
except MQLTimeoutError:
    print("Request timed out")
except MQLAPIError as e:
    print(f"API error {e.status}: {e}")
```

## Context Manager

```python
with MQL(api_key="mql_...") as client:
    response = client.chat.complete(
        [{"role": "user", "content": "Hello"}],
        model="gpt-4o",
    )
```

## API Reference

| Resource | Methods |
|----------|---------|
| `client.chat` | `create`, `stream`, `stream_to_completion`, `complete` |
| `client.audio` | `speech`, `speech_async`, `speech_async_and_wait`, `transcribe`, `translate`, `clone_voice`, `design_voice`, `get_voices`, `create_voice`, `generate_lyrics`, + more |
| `client.video` | `create`, `get_status`, `download`, `create_and_wait`, `create_and_download`, `create_from_image`, `query_video_status`, + more |
| `client.images` | `generate`, `generate_base64`, `generate_urls`, `generate_minimax` |
| `client.music` | `generate`, `generate_from_prompt`, `generate_with_lyrics` |
| `client.embeddings` | `create`, `create_with_dimensions`, `create_base64` |
| `client.proxy_keys` | `list`, `create`, `delete`, `regenerate`, `test`, `get_usage`, + org variants |
| `client.filters` | `list`, `create`, `update`, `toggle`, `delete`, `get_templates`, `test`, + org variants |
| `client.organizations` | `list`, `get`, `create`, `list_members`, `invite_member`, `accept_invite`, + more |
| `client.analytics` | `get_overview`, `get_timeseries`, `get_provider_stats`, `get_usage_logs`, + org variants |
| `client.webhooks` | `list`, `create`, `update`, `delete`, `get_deliveries`, + org variants |
| `client.experiments` | `create`, `list`, `get`, `update`, `delete`, `start`, `pause`, `complete`, `create_variant`, `get_analytics` |
| `client.feedback` | `submit`, `get`, `get_analytics`, `export` |
| `client.prompt_hub` | `create`, `list`, `get`, `update`, `delete`, `publish`, `share`, `discover`, `star`, `fork`, `attach_to_key`, + more |
| `client.subscription` | `get_status`, `get_plan_tier`, `get_limits`, `has_feature`, `start_trial`, `is_at_limit`, + more |
| `client.models` | `list`, `list_by_provider`, `get` |
| `client.pricing` | `get_by_provider`, `get_openai`, `get_anthropic`, `get_mistral`, `get_gemini`, `get_cohere` |

## Requirements

- Python >= 3.9
- [httpx](https://www.python-httpx.org/) >= 0.25.0

## License

MIT — see [LICENSE](LICENSE).
