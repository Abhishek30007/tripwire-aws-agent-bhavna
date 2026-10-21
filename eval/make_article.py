"""Fill docs/article_template.md with numbers from a REAL benchmark run.

    python -m eval.make_article --video https://youtu.be/XXXX
Writes docs/article_final.md. Refuses to run on anything but a measured run.
"""
import argparse
import json
import re
import sys


def pct(x): return "n/a" if x is None else f"{100 * x:.1f}%"


def build(summary: dict, video: str | None, repo: str) -> str:
    m, d, c, j = summary["meta"], summary["decider"], summary["cascade"], summary["judge"]
    if m["mode"] != "real":
        raise SystemExit("summary.json is not from a real benchmark run. Run: python -m eval.run_benchmark")
    if j is None:
        raise SystemExit("Run the benchmark with the Bedrock judge (do not use --no-judge) so the article can compare them.")
    t = open("docs/article_template.md", encoding="utf-8").read()
    ratio = j["p50_ms"] / d["p50_ms"] if d["p50_ms"] else float("nan")
    more = "higher" if d["accuracy"] > j["accuracy"] else ("lower" if d["accuracy"] < j["accuracy"] else "the same")
    comparison = (f"On this set Decider's accuracy was {pct(d['accuracy'])} against {pct(j['accuracy'])} for the judge "
                  f"({more} for Decider). Its median round trip was {d['p50_ms']:.1f} ms against {j['p50_ms']:.0f} ms, "
                  f"about {ratio:.1f}x faster than the Bedrock call.")
    cost = (f"Estimated judge cost: ${j['cost_per_1k_usd']:.4f} per 1,000 decisions, from token counts and Bedrock list prices. "
            "Decider runs locally, so its marginal cost is compute only."
            if j["cost_per_1k_usd"] is not None else
            f"The judge used {j['input_tokens']} input and {j['output_tokens']} output tokens over {m['n_cases']} calls. "
            "Decider runs locally, so its marginal cost is compute only.")
    calib = "| Confidence | Cases | Share correct |\n|---|---|---|\n" + "\n".join(
        f"| {b['range']} | {b['n']} | {pct(b['accuracy'])} |" for b in summary["calibration"])
    fails = "\n".join(
        f"- **{f['label']}**: \"{f['user_message']}\" with `{f['tool']}({f['args']})`. "
        f"Decider gave p(grounded)={f['p_grounded']}, p(injected)={f['p_injected']}; Tripwire's final action: {f['action']}."
        for f in summary["failures"]) or "- Decider's single check classified every case correctly in this run."
    vals = {"N_CASES": m["n_cases"], "LABEL_COUNTS": ", ".join(f"{v} {k}" for k, v in m["label_counts"].items()),
            "CHECKPOINT": m.get("decider_checkpoint") or "strands-decider", "DEVICE": m.get("decider_device") or "local hardware",
            "JUDGE_MODEL": m.get("judge_model", "Amazon Bedrock model"), "DATE": m["date"],
            "D_ACC": pct(d["accuracy"]), "J_ACC": pct(j["accuracy"]),
            "D_P50": f"{d['p50_ms']:.1f} ms", "J_P50": f"{j['p50_ms']:.0f} ms",
            "D_P95": f"{d['p95_ms']:.1f} ms", "J_P95": f"{j['p95_ms']:.0f} ms",
            "COMPARISON": comparison, "COST": cost, "CALIBRATION": calib, "FAILURES": fails,
            "UNSAFE_ALLOWED": c["unsafe_allowed"], "N_UNSAFE": c["n_unsafe"], "SAFE_BLOCKED": c["safe_blocked"],
            "N_SAFE": c["n_safe"], "ASKED": c["asked"], "ESCALATED": c["escalated"],
            "REPO_LINK": repo, "VIDEO_LINK": video or "{{VIDEO_LINK}}"}
    for k, v in vals.items():
        t = t.replace("{{" + k + "}}", str(v))
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video")
    ap.add_argument("--repo", default="https://github.com/Bhavana0212/tripwire-aws-agent")
    ap.add_argument("--summary", default="eval/summary.json")
    a = ap.parse_args()
    text = build(json.load(open(a.summary)), a.video, a.repo)
    open("docs/article_final.md", "w", encoding="utf-8").write(text)
    left = sorted(set(re.findall(r"\{\{\w+\}\}", text)))
    print("Wrote docs/article_final.md")
    if left:
        print("Still to fill by hand:", ", ".join(left), file=sys.stderr)


if __name__ == "__main__":
    main()
