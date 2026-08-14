# Week 1 Notes — Agentic AI Basics

## What I learned
1. **`.text` isn't the whole response.** The response object carries `finish_reason`, `usage_metadata`, and (on some models) visible "thinking" tokens — always worth checking these before assuming an empty or weird `.text` means broken code.
2. **`max_output_tokens` is a shared budget, not just an answer-length cap.** On reasoning models, invisible/visible "thinking" tokens eat into that same budget before the real answer gets written — a generous-looking limit can still truncate to nothing.
3. **Quotas come in different flavors** (per-minute vs per-day), and the error message's `quotaId` field is the only reliable way to tell which one you hit — the human-readable `retryDelay` can be misleading for daily quotas.
4. **Function calling is a round trip, not a single call.** The model requests a tool call, your code runs the real function, and you send the result back for a second, final response — this loop is the core of every agent.
5. **Schema-enforced JSON (`response_schema`) is far more reliable than prompting for JSON** — but still worth validating in code (missing fields, parse errors) rather than trusting it blindly.

## What confused me
- Python syntax still confuses me, overall the flow is easy to call the API pre-defined functions and defined result.
- Tool use is defintely a lame and hacky solution for a GenAI model, it will be cool to learn it.
- Wonder how this all will turn out to be agentic.

## Bugs I hit and fixed this week
- Model name deprecation (`gemini-2.5-flash` → 404 for new users)
- Empty `.text` caused by `max_tokens` being consumed entirely by thinking tokens
- Two different 429 errors: per-minute rate limit vs per-day quota exhaustion
- 503 ServerError (transient, unrelated to my code)
- Missing `thought_signature` when replaying a function call in conversation history — had to reuse the original `Part` object instead of rebuilding it

## Questions to explore next week
- 
-