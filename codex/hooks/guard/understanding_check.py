"""Focus direct understanding checks on answering the check first."""

from __future__ import annotations

import re

from .common import add_context, env_enabled

FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")
QUOTED_TEXT_RE = re.compile(r"\"[^\"\n]*\"|(?<!\w)'[^'\n]*'(?!\w)")
BLOCK_QUOTE_RE = re.compile(r"(?m)^\s*>.*$")
UNDERSTANDING_PHRASE_RE = re.compile(
    r"\b(?:"
    r"do\s+(?:you|u)\s+(?:understand|know)\s+what\s+i\s+mean"
    r"|do\s+(?:you|u)\s+understand\s+me"
    r"|you\s+know\s+what\s+i\s+mean"
    r"|know\s+what\s+i\s+mean"
    r")\b",
    re.IGNORECASE,
)
UNDERSTANDING_ABBREVIATION_RE = re.compile(
    r"\b(?:dykwim|dywim|ykwim)\b",
    re.IGNORECASE,
)
UNDERSTANDING_CONTEXT = (
    "Understanding-check override: make this turn about answering the user's "
    "understanding check, not carrying out other requested work. Inspect the "
    "repo or search the web if needed to understand the reference. Then state "
    "whether you understand, restate the likely meaning in 1 to 3 sentences, "
    "and name any remaining ambiguity."
)
PHRASE_DISCUSSION_BEFORE_RE = re.compile(
    r"(?:"
    r"\b(?:example|fixture|quoted?)\b"
    r"|\b(?:review|spec|verify)\s+(?:if|whether)\b"
    r"|\bphrases?\s+like\b"
    r"|\b(?:the|this|that)\s+(?:phrase|term|text|wording)\b"
    r"|\bhook\s+(?:off\s+of|for|on|around)\b"
    r"|\btrigger\s+(?:on|when|for)\b"
    r"|\b(?:literal|match(?:er)?|regex|string)\b"
    r")",
    re.IGNORECASE,
)
FIRST_PERSON_BEFORE_RE = re.compile(
    r"\b(?:i|we)\s+(?:(?:do\s+not|don't|dont|did\s+not|didn't|didnt)\s+)?$",
    re.IGNORECASE,
)
PHRASE_DISCUSSION_AFTER_RE = re.compile(
    r"\b(?:"
    r"acronym|detect|detection|docs?|example|fixture|hook|literal|match(?:er)?|"
    r"phrase|quoted?|regex|string|support(?:ed)?|tests?|trigger|is|means?|"
    r"refers?|should"
    r")\b",
    re.IGNORECASE,
)
TERM_DEFINITION_RE = re.compile(
    r"\b(?:what\s+(?:does|is)|what\s+do\s+you\s+mean\s+by|define|meaning\s+of)\b",
    re.IGNORECASE,
)
QUALIFIED_CHECK_AFTER_RE = re.compile(
    r"\s+(?:about|around|as|by|for|from|on|regarding|with)\b",
    re.IGNORECASE,
)


def strip_examples(text: str) -> str:
    without_code = INLINE_CODE_RE.sub(" ", FENCED_CODE_RE.sub(" ", text))
    without_quotes = QUOTED_TEXT_RE.sub(" ", without_code)
    return BLOCK_QUOTE_RE.sub(" ", without_quotes)


def sentence_context(text: str, start: int, end: int) -> str:
    before = re.split(r"[.?!;\n]", text[:start])[-1]
    after = re.split(r"[.?!;\n]", text[end:], maxsplit=1)[0]
    return f"{before} {after}"


def is_phrase_discussion(text: str, start: int, end: int) -> bool:
    before = re.split(r"[.?!;\n]", text[:start])[-1]
    after = re.split(r"[.?!;\n]", text[end:], maxsplit=1)[0]
    return bool(
        PHRASE_DISCUSSION_BEFORE_RE.search(before)
        or PHRASE_DISCUSSION_AFTER_RE.search(after)
    )


def is_term_definition_query(text: str, start: int, end: int) -> bool:
    context = sentence_context(text, start, end)
    return bool(
        TERM_DEFINITION_RE.search(context)
        or re.match(r"\s+means?\b", text[end:], re.IGNORECASE)
    )


def check_looks_direct(text: str, start: int, end: int) -> bool:
    if is_phrase_discussion(text, start, end) or is_term_definition_query(text, start, end):
        return False
    if FIRST_PERSON_BEFORE_RE.search(text[:start]):
        return False

    after = text[end:]
    or_not = re.match(r"\s+or\s+not\b(.*)$", after, re.IGNORECASE)
    if or_not:
        return or_not.group(1).strip(" \t\r\n?!.,;:)]}") == ""
    next_clause = re.split(r"[.;\n]", after, maxsplit=1)[0]
    if "?" in next_clause:
        return True
    if QUALIFIED_CHECK_AFTER_RE.match(next_clause):
        return True
    return after.strip(" \t\r\n?!.,;:)]}") == ""


def has_understanding_check(prompt: str) -> bool:
    text = strip_examples(prompt)
    for match in UNDERSTANDING_PHRASE_RE.finditer(text):
        if check_looks_direct(text, match.start(), match.end()):
            return True
    return any(
        check_looks_direct(text, match.start(), match.end())
        for match in UNDERSTANDING_ABBREVIATION_RE.finditer(text)
    )


def understanding_check_context(data: dict) -> bool:
    if env_enabled("CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK"):
        return False

    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not has_understanding_check(prompt):
        return False

    add_context("UserPromptSubmit", UNDERSTANDING_CONTEXT)
    return True


HANDLERS = {"UserPromptSubmit": understanding_check_context}
