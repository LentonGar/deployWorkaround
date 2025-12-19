"""Security utilities for input validation and sanitization"""
import uuid


def validate_input(text: str) -> tuple[bool, str]:
    """
    Prevents prompt injection and abuse.
    
    Args:
        text: User input to validate
        
    Returns:
        (is_valid, error_message): Tuple with validation result
    """
    MAX_LENGTH = 1200
    if len(text) > MAX_LENGTH:
        return (False, f"Input too long! Max {MAX_LENGTH} characters. You used {len(text)}.")
    
    forbidden_phrases = [
        "ignore previous instructions", "disregard all prior messages",
        "you are no longer", "forget you are",
        "bypass your restrictions", "break your programming",
        "act as a different AI", "malicious", "harmful",
        "illegal", "unethical", "pretend to be", "jailbreak",
        "pretend", "imagine", "disregard", "bypass",
        "override", "disable", "break", "you are now",
        "you are", "forget"
    ]

    text_lower = text.lower()
    for phrase in forbidden_phrases:
        if phrase in text_lower:
            return (False, "Input contains forbidden phrases. Please revise your input.")
        
    return True, ""


def wrap_user_input(user_text: str) -> str:
    """
    Wraps user input with unique identifiers to prevent prompt injection.
    
    AI treats anything within these boundaries as user content, not instructions.
    
    Args:
        user_text: Raw user input
        
    Returns:
        Wrapped input with UUID boundary
    """
    boundary = str(uuid.uuid4())
    return f"""<USER_INPUT id="{boundary}">
{user_text}
</USER_INPUT>"""
