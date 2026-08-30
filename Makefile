.PHONY: setup build-identity eval-mock eval-real eval-v2-mock eval-v2-real eval-v2-semantic eval-documents test clean

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

# v2.5 — generates an actual cover letter with each system. Uses hybrid
# retrieval (fastembed) so the real narrative-state/citation behavior shows.
eval-documents: build-identity
	.venv/bin/python scripts/run_eval_documents.py mock docs_mock fastembed

test:
	.venv/bin/python -m pytest tests/ -q

clean:
	rm -rf data/digital_self data/evaluation/results
