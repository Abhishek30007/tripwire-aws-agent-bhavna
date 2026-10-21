#!/usr/bin/env bash
# One command for the real run: checks, tests, demo, benchmark, article.
#   VIDEO_URL=https://youtu.be/XXXX bash scripts/run_all.sh
set -euo pipefail
python -m scripts.check_setup
python -m pytest -q
python -m agent.demo
python -m eval.run_benchmark
python -m eval.make_article ${VIDEO_URL:+--video "$VIDEO_URL"}
echo "Done. Review eval/results.md and docs/article_final.md, then commit eval/ and docs/."
