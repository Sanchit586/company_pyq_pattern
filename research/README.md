# Research records

The research is incomplete. These files make the reviewed evidence and the remaining gaps inspectable; they do not establish an exhaustive archive.

## Discovery and access

- [searches](searches): 104 search batches, eight queries per company across four years and four institution groups; result titles and links only. Search results can include irrelevant companies, old events, mirrors, or preparation material.
- [query_log.json](query_log.json): additional recorded search batches. Targeted follow-up and official difficulty checks also appear as URLs in curated records and difficulty references. This is not a claim that every search engine result was read.
- [campus_candidate_sources.json](campus_candidate_sources.json): campus-related candidate leads; discovery metadata only, not a source of inferred topics.
- [archive_index.json](archive_index.json): public company-tag index crawl. Repeated and unrelated navigation links remain for auditability. Neither per-company row counts nor repository timestamps establish question counts or event dates.
- [archive_access.json](archive_access.json): initial access checks of 69 campus-title leads.
- [archive_year_access.json](archive_year_access.json): additional access checks of 446 unique leads with 2023–2026 title hints. Access audit means the ordinary public page was fetched; substantive task review is reflected by curated report records.
- [exclusions.json](exclusions.json): selected reviewed sources rejected for institute, round, date, or content reasons.
- [difficulty_references.json](difficulty_references.json): official LeetCode pages whose difficulty labels were checked on November 6, 2026. Some checked comparisons were not used because the OA formulation was a variant.

The two access audits overlap. Their union, rather than their sum, is used in [summary counts](../data/summary.json). Archive public pages can include attachments rather than text; a short body is not automatically an access restriction. `public_excerpt` and `title_only` are retained without inferring hidden task content.

## Remaining work

All 208 company/year cells are partial. Major gaps include institutions not named by authors, role years with no OA dates, public accounts that disclose only overall difficulty, and title-only/premium source bodies. The company pages separate these from qualifying dated observations. This pass found substantially more usable historical detail for 2023 than later years; the sample is not balanced across years, companies, roles, or campuses.

Further additions should establish the exact assessment round, eligible institution or explicit institution group, calendar year, topic, and difficulty basis. Do not fill missing cells from a company's generic syllabus, an interview task, a joining year, or a page-update timestamp. There is no evidence-based stopping rule that can prove “nothing missed” across private campus OA pools.

## Optional fetching tools

Offline builds and validation need only Python's standard library. The following scripts are research helpers and require ordinary public network access:

```sh
python scripts/collect_archive_index.py
python scripts/review_archive_sources.py
python scripts/review_archive_sources.py --all-years
python scripts/review_archive_sources.py --ids 1835 --preview
```

The reviewer needs `beautifulsoup4`. Preview output is transient terminal text; it is not saved into the dataset. These commands overwrite discovery/audit metadata, so review changes before accepting a refresh.

`review_public_pdf.py` optionally downloads ordinary publicly linked PDF attachments into ignored `tmp/`, renders them with Poppler, and uses Windows OCR through `ocr_public_image.ps1`. It requires Windows and `pdfinfo`/`pdftoppm` in PATH. Remove its temporary PDFs/images after classification; the validator requires `tmp/` to be absent before delivery. No credentials, premium access, or paywall bypass are involved.
