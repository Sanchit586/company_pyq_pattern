# Combination search records

Each company/campus batch contains four year-specific queries for 2023–2026, execution statuses, the search date, and a shared pool of source titles and URLs. No source question statements are stored.

The raw directory contains plain or gzip-compressed JSONL checkpoints. Consolidated files preserve original record order, including failed attempts and later successful retries. The reader counts each successful company/campus/year key once.

Run `python scripts/build_matrix_search_audit.py` to rebuild the execution audit, then rebuild and validate the dataset. Search execution does not establish complete source review or a complete OA question collection.
