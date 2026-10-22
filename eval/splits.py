"""Stratified dev/test split of eval/cases.csv (first half of each label = dev, rest = test)."""
import pandas as pd


def split(df: pd.DataFrame, which: str = "all") -> pd.DataFrame:
    if which == "all":
        return df
    parts = []
    for _, g in df.groupby("label", sort=True):
        g = g.sort_values(["user_message", "tool_args"], kind="stable")
        half = len(g) // 2
        parts.append(g.iloc[:half] if which == "dev" else g.iloc[half:])
    return pd.concat(parts).sort_index()
