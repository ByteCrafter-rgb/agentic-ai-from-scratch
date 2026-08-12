# Agentic AI from scratch
In this repo I will complete the checklist provided to me by claude for Agentic AI practical skills.

# Agentic AI Build — Daily Checklist (8 Weeks)

Tick one box per day. ~60–90 min/day. Don't skip to the next week's tasks early — build in order.

## Week 1 — LLM API Fundamentals
- [x] Day 1: Set up API access (OpenAI/Anthropic/Gemini), send your first basic completion call from a script
- [x] Day 2: Experiment with system prompts vs user prompts, temperature, max tokens
- [x] Day 3: Implement function calling — get the model to call one dummy function correctly
- [x] Day 4: Get the model to return structured JSON output reliably (use schema/response_format if available)
- [x] Day 5: Build a tiny CLI chatbot that keeps conversation history in a list
- [ ] Day 6: Add error handling — rate limits, timeouts, malformed responses
- [ ] Day 7: Review — write 5 lines in NOTES.md on what you learned + what confused you

## Week 2 — Prompting + Single-Tool Agent
- [ ] Day 1: Pick one real external API (weather, currency, search) and call it manually first
- [ ] Day 2: Wire that API as a "tool" the model can call via function calling
- [ ] Day 3: Get the agent to decide ON ITS OWN whether to use the tool or answer directly
- [ ] Day 4: Add a second tool, test the model choosing correctly between the two
- [ ] Day 5: Handle tool failure gracefully (API down, bad input) — agent should recover, not crash
- [ ] Day 6: Write basic logging so you can see the agent's tool-call decisions
- [ ] Day 7: Review — commit to GitHub with a short README describing what it does

## Week 3 — Learn One Orchestration Framework
- [ ] Day 1: Install LangGraph (or CrewAI), read core concepts docs (nodes/edges or agents/tasks)
- [ ] Day 2: Rebuild your Week 2 single-tool agent using the framework
- [ ] Day 3: Understand how the framework manages state vs how you did it manually
- [ ] Day 4: Add a conditional branch (e.g. agent decides between 2+ paths, not just tool y/n)
- [ ] Day 5: Add a "human-in-the-loop" or approval-style checkpoint
- [ ] Day 6: Break something on purpose, debug it — get comfortable reading framework errors
- [ ] Day 7: Review — commit, write NOTES.md on framework vs manual trade-offs

## Week 4 — Memory + Multi-Step Planning
- [ ] Day 1: Add persistent memory across turns (not just in-session list — save/load from a file or DB)
- [ ] Day 2: Design a multi-step goal (e.g. "research X, summarize, draft email") and break it into subtasks
- [ ] Day 3: Implement the planning step — agent outputs a task list before executing
- [ ] Day 4: Implement execution loop that works through the task list
- [ ] Day 5: Add retry logic for failed steps (don't just fail the whole chain)
- [ ] Day 6: Test edge cases — ambiguous goals, impossible tasks, contradictory instructions
- [ ] Day 7: Review — commit, demo the full flow to yourself out loud

## Week 5 — RAG + Vector Database
- [ ] Day 1: Set up a vector DB (Pinecone/Weaviate/pgvector), understand embeddings basics
- [ ] Day 2: Ingest a small document set (10-20 docs) and generate embeddings
- [ ] Day 3: Build basic retrieval — query in, relevant chunks out
- [ ] Day 4: Wire retrieval into your agent's reasoning loop (agent can "look things up")
- [ ] Day 5: Tune chunk size / retrieval count, observe how it affects answer quality
- [ ] Day 6: Add source citation — agent should say which doc it pulled info from
- [ ] Day 7: Review — commit, write NOTES.md on RAG design choices and trade-offs

## Week 6 — Multi-Agent + Production Hardening
- [ ] Day 1: Split your single agent into 2 specialized agents with distinct roles
- [ ] Day 2: Build the handoff logic between them (who talks to whom, and when)
- [ ] Day 3: Add a 3rd agent if it fits your use case (e.g. a "reviewer" or "critic" agent)
- [ ] Day 4: Add structured logging across the whole system (timestamps, agent, action, result)
- [ ] Day 5: Build a tiny eval harness — 5-10 test cases you can re-run to check nothing broke
- [ ] Day 6: Add basic cost/latency tracking (token usage, response time per call)
- [ ] Day 7: Review — commit, run your eval harness end to end

## Week 7 — Deployment
- [ ] Day 1: Write a Dockerfile for your project
- [ ] Day 2: Get it running locally in Docker
- [ ] Day 3: Deploy to a free-tier VM or platform (Railway, Render, Fly.io, etc.)
- [ ] Day 4: Add environment variable handling for API keys (never hardcode secrets)
- [ ] Day 5: Test the deployed version end-to-end, fix what breaks in production vs local
- [ ] Day 6: Add a minimal front-end or CLI interface if you don't have one yet
- [ ] Day 7: Review — confirm it's live and reachable, note any known limitations

## Week 8 — Polish & Document
- [ ] Day 1: Write a clear README: what it does, architecture diagram, tech stack
- [ ] Day 2: Write the "why" — design decisions and trade-offs (framework choice, memory approach, etc.)
- [ ] Day 3: Record a 2-3 min demo video or GIF walkthrough
- [ ] Day 4: Clean up code — remove dead code, add comments where logic isn't obvious
- [ ] Day 5: Write a short LinkedIn/portfolio post about what you built and learned
- [ ] Day 6: Prepare a 60-second verbal pitch of the project for interviews
- [ ] Day 7: Final review — mock-explain the whole system out loud, note gaps to fill later

---
**Rule of thumb:** if a day's task isn't done, don't skip it — extend that week by a day rather than moving ahead with gaps in the build.
