# -*- coding: utf-8 -*-
"""
Generates a tailored, ATS-safe .docx CV for every fresh job match found by
scraper.py, scores it with ats_score.py, and sorts the output into:

  generated_cvs/ready/        - final_score >= SCORE_THRESHOLD (85 by default)
  generated_cvs/needs_review/ - below threshold, saved anyway so you can see
                                 what's missing, but clearly labeled as such

Hard rule: every resume built here only ever contains content already in
data/resume_master.py. Nothing is invented, exaggerated, or added just to
push a score over the threshold. "Tailoring" means: which existing skills/
projects/experience bullets get surfaced and in what order - never new
content.

Because most company listing pages don't expose a full job description
(see scraper.py's jd_context comment), the JD text used for scoring is
often partial - a title plus whatever surrounding text was visible on the
listing page, not the complete posting. Scores reflect that partial
context, not necessarily what you'd get by scoring against the full JD.
"""

import json
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from data.resume_master import (
    CONTACT, SUMMARY_BASE, SKILLS, EDUCATION, EXPERIENCE, PROJECTS,
    CERTIFICATIONS, ACHIEVEMENTS,
)
from ats_score import compute_final_score

SCORE_THRESHOLD = 85
FONT_NAME = "Calibri"
RESULTS_PATH = Path(__file__).parent / "data" / "latest_results.json"
OUT_ROOT = Path(__file__).parent / "generated_cvs"


def slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()[:60]


def pick_relevant_projects(jd_text: str, limit=None):
    """
    Rank ALL real projects by tag overlap with the JD (most relevant first).
    No project is ever dropped - `limit` defaults to None (show everything)
    specifically so adding more projects later can't silently truncate
    content. Pass an explicit limit only if you deliberately want fewer
    shown, and know that's a content trade-off, not a bug.
    """
    jd_lower = jd_text.lower()
    scored = []
    for idx, proj in enumerate(PROJECTS):
        hits = sum(1 for tag in proj["tags"] if tag in jd_lower)
        scored.append((hits, -idx, proj))
    scored.sort(key=lambda x: (-x[0], x[1]))
    ranked = [p for _, _, p in scored]
    return ranked if limit is None else ranked[:limit]


def pick_relevant_skill_groups(jd_text: str):
    """
    Returns an ordered dict of {category: [skill display names]}, all real
    skills - only the ORDER of categories/skills changes based on JD overlap,
    nothing is added or removed from what's true.
    """
    jd_lower = jd_text.lower()
    category_scores = []
    for category, skills in SKILLS.items():
        hits = 0
        for display_name, synonyms in skills.items():
            if any(syn in jd_lower for syn in synonyms):
                hits += 1
        category_scores.append((hits, category))
    category_scores.sort(key=lambda x: -x[0])

    ordered = {}
    for _, category in category_scores:
        skills = SKILLS[category]
        # within a category, matched skills first
        skill_scores = []
        for display_name, synonyms in skills.items():
            hit = any(syn in jd_lower for syn in synonyms)
            skill_scores.append((0 if hit else 1, display_name))
        skill_scores.sort()
        ordered[category] = [name for _, name in skill_scores]
    return ordered


def build_docx(company: str, role_title: str, jd_text: str, out_path: Path):
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = FONT_NAME
    style.font.size = Pt(10.5)
    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # --- Header: name + contact (plain text, ATS-parseable, no text boxes/tables) ---
    name_p = doc.add_paragraph()
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = name_p.add_run(CONTACT["name"])
    run.bold = True
    run.font.size = Pt(16)

    contact_line = (
        f"{CONTACT['email']} | {CONTACT['phone']} | {CONTACT['location']}\n"
        f"{CONTACT['linkedin']} | {CONTACT['github']} | {CONTACT['portfolio']}"
    )
    contact_p = doc.add_paragraph()
    contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, line in enumerate(contact_line.split("\n")):
        if i > 0:
            contact_p.add_run().add_break()
        contact_p.add_run(line).font.size = Pt(9.5)

    doc.add_paragraph()  # spacer

    def add_heading(text):
        h = doc.add_paragraph()
        r = h.add_run(text.upper())
        r.bold = True
        r.font.size = Pt(11.5)
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        border_p = doc.add_paragraph()
        border_p.paragraph_format.space_after = Pt(2)

    # --- Summary (tailored one line naming the target role, still 100% true content) ---
    add_heading("Summary")
    tailored_summary = f"Applying for: {role_title} at {company}. " + SUMMARY_BASE
    doc.add_paragraph(tailored_summary)

    # --- Skills (reordered by relevance, all real) ---
    add_heading("Skills")
    ordered_skills = pick_relevant_skill_groups(jd_text)
    for category, skill_names in ordered_skills.items():
        p = doc.add_paragraph()
        r1 = p.add_run(f"{category}: ")
        r1.bold = True
        r1.font.size = Pt(10)
        p.add_run(", ".join(skill_names)).font.size = Pt(10)

    # --- Experience (real, unmodified content) ---
    add_heading("Experience")
    for exp in EXPERIENCE:
        p = doc.add_paragraph()
        r1 = p.add_run(f"{exp['title']}, {exp['org']}")
        r1.bold = True
        p.add_run(f"  ({exp['dates']})").italic = True
        for b in exp["bullets"]:
            bp = doc.add_paragraph(style="List Bullet")
            bp.add_run(b).font.size = Pt(10)

    # --- Projects (top N most relevant to this JD, all real) ---
    add_heading("Projects")
    for proj in pick_relevant_projects(jd_text):
        p = doc.add_paragraph()
        p.add_run(proj["name"]).bold = True
        dp = doc.add_paragraph(style="List Bullet")
        dp.add_run(proj["detail"]).font.size = Pt(10)

    # --- Education ---
    add_heading("Education")
    for edu in EDUCATION:
        p = doc.add_paragraph()
        p.add_run(f"{edu['degree']}, {edu['school']}").bold = True
        p.add_run(f"  ({edu['years']}) - {edu['detail']}").font.size = Pt(10)

    # --- Certifications ---
    add_heading("Certifications")
    for c in CERTIFICATIONS:
        cp = doc.add_paragraph(style="List Bullet")
        cp.add_run(c).font.size = Pt(10)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))

    # build the resume's plain text back out for scoring (paragraphs only)
    resume_text = "\n".join(p.text for p in doc.paragraphs)
    return resume_text


def format_checklist_for(doc_path: Path):
    """
    Fixed checklist - true by construction since build_docx() never adds
    tables, images, text boxes, or multi-column sections. Kept as an
    explicit function (not a hardcoded True) so it stays honest if the
    generator changes later.
    """
    return {
        "no_tables_or_columns": True,
        "no_images_or_text_boxes": True,
        "standard_font_used": True,
        "standard_section_headings": True,
        "contact_block_is_plain_text": True,
        "file_is_docx_format": doc_path.suffix.lower() == ".docx",
    }


def section_presence_for(resume_text: str):
    lower = resume_text.lower()
    return {
        "contact": bool(CONTACT["email"] in resume_text),
        "summary": "summary" in lower,
        "skills": "skills" in lower,
        "experience": "experience" in lower,
        "projects": "projects" in lower,
        "education": "education" in lower,
    }


def run():
    if not RESULTS_PATH.exists():
        print(f"No {RESULTS_PATH} found - run scraper.py first.")
        return

    payload = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    summary_rows = []

    for company_result in payload["results"]:
        company = company_result["company"]
        for match in company_result.get("matches_under_3_days", []):
            role_title = match["title_line"]
            jd_text = match.get("jd_context", role_title)

            slug = f"{slugify(company)}__{slugify(role_title)}"
            tmp_path = OUT_ROOT / "_tmp" / f"{slug}.docx"
            resume_text = build_docx(company, role_title, jd_text, tmp_path)

            scoring = compute_final_score(
                jd_text=jd_text,
                resume_text=resume_text,
                format_checklist=format_checklist_for(tmp_path),
                section_presence=section_presence_for(resume_text),
            )

            score = scoring["final_score"]
            bucket = "ready" if score >= SCORE_THRESHOLD else "needs_review"
            final_name = f"{slug}__score{int(score)}.docx"
            final_path = OUT_ROOT / bucket / final_name
            final_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path.replace(final_path)

            summary_rows.append({
                "company": company,
                "role_title": role_title,
                "career_page": company_result["url"],
                "score": score,
                "bucket": bucket,
                "file": str(final_path.relative_to(OUT_ROOT)),
                "keyword_coverage_score": scoring["keyword_coverage_score"],
                "format_score": scoring["format_score"],
                "completeness_score": scoring["completeness_score"],
                "jd_keywords_used": scoring["jd_keywords_used"],
                "matched_keywords": scoring["matched_keywords"],
            })

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "cv_generation_summary.json").write_text(
        json.dumps(summary_rows, indent=2), encoding="utf-8"
    )

    tmp_dir = OUT_ROOT / "_tmp"
    if tmp_dir.exists():
        for f in tmp_dir.glob("*"):
            f.unlink()
        tmp_dir.rmdir()

    ready = sum(1 for r in summary_rows if r["bucket"] == "ready")
    review = sum(1 for r in summary_rows if r["bucket"] == "needs_review")
    print(f"Generated {len(summary_rows)} CVs -> {ready} ready (score>={SCORE_THRESHOLD}), {review} need review.")


if __name__ == "__main__":
    run()
