.PHONY: setup build-identity eval-mock eval-real eval-real-groq eval-v2-mock eval-v2-real eval-v2-real-groq eval-v2-semantic eval-documents eval-documents-real-groq eval-browser eval-browser-real-groq eval-security-demo test clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	.venv/bin/python -m playwright install chromium

build-identity:
	.venv/bin/python scripts/build_digital_self.py

eval-mock: build-identity
	.venv/bin/python scripts/run_eval.py mock v1_mock

# Requires ANTHROPIC_API_KEY (or set PROVIDER=openai + OPENAI_API_KEY) in .env
eval-real: build-identity
	.venv/bin/python scripts/run_eval.py anthropic v1_real

# Requires GROQ_API_KEY in .env — free, no credit card: https://console.groq.com/keys
eval-real-groq: build-identity
	.venv/bin/python scripts/run_eval.py groq v1_real_groq

# Runs all 5 systems: baseline_plain, baseline_rag, identityos_v2 (lexical),
# identityos_v2_semantic, identityos_v2_hybrid (recommended — see docs/evaluation_v2.md).
# EMBEDDING_PROVIDER=hash here means the two embedding-based arms are not
# meaningfully semantic yet (zero dependency, zero network).
eval-v2-mock: build-identity
	.venv/bin/python scripts/run_eval_v2.py mock v2_mock hash

# Real semantic embeddings (fastembed): downloads a ~65MB ONNX model on
# first run, cached under data/.embedding_cache/. No API key needed. This
# is what makes identityos_v2_semantic and identityos_v2_hybrid meaningful.
eval-v2-semantic: build-identity
	.venv/bin/python scripts/run_eval_v2.py mock v2_semantic fastembed

eval-v2-real: build-identity
	.venv/bin/python scripts/run_eval_v2.py anthropic v2_real fastembed

# Requires GROQ_API_KEY in .env — free, no credit card: https://console.groq.com/keys
eval-v2-real-groq: build-identity
	.venv/bin/python scripts/run_eval_v2.py groq v2_real_groq fastembed

# v2.5 — generates an actual cover letter with each system. Uses hybrid
# retrieval (fastembed) so the real narrative-state/citation behavior shows.
eval-documents: build-identity
	.venv/bin/python scripts/run_eval_documents.py mock docs_mock fastembed

# Requires GROQ_API_KEY in .env — free, no credit card: https://console.groq.com/keys
eval-documents-real-groq: build-identity
	.venv/bin/python scripts/run_eval_documents.py groq docs_real_groq fastembed

# v3 — fills the local synthetic application form (data/applications/local_demo/),
# verifies each field, and halts before submit (never submits — no --approve-submit
# flag is passed here; see scripts/run_browser_demo.py for that checkpoint).
eval-browser: build-identity
	.venv/bin/python scripts/run_browser_demo.py mock browser_mock fastembed

# Requires GROQ_API_KEY in .env — free, no credit card: https://console.groq.com/keys
eval-browser-real-groq: build-identity
	.venv/bin/python scripts/run_browser_demo.py groq browser_real_groq fastembed

# v3.2 — runs two adversarial local fixtures (mixed prompt-injection/
# identity-verification/off-topic attacks alongside legitimate fields, and
# a CAPTCHA-widget page) through the Security Policy Engine + Agent
# Auditor, and writes real evidence of detect/explain/block/continue —
# see docs/evaluation_browser.md's v3.2 addendum.
eval-security-demo: build-identity
	.venv/bin/python scripts/run_security_demo.py mock security_demo fastembed

test:
	.venv/bin/python -m pytest tests/ -q

clean:
	rm -rf data/digital_self data/evaluation/results
