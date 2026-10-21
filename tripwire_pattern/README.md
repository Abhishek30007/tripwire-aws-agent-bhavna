# tripwire_pattern: a reusable Decider 2B guardrail

**Pattern:** guardrails. **Question:** are a tool call's arguments grounded in what the user actually said, and does the call follow instructions hidden in tool output?

## What is in the box

| File | Purpose |
|---|---|
| `decider_client.py` | The typed questions (`QUESTIONS`) and an HTTP client for `strands-decider serve` |
| `cascade.py` | `Thresholds` and `route()`: probabilities to lanes (allow, block, ask_user, llm_judge) |
| `core.py` | `Tripwire.evaluate()`: decide, route, optional judge, audit log. No framework dependency |
| `handler.py` | `TripwireHandler`, a Strands `InterventionHandler` for `before_tool_call` |
| `state.py` | Splits message history into trusted user text and untrusted tool output |
| `policy.py` | Optional deterministic rules (prod mutation, environment confusion, roles); can only tighten a Decider allow |
| `authorization.py` | Single-use, argument-bound confirmation tokens for your own ask-the-user step |
| `judge.py` | Optional Amazon Bedrock judge for low-confidence cases |
| `audit_log.py` | JSONL decision log |
| `redact.py` | Scrubs credentials from audit-log rows (adapted from Ayush Devani's prototype) |
| `examples/minimal_agent.py` | One tool, one guard |

## Use it

1. Run Decider: `pip install strands-decider` then `strands-decider serve StrandsAgents/strands-decider-2B-hobson-v21 --port 8000`.
2. Copy this folder into your project.
3. Add the handler:

```python
from strands import Agent
from tripwire_pattern import DeciderClient, Tripwire
from tripwire_pattern.handler import TripwireHandler

tripwire = Tripwire(DeciderClient(), destructive={"delete_bucket", "stop_instance"})
agent = Agent(tools=my_tools, interventions=[TripwireHandler(tripwire, guarded_tools={"delete_bucket"})])
```

Actions returned to Strands: allow is `Proceed`, block is `Deny`, medium confidence is `Guide` (the agent asks the user). Pass `judge=BedrockJudge()` to `Tripwire` to send low-confidence cases to Bedrock; without a judge they become a question to the user.

## Tune it

`Thresholds(allow_conf=0.70, destructive_conf=0.84, judge_conf=0.30, injection_p=0.60)`. Confidence is `|2p - 1|`. Raise `allow_conf` to ask the user more often; lower `injection_p` to block suspected injection earlier. Pick values from a calibration table on your own cases (see `eval/run_benchmark.py`).

## Adapt the question

Edit `ARGS_GROUNDED` and `FROM_UNTRUSTED_TEXT` in `decider_client.py` for your domain, or add a third question and read it in `cascade.route()`.

## Limits

Decider 2B is experimental. Treat its probability as a signal, keep a human or LLM lane for uncertain cases, and keep the handler fail-closed for destructive tools.
