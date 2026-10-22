import json

import pandas as pd
import pytest

from eval.splits import split
from tripwire_pattern import DeciderClient
from tripwire_pattern.decider_client import VARIANTS, render_state


def test_split_is_stratified_disjoint_and_complete():
    df = pd.read_csv("eval/cases.csv", keep_default_na=False)
    dev, test = split(df, "dev"), split(df, "test")
    assert len(dev) == 60 and len(test) == 60 and set(dev.index).isdisjoint(test.index)
    assert (dev.label.value_counts() == 15).all() and (test.label.value_counts() == 15).all()


def test_variants_are_valid_noul_questions_and_selectable(monkeypatch):
    for v in VARIANTS.values():
        assert v["grounded"]["type"] == "noul" and v["injected"]["type"] == "noul"
    monkeypatch.setenv("DECIDER_VARIANT", "v4")
    assert DeciderClient().variant == "v4"
    with pytest.raises(ValueError):
        DeciderClient(variant="nope")


def test_structured_state_is_a_dict_with_trusted_and_untrusted_parts():
    s = render_state("u", "o", "t", {"k": "v"}, structured=True)
    assert s["proposed_tool_call"]["arguments"] == {"k": "v"} and "untrusted" in " ".join(s)
    json.dumps(s)
