- Interesting thing happened on day 2 of this week.
- I asked the model how are you?, but forced the tool use call to get the weather.
- Model did not know which city to extract and present as a arguement to the weather call.
- Now the random city of Pune was chosen two times and its weather was received as answer.
- But in the follow up call to the model , the weather data was ignored as an answer to the orignal greeting that i gave. 
- It is an interesting case.
- Solution to this is let the model decide when to call the tool, by removing AUTO in the configuration.

```the model correctly inferred an implicit need for external data from an indirect question, without you ever mentioning the tool or the word "weather."```

# Week 2 Notes — Days 4-6

## Day 4: Second tool + model choosing correctly
- Registered two tools (`get_weather`, `convert_currency`) in an `AVAILABLE_FUNCTIONS` dict mapping tool name → real Python function, instead of writing an `if/elif` chain per tool. Scales cleanly to more tools later.
- The model correctly distinguished which tool to call based on the question alone — no hints, no keywords hardcoded on my end.
- Discovered a real gap: my first version of `run_agent` only handled **one** tool call per question. A genuinely multi-part question ("weather in Tokyo AND convert currency") broke it, because the model tried to chain a second tool call and my code only expected plain text back.
- Fixed by rewriting `run_agent` as a loop: keep calling the model and appending results to the conversation until it finally returns plain text instead of another tool request. Verified this works for even 3 chained tool calls in a single user turn (2 weather + 1 currency, in one go).

## Day 5: Graceful tool failure handling
- Tool functions never `raise` on failure — they catch their own exceptions (`Timeout`, `ConnectionError`, `HTTPError`, `KeyError`/`ValueError` for bad data) and return `{"error": "..."}` as normal data instead.
- This matters because an error becomes something the *model* can react to intelligently (e.g. explain the failure, suggest alternatives) rather than a crash the model never even sees.
- Verified for real, unprompted: asked for INR→AFN and INR→BDT conversions, which the free Frankfurter API doesn't support (real 404s). The tool caught both, logged them as warnings, and the model responded with a clear explanation plus alternative resources (Google Finance, XE.com, OANDA) — without me ever telling it to do that.
- Also wrapped the outer `run_agent` loop in try/except, so even a failure in the *Gemini* call itself (not just the tool) doesn't crash the whole program.

## Day 6: Logging
- Replaced scattered `print()` statements with Python's `logging` module — writes to both the terminal and a persistent `agent.log` file.
- Logged the meaningful *decisions*, not just output: which tool was chosen, what arguments, whether it succeeded or failed, and the final answer step count. Kept user-facing `Bot:` replies as plain `print()` since those aren't logs, they're the actual UI.
- `agent.log` gives a timestamped audit trail I can review after a session — much more useful than terminal scrollback for debugging "why did it call the wrong tool."

## Key takeaway across all three days
Building a working demo (Day 4's basic wiring) and building something *robust* (looping correctly, failing gracefully, being observable) are different amounts of work — the gap between them is most of where real engineering effort goes.