.PHONY: setup build-identity eval-mock eval-real eval-v2-mock eval-v2-real test clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

build-identity:
	.venv/bin/python scripts/build_digital_self.py

eval-mock: build-identity
	.venv/bin/python scripts/run_eval.py mock v1_mock

# Requires ANTHROPIC_API_KEY (or set PROVIDER=openai + OPENAI_API_KEY) in .env
eval-real: build-identity
	.venv/bin/python scripts/run_eval.py anthropic v1_real

eval-v2-mock: build-identity
	.venv/bin/python scripts/run_eval_v2.py mock v2_mock

eval-v2-real: build-identity
	.venv/bin/python scripts/run_eval_v2.py anthropic v2_real

test:
	.venv/bin/python -m pytest tests/ -q

clean:
	rm -rf data/digital_self data/evaluation/results
