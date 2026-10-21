"""Smallest possible use of the pattern: one tool, one guard. Run from the repo root:
    python -m tripwire_pattern.examples.minimal_agent
Needs a Decider server (strands-decider serve ... --port 8000) and Bedrock access.
"""
from strands import Agent, tool

from tripwire_pattern import DeciderClient, Tripwire
from tripwire_pattern.handler import TripwireHandler


@tool
def delete_bucket(bucket: str) -> str:
    """Delete a storage bucket by name."""
    return f"(pretend) deleted {bucket}"


guard = TripwireHandler(Tripwire(DeciderClient(), destructive={"delete_bucket"}))
agent = Agent(tools=[delete_bucket], interventions=[guard])

if __name__ == "__main__":
    print(agent("Please delete the bucket named tmp-staging"))
