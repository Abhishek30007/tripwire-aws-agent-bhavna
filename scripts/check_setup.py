"""Checks everything a real run needs.   python -m scripts.check_setup"""
import os
import sys

ok = True


def report(name, good, detail=""):
    global ok
    ok &= good
    print(f"[{'OK' if good else 'FAIL'}] {name} {detail}")


from tripwire_pattern import DeciderClient  # noqa: E402

d = DeciderClient()
info = d.info() if d.health() else {}
report("Decider server", bool(info), f"{info.get('checkpoint', '')} on {info.get('device', '')}" if info else
       "(start: strands-decider serve StrandsAgents/strands-decider-2B-hobson-v21 --port 8000)")
if info:
    try:
        a = d.assess("Start web-2 in staging.", "", "start_instance", {"instance_id": "web-2"})
        report("Decider answers", True, f"p_grounded={a.p_grounded:.2f}, {a.latency_ms:.0f} ms")
    except Exception as e:  # noqa: BLE001
        report("Decider answers", False, str(e))

try:
    import boto3
    client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    for var in ("BEDROCK_AGENT_MODEL_ID", "BEDROCK_JUDGE_MODEL_ID"):
        mid = os.getenv(var)
        if not mid:
            report(var, False, "(not set; see .env.example)")
            continue
        try:
            client.converse(modelId=mid, messages=[{"role": "user", "content": [{"text": "Say OK"}]}],
                            inferenceConfig={"maxTokens": 5})
            report(var, True, mid)
        except Exception as e:  # noqa: BLE001
            report(var, False, f"{mid}: {str(e)[:160]}")
except Exception as e:  # noqa: BLE001
    report("boto3 / AWS credentials", False, str(e)[:160])

print("\nReady for a real run." if ok else "\nFix the FAIL lines above, then run again.")
sys.exit(0 if ok else 1)
