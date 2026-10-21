import json

import pandas as pd
import pytest

from eval import make_article
from eval.run_benchmark import markdown, run
from tests.stubs import RuleStub
from tripwire_pattern.judge import JudgeResult


class FakeJudge:
    def judge(self, u, o, t, a): return JudgeResult(True, 250.0, 300, 3)


def _run(judge=None, mode="real"):
    cases = pd.read_csv("eval/cases.csv", keep_default_na=False)
    return run(cases, RuleStub(), judge, meta={"mode": mode, "judge_model": "fake"})


def test_benchmark_summary_has_all_sections():
    df, s = _run(FakeJudge())
    assert s["meta"]["n_cases"] == 120 and len(df) == 120
    assert 0 <= s["decider"]["accuracy"] <= 1 and s["judge"]["input_tokens"] == 120 * 300
    assert len(s["calibration"]) == 3 and s["cascade"]["n_unsafe"] == 90
    assert "Decider server" in markdown(s)


def test_article_refuses_unmeasured_summaries():
    _, s = _run(FakeJudge(), mode="stub")
    with pytest.raises(SystemExit):
        make_article.build(s, None, "https://example.com/repo")


def test_article_fills_every_token_from_measured_summary():
    _, s = _run(FakeJudge(), mode="real")
    text = make_article.build(s, "https://youtu.be/x", "https://github.com/Bhavana0212/tripwire-aws-agent")
    assert "{{" not in text and "https://youtu.be/x" in text and "Ayush Devani" in text
    assert "120 labeled cases" in text
