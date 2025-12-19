# Counting tokens and calculating costs for OpenAI API usage
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in text for a specific model using tiktoken.
    
    Args:
        text: Text to count tokens for
        model: OpenAI model name
        
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        # Fallback for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


def calculate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4o-mini") -> float:
    """
    Calculate API cost based on token usage.
    
    Pricing as of December 2024.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: OpenAI model name
        
    Returns:
        Total cost in USD
    """
    pricing = {
        "gpt-4o-mini": {"input": 0.150, "output": 0.600},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
    }
    
    rates = pricing.get(model, pricing["gpt-4o-mini"])
    
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    
    return input_cost + output_cost


def format_cost(cost: float) -> str:
    """
    Format cost for display.
    
    Args:
        cost: Cost in USD
        
    Returns:
        Formatted cost string
    """
    if cost < 0.01:
        return f"${cost:.4f}"
    return f"${cost:.2f}"


# Pricing reference (for documentation)
PRICING_INFO = {
    "gpt-4o-mini": {"input": "$0.150/1M tokens", "output": "$0.600/1M tokens"},
    "gpt-4o": {"input": "$2.50/1M tokens", "output": "$10.00/1M tokens"},
}
