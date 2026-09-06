# Data Roles Job Tracker (115 companies, daily @ midnight IST)

Automatically checks 115 companies' career pages every night for postings
matching **Data Analyst / Data Scientist / BI Analyst / SQL Developer** (and
close variants), and shows only postings it can confirm are **less than 3
days old**.

## What you get

- `data/companies.py` - the 115 companies + career page URLs.
- `scraper.py` - the checker (Playwright + keyword/date pattern matching).
- `.github/workflows/daily_job_check.yml` - runs `scraper.py` every day at
  **00:00 IST (18:30 UTC)** via GitHub Actions, and commits the results back
  to the repo.
- `docs/index.html` - the human-readable report (a plain HTML table).
  Regenerated every run.
- `data/latest_results.json` - the same data, machine-readable, if you want
  to build something on top of it later (Slack/Telegram alert, etc.)

## One-time setup (about 5 minutes)

1. Create a new **public** GitHub repo (private works too, but GitHub Pages
   on a private repo needs a paid plan).
2. Push everything in this folder to that repo's `main` branch.
3. In the repo: **Settings → Actions → General → Workflow permissions** →
   select **"Read and write permissions"**. (Without this, the workflow
   can't commit the daily report back.)
4. (Optional but recommended) **Settings → Pages** → Source: `Deploy from a
   branch` → Branch: `main`, folder: `/docs`. This gives you a live URL
   like `https://<your-username>.github.io/<repo-name>/` showing the latest
   report - open it on your phone anytime.
5. Go to the **Actions** tab → "Daily Job Posting Check" → **Run workflow**
   to trigger it manually the first time and confirm it works, instead of
   waiting for midnight.

That's it - after that it runs on its own every night.

## Reading the report

- **"Fresh matches" table**: role-line text the scraper found on a career
  page, matched to your target roles, with a confirmed age under 3 days.
  Click "Open" to go straight to that company's career page and search for
  it yourself (the scraper does not know exact job IDs/links on most sites,
  since most career pages load listings dynamically without stable per-job
  URLs in the raw page).
- **"Everything else" table**: every other company, with a status:
  - `ok_no_matching_role_found` - page loaded fine, nothing matched your
    role keywords right now.
  - `ok_role_found_no_date_or_stale` - a matching role IS on the page, but
    either its posting date is 3+ days old, or the page never states an age
    at all (very common - many ATS platforms don't show this).
  - `blocked_or_failed` - the page didn't load under automation (bot
    protection, login wall, or timeout). Check it manually.

## Please read - real limitations of this approach

1. **No single scraper works perfectly on 115 different websites.**
   Companies use wildly different platforms (Greenhouse, Lever, Workday,
   SuccessFactors, custom React apps, plain HTML). This script uses a
   generic "render the page, read the visible text, pattern-match" approach,
   which works reasonably well on simpler sites and poorly on heavy SPAs or
   bot-protected ones (expect Amazon, Google, LinkedIn-embedded widgets, and
   some bank ATS platforms to show up as `blocked_or_failed` or
   `ok_no_matching_role_found` even when jobs exist).
2. **"Days old" is often simply not on the page.** This script never
   invents an age - if it can't find explicit text like "Posted 2 days ago"
   near a matching title, it reports the role as found-but-undated rather
   than guessing, and it will NOT show up in the "< 3 days" filtered table.
3. **This is keyword matching, not true job-description understanding.**
   It reads the visible title/nearby text and checks it against role
   patterns in `scraper.py` (`ROLE_PATTERNS` / `EXCLUDE_IF_CONTAINS`) - it
   is not reading and reasoning over the full JD the way a person (or an
   LLM call per posting) would. You can tighten these patterns over time as
   you see false positives/negatives for specific companies.
4. **Be a good citizen.** This runs once a day per site, which is
   respectful of most sites' terms - don't lower `CONCURRENCY` timing or run
   it more frequently without checking each site's robots.txt.
5. **Expect to tune this.** Realistically, plan on checking the "Everything
   else" table occasionally and adjusting `ROLE_PATTERNS`/`AGE_PATTERNS` or
   adding a company-specific handler for sites that consistently fail - a
   generic scraper across 115 unrelated sites is a starting point, not a
   finished, maintenance-free product.

## Extending it (optional ideas for later)

- Add a Telegram/Slack webhook step in the workflow to push a message when
  `matches_under_3_days` is non-empty, instead of only updating the HTML.
- For companies you check often and that keep failing generically (e.g. a
  specific Workday tenant), add a small company-specific parser function in
  `scraper.py` and call it instead of the generic one for that company.
