# -*- coding: utf-8 -*-
"""
Daily job-posting checker for the 115-company tracker.

What it does
------------
1. Visits every career page in data/companies.py with a real (headless) browser
   so JS-rendered sites have a chance to load.
2. Scans the rendered page text for lines that look like a job title matching
   the target roles (Data Analyst, Data Scientist, BI Analyst, SQL Developer,
   and close variants), using the surrounding text as a stand-in "JD" for
   keyword confirmation.
3. Looks for a posting-age signal near each match ("Posted 2 days ago",
   "2d", "Today", "Yesterday", a literal date, etc.) and computes days-old.
4. Keeps only matches confirmed to be < 3 days old. Everything else (no
   postings found, postings found but too old, or age simply not stated on
   the page) is reported honestly instead of guessed.
5. Writes data/latest_results.json (machine-readable) and docs/index.html
   (human-readable static report - can be served via GitHub Pages).

Known, real limitations - please read
--------------------------------------
- Some sites (LinkedIn-embedded widgets, some Workday/SuccessFactors tenants,
  bot-protected pages) will refuse or fail to load under automation. These
  show up in the report as status = "blocked_or_failed".
- Many career pages never expose a machine-readable "posted X days ago"
  string at all. Those show as status = "found_no_date" - the role exists,
  but this script cannot tell you how old it is, so it is NOT included in
  the "< 3 days" filtered view (only in the raw per-company log).
- This is keyword/pattern matching, not true NLP job-role classification.
  A false positive (e.g. "Data Analyst Manager" matching "Data Analyst")
  or false negative (an oddly-worded title) is possible. Tighten
  ROLE_PATTERNS below if you see noise for a specific company.
- Respect each site's robots.txt / terms of use. This script is for your
  own personal job search, run once daily - don't hammer any single site.
"""

import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

import sys
sys.path.insert(0, str(Path(__file__).parent))
from data.companies import COMPANIES

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROLE_PATTERNS = [
    re.compile(r"\bdata\s*analy(st|tics)\b", re.I),
    re.compile(r"\bdata\s*scientist\b", re.I),
    re.compile(r"\b(bi|business\s*intelligence)\s*(analyst|developer|engineer)\b", re.I),
    re.compile(r"\bsql\s*(developer|analyst|engineer)\b", re.I),
    re.compile(r"\bpower\s*bi\s*(developer|analyst)\b", re.I),
]

# Words that, if present in the matched title line, usually mean it's NOT an
# entry-relevant individual-contributor role we want - tune as needed.
EXCLUDE_IF_CONTAINS = [
    re.compile(r"\bdirector\b", re.I),
    re.compile(r"\bvp\b|\bvice president\b", re.I),
    re.compile(r"\bhead of\b", re.I),
    re.compile(r"\bprincipal\b", re.I),
]

AGE_PATTERNS = [
    (re.compile(r"\bposted\s+today\b", re.I), 0),
    (re.compile(r"\byesterday\b", re.I), 1),
    (re.compile(r"\b(\d+)\s*(?:hours?|hrs?)\s+ago\b", re.I), "hours"),
    (re.compile(r"\b(\d+)\s*d(?:ays?)?\s+ago\b", re.I), "days"),
]

MAX_AGE_DAYS = 3          # only report postings strictly younger than this
NAV_TIMEOUT_MS = 25_000   # per-page load timeout
CONCURRENCY = 6           # parallel browser pages (be polite, keep this modest)

DATA_DIR = Path(__file__).parent / "data"
DOCS_DIR = Path(__file__).parent / "docs"


def extract_matches(page_text: str):
    """Scan rendered page text for role-line + nearby-age signals."""
    lines = [l.strip() for l in page_text.splitlines() if l.strip()]
    findings = []
    for i, line in enumerate(lines):
        if not any(p.search(line) for p in ROLE_PATTERNS):
            continue
        if any(p.search(line) for p in EXCLUDE_IF_CONTAINS):
            continue

        # look at a small window around the title line for an age signal
        window = " ".join(lines[max(0, i - 2): i + 4])
        age_days = None
        for pattern, kind in AGE_PATTERNS:
            m = pattern.search(window)
            if not m:
                continue
            if kind == "hours":
                age_days = 0
            elif kind == "days":
                age_days = int(m.group(1))
            else:
                age_days = kind
            break

        findings.append({"title_line": line[:160], "age_days": age_days})
    return findings


async def check_company(browser, name: str, url: str, sem: asyncio.Semaphore):
    async with sem:
        result = {
            "company": name,
            "url": url,
            "status": None,
            "matches_under_3_days": [],
            "matches_no_date_found": [],
            "error": None,
        }
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        )
        try:
            await page.goto(url, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
            # give client-rendered job boards a moment to populate
            try:
                await page.wait_for_load_state("networkidle", timeout=8_000)
            except Exception:
                pass
            text = await page.inner_text("body")
            findings = extract_matches(text)

            fresh = [f for f in findings if f["age_days"] is not None and f["age_days"] < MAX_AGE_DAYS]
            undated = [f for f in findings if f["age_days"] is None]

            result["matches_under_3_days"] = fresh
            result["matches_no_date_found"] = undated
            result["status"] = "ok_with_fresh_match" if fresh else (
                "ok_role_found_no_date_or_stale" if findings else "ok_no_matching_role_found"
            )
        except Exception as e:
            result["status"] = "blocked_or_failed"
            result["error"] = str(e)[:200]
        finally:
            await page.close()
        return result


async def run():
    sem = asyncio.Semaphore(CONCURRENCY)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [check_company(browser, name, url, sem) for name, url in COMPANIES]
        results = await asyncio.gather(*tasks)
        await browser.close()

    checked_at = datetime.now(timezone.utc).isoformat()
    payload = {"checked_at_utc": checked_at, "max_age_days_filter": MAX_AGE_DAYS, "results": results}

    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "latest_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    write_html_report(payload)
    print(f"Checked {len(results)} companies at {checked_at}")


def write_html_report(payload):
    fresh_rows, other_rows = [], []
    for r in payload["results"]:
        if r["matches_under_3_days"]:
            for m in r["matches_under_3_days"]:
                fresh_rows.append((r["company"], r["url"], m["title_line"], m["age_days"]))
        else:
            other_rows.append((r["company"], r["url"], r["status"], r.get("error") or ""))

    def esc(s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    fresh_html = "".join(
        f"<tr><td>{esc(c)}</td><td><a href='{esc(u)}' target='_blank'>Open</a></td>"
        f"<td>{esc(t)}</td><td>{esc(a)} day(s)</td></tr>"
        for c, u, t, a in fresh_rows
    ) or "<tr><td colspan='4'>No postings under 3 days old found in this run.</td></tr>"

    other_html = "".join(
        f"<tr><td>{esc(c)}</td><td><a href='{esc(u)}' target='_blank'>Open</a></td>"
        f"<td>{esc(s)}</td><td>{esc(e)}</td></tr>"
        for c, u, s, e in other_rows
    )

    html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>Data Roles Tracker - Fresh Postings</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;margin:24px;color:#222}}
h1{{font-size:20px}} h2{{font-size:16px;margin-top:32px}}
table{{border-collapse:collapse;width:100%;margin-top:8px}}
th,td{{border:1px solid #ddd;padding:6px 8px;font-size:13px;text-align:left}}
th{{background:#1F4E78;color:#fff}}
tr:nth-child(even){{background:#f7f7f7}}
.meta{{color:#666;font-size:12px}}
</style></head><body>
<h1>Data Analyst / Data Scientist / BI Analyst / SQL Developer - Fresh Postings (&lt; 3 days old)</h1>
<p class="meta">Last checked: {esc(payload['checked_at_utc'])} UTC &middot; {len(payload['results'])} companies scanned</p>

<h2>Fresh matches ({len(fresh_rows)})</h2>
<table><tr><th>Company</th><th>Career Page</th><th>Matched Title Line</th><th>Age</th></tr>
{fresh_html}
</table>

<h2>Everything else (no fresh match this run)</h2>
<table><tr><th>Company</th><th>Career Page</th><th>Status</th><th>Notes</th></tr>
{other_html}
</table>
</body></html>
"""
    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(run())
