# backend/app/services/nlp.py
"""
NLP helpers for resume parsing (Day 2)
- extract_name(text, skills_list): robust header + spaCy fallback with skill filtering
- extract_experience_years(text): parse "X years", month-year ranges, and year ranges
- match_skills(text, skills_list): find skills from a provided list
"""

import re
from typing import List, Optional
from datetime import datetime

# Try to load spaCy model (optional). If unavailable, functions will fallback gracefully.
try:
    import spacy
    _SPACY_NLP = spacy.load("en_core_web_sm")
except Exception:
    _SPACY_NLP = None

# Keywords that indicate a line is a header for skills/tools/education etc.
_BAD_NAME_KEYWORDS = re.compile(
    r'\b(skills?|technical|languages?|frameworks?|tools?|libraries?|education|experience|projects|courses?|certifications?)\b',
    flags=re.I
)


def _looks_like_skill_list(line: str, skills_list: Optional[List[str]] = None) -> bool:
    """Return True if the line appears to be a skills/header line rather than a personal name."""
    if not line or len(line.strip()) == 0:
        return True
    # header keywords (e.g., "Technical Skills", "Frameworks")
    if _BAD_NAME_KEYWORDS.search(line):
        return True

    # if the line contains separators and many tokens, and some match skills, treat as skill line
    separators_count = line.count(',') + line.count('/') + line.count('|') + line.count(';')
    if separators_count >= 1:
        tokens = re.split(r'[,\|/;]+|\s{2,}', line)
        found = 0
        for t in tokens:
            t_clean = t.strip().lower()
            if not t_clean:
                continue
            if skills_list and any(t_clean == s.lower() for s in skills_list):
                found += 1
        if found >= 1:
            return True

    # if the line is mostly non-alpha (low alpha ratio), it's likely not a name
    alpha_chars = sum(1 for ch in line if ch.isalpha())
    if alpha_chars / max(1, len(line)) < 0.5:
        return True

    return False


def _clean_name_candidate(s: str) -> Optional[str]:
    """Normalize a name candidate: strip punctuation, collapse spaces, limit length."""
    if not s:
        return None
    # remove stray punctuation except hyphen
    s = re.sub(r'[^\w\s\-]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    parts = s.split()
    # typical name length 1-4 words; reject too long or empty
    if len(parts) == 0 or len(parts) > 4:
        return None
    # reject if parts are mostly non-alpha
    if not any(p.isalpha() for p in parts):
        return None
    # Title-case each part for nicer output
    return " ".join(p.capitalize() for p in parts)

def extract_name(text: str, skills_list: Optional[List[str]] = None) -> Optional[str]:
    """
    Improved name extraction prioritizing Title-Case sequences.
    Steps:
      1) Look at top 6 lines (header area). Remove emails/phones and search for Title-Case sequences.
      2) If not found, use the line before contact (email/phone).
      3) If not found, try the first line.
      4) Finally, fallback to spaCy PERSON if available.
    Filters:
      - Exclude candidates that match known skills or header keywords.
      - Return 1-3 word candidate (title-cased).
    """
    if not text or not text.strip():
        return None

    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", flags=re.I)
    phone_re = re.compile(r"\+?\d[\d\-\s]{6,}\d")
    header_bad = re.compile(r'\b(skills?|technical|languages?|frameworks?|tools?|education|experience|projects|courses?|certifications?)\b', flags=re.I)

    def is_skill_candidate(s: str) -> bool:
        if not s:
            return False
        s_norm = s.strip().lower()
        if skills_list and any(s_norm == sk.lower() for sk in skills_list):
            return True
        return False

    def title_case_candidates(s: str) -> List[str]:
        """
        Return list of candidate name strings found via Title-Case regex.
        Matches sequences of 1-3 words starting with uppercase letter followed by lowercase letters.
        """
        # Normalize separators to spaces
        s = re.sub(r'[\|\-\/\·\•,]+', ' ', s)
        # Find sequences: e.g., "Onkesh Gupta" or "John A Smith"
        pattern = re.compile(r'\b([A-Z][a-z]{1,}\b(?:\s+[A-Z][a-z]{1,}\b){0,2})')
        return [m.group(1).strip() for m in pattern.finditer(s)]

    # split and trim lines
    lines = [ln.strip() for ln in text.splitlines() if ln and ln.strip()]
    # Look in top header area (first 6 lines) for title-case names after removing contact tokens
    header_area = lines[:6]
    for ln in header_area:
        if not ln:
            continue
        # remove emails and phones in that line
        ln_clean = email_re.sub('', ln)
        ln_clean = phone_re.sub('', ln_clean)
        # search for Title-Case sequences
        cand_list = title_case_candidates(ln_clean)
        for cand in cand_list:
            # basic filters
            if header_bad.search(cand):
                continue
            if is_skill_candidate(cand):
                continue
            parts = cand.split()
            if 1 <= len(parts) <= 3:
                return " ".join(p.capitalize() for p in parts)

    # 2) Try line before contact (email/phone)
    contact_idx = None
    for i, ln in enumerate(lines):
        if email_re.search(ln) or phone_re.search(ln):
            contact_idx = i
            break
    if contact_idx is not None and contact_idx > 0:
        candidate_line = lines[contact_idx - 1]
        # remove separators, then check title-case patterns
        candidate_line_clean = email_re.sub('', candidate_line)
        candidate_line_clean = phone_re.sub('', candidate_line_clean)
        cand_list = title_case_candidates(candidate_line_clean)
        for cand in cand_list:
            if header_bad.search(cand):
                continue
            if is_skill_candidate(cand):
                continue
            parts = cand.split()
            if 1 <= len(parts) <= 3:
                return " ".join(p.capitalize() for p in parts)
        # if no title-case found, take sanitized tokens as fallback
        tokens = [t for t in re.split(r'[\s\|\/,]+', candidate_line_clean) if t and re.search(r'[A-Za-z]', t)]
        if tokens:
            # filter skill tokens
            tokens = [t for t in tokens if not is_skill_candidate(t)]
            if tokens:
                cand = " ".join(tokens[:3])
                if not header_bad.search(cand):
                    return " ".join(p.capitalize() for p in re.sub(r'[^\w\s\-]', ' ', cand).split())

    # 3) First-line fallback (similar to header)
    if lines:
        first = lines[0]
        first_clean = email_re.sub('', first)
        first_clean = phone_re.sub('', first_clean)
        cand_list = title_case_candidates(first_clean)
        for cand in cand_list:
            if header_bad.search(cand):
                continue
            if is_skill_candidate(cand):
                continue
            parts = cand.split()
            if 1 <= len(parts) <= 3:
                return " ".join(p.capitalize() for p in parts)
        # fallback: take first token group not skill-like
        tokens = [t for t in re.split(r'[\s\|\/,]+', first_clean) if t and re.search(r'[A-Za-z]', t)]
        tokens = [t for t in tokens if not is_skill_candidate(t)]
        if tokens:
            cand = tokens[0]
            if not header_bad.search(cand):
                return cand.capitalize()

    # 4) spaCy fallback
    if _SPACY_NLP:
        try:
            doc = _SPACY_NLP(text[:2000])
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    cand = ent.text.strip()
                    if not cand:
                        continue
                    if header_bad.search(cand):
                        continue
                    if is_skill_candidate(cand):
                        continue
                    parts = cand.split()
                    if 1 <= len(parts) <= 3:
                        return " ".join(p.capitalize() for p in parts)
        except Exception:
            pass

    return None


# ---------------- Experience extraction ----------------

_MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}


def _parse_month_year(s: str) -> Optional[datetime]:
    """Parse strings like 'May 2020' or 'May, 2020' -> datetime(year, month, 1)."""
    if not s or not s.strip():
        return None
    s = s.strip()
    m = re.search(r'([A-Za-z]{3,9})[\s\.\-/,]*(\d{4})', s)
    if m:
        mon = m.group(1)[:3].lower()
        yr = int(m.group(2))
        mon_key = mon[:3]
        if mon_key in _MONTHS:
            return datetime(yr, _MONTHS[mon_key], 1)
    # fallback: just a four-digit year
    m2 = re.search(r'\b(20\d{2})\b', s)
    if m2:
        return datetime(int(m2.group(1)), 1, 1)
    return None


def extract_experience_years(text: str) -> Optional[float]:
    """
    Extract total professional experience in years.

    ✔ Considers ONLY experience-related sections
    ✔ Ignores education timelines (e.g., 2022–2026)
    ✔ Supports:
        - "X years" / "X.X years"
        - Month–year ranges (May 2019 - Jul 2021)
        - Year ranges (2018 - 2021)
    ✔ Returns float years rounded to 1 decimal
    """

    if not text:
        return None

    text_lower = text.lower()

    # --------------------------------------------------
    # 1️⃣ Identify EXPERIENCE sections only
    # --------------------------------------------------
    experience_section_patterns = [
        r"experience",
        r"work experience",
        r"professional experience",
        r"employment",
        r"internship",
        r"work history"
    ]

    lines = text.splitlines()
    experience_lines = []
    capture = False

    for line in lines:
        line_lower = line.lower()

        # Start capturing when experience section begins
        if any(pat in line_lower for pat in experience_section_patterns):
            capture = True
            continue

        # Stop capturing if we hit education / skills section
        if capture and re.search(
            r"\b(education|skills|projects|certifications|courses|languages)\b",
            line_lower
        ):
            break

        if capture:
            experience_lines.append(line)

    experience_text = "\n".join(experience_lines)

    if not experience_text.strip():
        return None

    # --------------------------------------------------
    # 2️⃣ Direct "X years" extraction
    # --------------------------------------------------
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*\+?\s*(years|yrs|year|yr)\b",
        experience_text,
        flags=re.I
    )
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass

    total_months = 0

    # --------------------------------------------------
    # 3️⃣ Month–Year ranges (May 2019 - Jul 2021)
    # --------------------------------------------------
    ranges = re.findall(
        r"([A-Za-z]{3,9}\s*\d{4})\s*[\-\u2013\u2014to]{1,4}\s*([A-Za-z]{3,9}\s*\d{4}|present|current)",
        experience_text,
        flags=re.I
    )

    now = datetime.utcnow()

    for start_s, end_s in ranges:
        start_dt = _parse_month_year(start_s)

        if re.search(r"present|current", end_s, flags=re.I):
            end_dt = now
        else:
            end_dt = _parse_month_year(end_s)

        if start_dt and end_dt and end_dt >= start_dt:
            months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
            total_months += max(months, 0)

    # --------------------------------------------------
    # 4️⃣ Year-only ranges (2018 - 2021)
    # --------------------------------------------------
    year_ranges = re.findall(
        r"\b(20\d{2})\s*[\-–—]\s*(20\d{2}|present|current)\b",
        experience_text,
        flags=re.I
    )

    for ys, ye in year_ranges:
        try:
            start_year = int(ys)
            end_year = now.year if re.search(r"present|current", ye, flags=re.I) else int(ye)
            if end_year >= start_year:
                total_months += (end_year - start_year) * 12
        except ValueError:
            pass

    # --------------------------------------------------
    # 5️⃣ Final calculation
    # --------------------------------------------------
    if total_months > 0:
        return round(total_months / 12.0, 1)

    return None


# ---------------- Skills matching ----------------

def match_skills(text: str, skills_list: List[str]) -> List[str]:
    """
    Return a list of skills found in `text` based on `skills_list`.
    Matching is case-insensitive and uses whole-word boundaries.
    """
    if not text or not skills_list:
        return []
    text_lower = text.lower()
    found = []
    # iterate skills_list in given order and collect matches
    for s in skills_list:
        s_clean = s.strip().lower()
        if not s_clean:
            continue
        # match whole word (handles multi-word skills due to \b boundaries)
        if re.search(r'\b' + re.escape(s_clean) + r'\b', text_lower):
            found.append(s)
    return found