# -*- coding: utf-8 -*-
"""
Heuristic ATS-compatibility scorer.

IMPORTANT - what this score actually is
----------------------------------------
There is no public, universal "ATS score." Real ATS platforms (Workday,
Taleo, iCIMS, Greenhouse's own screen, etc.) each use their own undisclosed
ranking logic, and tools like Jobscan publish their own proprietary estimate
- not a shared standard. This module computes a transparent, reproducible
proxy score out of 100, built from three components that are broadly known
to matter for ATS parsing and keyword screening:

  1. Keyword coverage (60%) - of the meaningful keywords found in the job
     text, what fraction also appear in the generated resume? This is the
     single biggest lever real ATS keyword-screens use.
  2. Format compliance (25%) - fixed checklist (no tables/columns/text
     boxes/images, standard section headings, a parseable contact block,
     a standard font). Since we control generation, a correctly-built
     resume should score at or near full marks here every time.
  3. Section completeness (15%) - are the standard sections an ATS expects
     (Contact, Summary, Skills, Experience, Education) all present and
     non-empty?

final_score = 0.60*keyword_coverage + 0.25*format_score + 0.15*completeness_score

This is a best-effort proxy, not a guarantee of how any specific company's
real ATS will actually rank the document.
"""

import re

STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "will", "this",
    "that", "from", "have", "has", "who", "job", "role", "team", "work",
    "years", "year", "experience", "skills", "strong", "good", "ability",
    "including", "such", "using", "etc", "into", "about", "across", "per",
    "all", "any", "we", "in", "of", "to", "a", "an", "on", "as", "is",
    "be", "or", "at", "by", "an", "it", "their", "them", "they",
    # job-ad boilerplate that isn't a real skill/keyword
    "ago", "day", "days", "hour", "hours", "posted", "looking", "preferred",
    "plus", "apply", "now", "opening", "openings", "position", "positions",
    "candidate", "candidates", "required", "requirements", "responsibilities",
    "location", "remote", "hybrid", "onsite", "full-time", "part-time",
    # common India location names that leak into keyword extraction but
    # aren't skills
    "bengaluru", "bangalore", "hyderabad", "mumbai", "chennai", "pune",
    "delhi", "gurgaon", "noida", "karnataka", "telangana", "maharashtra",
}


def _tokenize(text: str):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}", text.lower())
    return [w.strip(".,-/") for w in words if w.strip(".,-/") and w not in STOPWORDS and len(w) > 2]


def extract_keywords(jd_text: str, max_keywords: int = 25):
    """
    Pull the most frequent meaningful tokens from the job text as a stand-in
    keyword set. This is intentionally simple (frequency-based, no external
    NLP model call) so it's fast, free, and fully inspectable.
    """
    tokens = _tokenize(jd_text)
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in ranked[:max_keywords]]


def keyword_coverage_score(jd_keywords, resume_text: str):
    if not jd_keywords:
        return 0.0, []
    resume_lower = resume_text.lower()
    hit = [kw for kw in jd_keywords if kw in resume_lower]
    coverage = (len(hit) / len(jd_keywords)) * 100
    return round(coverage, 1), hit


def format_compliance_score(checklist: dict):
    """checklist: dict of {check_name: bool}. All checks weighted equally."""
    if not checklist:
        return 0.0
    passed = sum(1 for v in checklist.values() if v)
    return round((passed / len(checklist)) * 100, 1)


def completeness_score(sections: dict):
    """sections: dict of {section_name: bool_non_empty}."""
    if not sections:
        return 0.0
    present = sum(1 for v in sections.values() if v)
    return round((present / len(sections)) * 100, 1)


def compute_final_score(jd_text: str, resume_text: str, format_checklist: dict, section_presence: dict):
    jd_keywords = extract_keywords(jd_text)
    kw_score, matched_keywords = keyword_coverage_score(jd_keywords, resume_text)
    fmt_score = format_compliance_score(format_checklist)
    comp_score = completeness_score(section_presence)

    final = round(0.60 * kw_score + 0.25 * fmt_score + 0.15 * comp_score, 1)
    return {
        "final_score": final,
        "keyword_coverage_score": kw_score,
        "format_score": fmt_score,
        "completeness_score": comp_score,
        "jd_keywords_used": jd_keywords,
        "matched_keywords": matched_keywords,
    }
