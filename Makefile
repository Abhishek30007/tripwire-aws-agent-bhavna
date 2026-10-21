.PHONY: setup test demo check bench article dashboard
setup:      ; pip install -r requirements.txt
test:       ; python -m pytest -q
check:      ; python -m scripts.check_setup
demo:       ; python -m agent.demo
bench:      ; python -m eval.run_benchmark
article:    ; python -m eval.make_article
dashboard:  ; streamlit run dashboard/app.py
