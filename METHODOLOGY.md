# Methodology and evidence limits

## Scope

This dataset records DSA **coding** topics in screening online assessments for the requested companies, taken through IIT, NIT, IIIT, or BITS campus recruitment during **2023–2026**, through November 7, 2026. A computer-based OA supervised in a campus lab is included. A paper coding test whose online delivery is not established is held separately.

The campus may be explicitly unnamed if a candidate states that the drive was at an IIT or NIT. A subreddit name alone does not establish the author's institute. A college listed only as an exam venue does not establish campus recruitment. BIT Mesra, DTU, NSUT, and other institutions outside the requested groups are excluded from the main tables.

Quantitative aptitude, MCQs, SQL, frontend tasks, ML theory, debugging repositories, take-home projects, live interviews, and paper coding rounds do not contribute DSA OA topic rows. An MCQ-only OA can be retained as an evidence record with an empty topic list.

## Sources and search

Public candidate accounts, institute placement-office accounts, student-body interviews, and community OA reports provide the evidence. Commercial preparation pages and mirrors can identify leads but are not used to invent campus-specific historical patterns. Anonymous community reports remain unverified accounts of an OA; a readable source is not independent employer confirmation.

The recorded broad search sweep uses eight queries per company: four calendar-year searches and four institute-group searches. Targeted follow-ups examine dates, rounds, campus attribution, public attachments, and official difficulty references. Search-result metadata is a discovery queue, not proof of every claim in a page title.

That initial sweep did not fulfill the requested campus-by-campus depth. A subsequent 88-campus roster and 352 exact campus/year discovery queries are logged separately. That earlier sweep does not establish individual company/campus coverage. The newer full matrix audit below records those queries separately; neither audit establishes substantive review of every returned source.

The public archive was additionally scanned by company tags, with up to four result pages per tag. Its navigation/sidebar links include unrelated posts and duplicate entries. The index therefore must not be counted as a verified question bank. Separate access audits distinguish public pages, public excerpts, title-only records, and fetch failures. Public pages with a short body can contain useful ordinary public attachments.

The subsequent full [company/campus/year execution audit](MATRIX_SEARCHES.md) records each actually attempted query and returned source metadata, including unsuccessful attempts and executed retries. Four year-specific queries share a result pool in each company/campus request. Search execution is separate from source review and paper completeness.

No login-only content or premium body was accessed. Public PDF attachments were read transiently, with OCR and visual checks when needed. The delivered repository retains classifications and source links; source media and OCR transcripts are not retained. Public community-platform submissions remain source claims, not employer verification. An explicit OA date is distinguished from a platform upload/update date; an unlabelled date can remain unresolved. Generic placeholders on membership previews are not treated as real task content.

## Calendar years

An OA year is the year of the assessment, not the graduation, joining, internship, or article-update year. For example, an explicitly dated July 2024 OA for a summer 2025 internship belongs in **2024**. A GeeksforGeeks last-updated timestamp alone never establishes an OA year.

`year_basis` records explicit dates/titles or a stated inference. Contemporaneous reports, previous-year statements, and day/month plus original creation metadata sometimes support an inferred year; these are visible rather than presented as exact event dates. When inference remains too uncertain, `oa_year` is null and candidate years are retained only in the source record. Undated reports may predate this four-year window.

Conflicting role years and archive dates are documented. Readers who require only explicit event-year evidence can filter `year_basis` accordingly. Even exact event dates do not prove completeness of a company's paper pool.

## Topic observations

Each topic row is a **source observation**. A semicolon-separated topic field describes the relevant techniques for a recalled task or an aggregate topic group. Several techniques in one row are not several questions. Repeated reports can describe the same task or shared pool; rows across sources are not deduplicated into purported unique questions.

The dataset does not calculate true question frequencies or company probabilities from this convenience sample. A report describing four pool tasks does not establish that every candidate received four tasks. General preparation advice and later interview topics are not converted into OA observations.

## Difficulty

Official LeetCode levels are checked on the official problem page and retained with a reference URL. Matching may use a different story or data representation while preserving the algorithmic objective. Materially changed constraints or task objectives are classified as variants and estimated separately.

Custom tasks receive a clearly marked estimate based on constraints, required reasoning, and plausible efficient approaches. Author labels and whole-assessment ranges remain separate. Codeforces ratings are not mechanically converted into LeetCode levels. Missing constraints, ambiguous formulations, and unreadable formulas can require an Unknown rating.

## Coverage status

| Status | Meaning |
|---|---|
| `topics_found` | At least one qualifying dated topic observation, with partial coverage |
| `report_without_topics` | A qualifying coding OA report exists, but no specific topic was disclosed |
| `source_lead_gap` | A campus-related dated lead needs content review or has limited public access |
| `no_qualifying_public_evidence_found` | No qualifying dated coding evidence curated in this pass |

Every cell has `complete: false`. Title hints, inaccessible reports, and undated reports do not silently fill the main year tables. No public search method can substantiate the claim that all questions from all campuses have been found.
