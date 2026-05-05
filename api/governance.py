import re
from datetime import datetime

PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b",
}

INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore all previous",
    "disregard your instructions", "you are now",
    "forget your training", "act as if", "pretend you are",
    "jailbreak", "bypass your", "override your",
    "new instructions:", "system prompt:",
]

OFF_TOPIC_KEYWORDS = [
    "how to make a bomb", "fraud", "insider trading",
    "manipulate stock", "pump and dump", "launder money",
    "evade taxes", "hack", "exploit"
]

audit_log = []


def detect_pii(text: str) -> list:
    return [pii_type for pii_type, pattern in PII_PATTERNS.items() if re.search(pattern, text)]


def detect_injection(text: str) -> bool:
    return any(pattern in text.lower() for pattern in INJECTION_PATTERNS)


def is_off_topic(text: str) -> bool:
    return any(keyword in text.lower() for keyword in OFF_TOPIC_KEYWORDS)


def validate_request(query: str) -> tuple:
    if detect_injection(query):
        return False, "Request blocked: Potential prompt injection detected."
    if is_off_topic(query):
        return False, "Request blocked: Query contains prohibited content."
    if len(query) > 2000:
        return False, "Request blocked: Query exceeds maximum length."
    if len(query.strip()) < 3:
        return False, "Request blocked: Query too short."
    return True, ""


def log_request(session_id: str, query: str, response: str,
                pii_detected: list, injection_detected: bool):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "query_length": len(query),
        "query_preview": query[:100] + "..." if len(query) > 100 else query,
        "pii_detected": pii_detected,
        "injection_detected": injection_detected,
        "response_length": len(response),
        "flagged": bool(pii_detected) or injection_detected
    }
    audit_log.append(entry)
    return entry


def get_audit_log():
    return audit_log
