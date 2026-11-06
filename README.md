# Company OA topic and difficulty research

Topics and difficulty only, for the 52 requested companies and calendar years **2023, 2024, 2025, and 2026**. Institution scope: **IITs, NITs, IIITs, and BITS**. Research cutoff: **November 6, 2026**.

**This is a partial, source-backed public dataset. It is not an exhaustive collection of every campus OA.** Public evidence does not support filling every company/year cell, and 2026 is still in progress. Empty cells must not be interpreted as absence of an OA.

Start with the **[52-company coverage table](COVERAGE.md)**. Each company links to four year sections, topic/difficulty tables, source links, and evidence limitations.

## Files

| File | Purpose |
|---|---|
| [COVERAGE.md](COVERAGE.md) | Browse all 208 company/year cells |
| [data/topics.json](data/topics.json) | Qualifying dated campus OA topic observations |
| [data/unverified_topics.json](data/unverified_topics.json) | Useful topics with unresolved year, campus, or drive scope |
| [data/reports](data/reports) | Curated source records, including reports that disclose no specific OA topics |
| [data/coverage.json](data/coverage.json) | Coverage status for every company/year pair |
| [data/summary.json](data/summary.json) | Generated research and coverage counts |
| [METHODOLOGY.md](METHODOLOGY.md) | Inclusion rules, difficulty scale, and date handling |
| [research/README.md](research/README.md) | Search records, source access audits, and unresolved work |

No question statements, examples, solutions, screenshots, or source PDFs are included in the dataset. Source metadata can contain the original article title; LeetCode reference URLs identify the basis for an official rating.

## Reading difficulty

- `official_leetcode`: the source identifies a canonical task, or its objective matches one; the official LeetCode page was checked. This establishes that reference task's rating, not an employer-issued rating or independent verification that the OA occurred.
- `estimated`: a researcher estimate of Easy/Medium/Hard on the LeetCode scale for a custom task or variant. It is not an official LeetCode label.
- `reported`: the candidate author's label, which has not been independently established as an official LeetCode rating.
- `reported_range` / `reported_oa_range`: only a range is known. An assessment-wide range must not be read as an individual task's level.
- `unknown`: evidence is too vague, contradictory, or incomplete to assign a defensible single level.

The `difficulty` field is always Easy, Medium, Hard, or Unknown. An unresolved range is stored separately as `difficulty_range`. An accurate dataset needs Unknown values rather than invented ratings.

## Rebuild and validate

Python 3.10+ is sufficient for the offline build and checks:

```sh
python scripts/build_dataset.py
python scripts/validate_dataset.py
```

Edit curated report JSON files, then rebuild. Generated company pages and exports share the same source of truth. Research-fetching scripts are separate and require network access; see [research instructions](research/README.md).

The input spelling “Capital On” is normalized to **Capital One**. Brand aliases such as Zomato/Eternal, Facebook/Meta, and LTI/LTIMindtree are preserved in the company catalog.
