"""
Example 1: Basic Regex Search

Demonstrates how to use DeepGrep for regex pattern matching.
"""

from deepgrep.core.engine import find_matches


def extract_emails(text: str):
    """Extract email addresses from text."""
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    matches = []
    
    for line in text.splitlines():
        line_matches = find_matches(line, pattern)
        matches.extend(line_matches)
    
    return matches


def extract_phone_numbers(text: str):
    """Extract phone numbers from text."""
    pattern = r"\d{3}-\d{3}-\d{4}"
    matches = []
    
    for line in text.splitlines():
        line_matches = find_matches(line, pattern)
        matches.extend(line_matches)
    
    return matches


def extract_dates(text: str):
    """Extract dates in YYYY-MM-DD format."""
    pattern = r"\d{4}-\d{2}-\d{2}"
    matches = []
    
    for line in text.splitlines():
        line_matches = find_matches(line, pattern)
        matches.extend(line_matches)
    
    return matches


if __name__ == "__main__":
    # Sample text
    sample_text = """
    Contact us at support@example.com or sales@company.org
    Phone: 123-456-7890 or 098-765-4321
    Meeting scheduled for 2024-01-15 at 10:00 AM
    Follow up on 2024-01-20
    """
    
    # Extract information
    emails = extract_emails(sample_text)
    phones = extract_phone_numbers(sample_text)
    dates = extract_dates(sample_text)
    
    print("Emails found:", emails)
    print("Phone numbers found:", phones)
    print("Dates found:", dates)
