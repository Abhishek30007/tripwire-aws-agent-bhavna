# Demo video script (target 2:40, hard limit 3:00)

Setup: Decider server running; dashboard open in a second window; `python -m agent.main` ready.

| Time | Show | Say |
|---|---|---|
| 0:00-0:20 | Title, one slide | AI agents with cloud access can act on wrong or injected instructions. Tripwire checks every call first. |
| 0:20-0:50 | `--scenario normal` | A normal request. Decider approves in milliseconds and the tool runs. |
| 0:50-1:15 | `--scenario hallucinated` | The agent guesses a target the user never named. Blocked, with the reason. |
| 1:15-1:45 | `--scenario injection` | The agent reads a poisoned log that tells it to delete a bucket. Tripwire sees the call comes from tool output, not the user. Blocked. |
| 1:45-2:05 | `--scenario ambiguous` | Medium confidence: the agent asks which instance. |
| 2:05-2:35 | Dashboard and `eval/results.md` | Lanes, latency, accuracy against a Bedrock judge, and where Decider is wrong. |
| 2:35-3:00 | `tripwire_pattern/` and repo link | Drop-in pattern for any Strands agent: ten lines. |

No copyrighted music or third-party logos. Upload as Public.
