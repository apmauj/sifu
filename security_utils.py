"""
Security validation and sanitization utilities for SIFU API
"""
import re
import html
from typing import Any, Dict, List, Union

# XSS protection patterns
XSS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'vbscript:',
    r'on\w+\s*=',
    r'<iframe[^>]*>.*?</iframe>',
    r'<object[^>]*>.*?</object>',
    r'<embed[^>]*>.*?</embed>',
    r'<form[^>]*>.*?</form>',
    r'<input[^>]*>',
    r'<meta[^>]*>',
    r'<link[^>]*>',
    r'<style[^>]*>.*?</style>',
]

# SQL injection patterns (additional protection beyond SQLAlchemy)
SQL_INJECTION_PATTERNS = [
    r';\s*(drop|delete|update|insert|alter|create|truncate)\s',
    r'union\s+select',
    r'--',
    r'/\*.*?\*/',
]

class SecurityValidator:
    """Security validation and sanitization utilities"""

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input to prevent XSS attacks"""
        if not isinstance(input_str, str):
            return str(input_str)

        # Truncate if too long
        if len(input_str) > max_length:
            input_str = input_str[:max_length]

        # HTML escape
        sanitized = html.escape(input_str, quote=True)

        # Remove potentially dangerous patterns
        for pattern in XSS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)

        return sanitized.strip()

    @staticmethod
    def validate_no_injection(input_str: str) -> bool:
        """Check for potential SQL injection patterns"""
        if not isinstance(input_str, str):
            return True

        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                return False
        return True

    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize all string values in a dictionary"""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = SecurityValidator.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = SecurityValidator.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = SecurityValidator.sanitize_list(value)
            else:
                sanitized[key] = value
        return sanitized

    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """Sanitize all string values in a list"""
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(SecurityValidator.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(SecurityValidator.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(SecurityValidator.sanitize_list(item))
            else:
                sanitized.append(item)
        return sanitized

    @staticmethod
    def validate_date_string(date_str: str) -> bool:
        """Validate date string format to prevent injection"""
        if not isinstance(date_str, str):
            return False

        # Only allow YYYY-MM-DD format
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(date_pattern, date_str))

    @staticmethod
    def validate_currency_code(currency: str) -> bool:
        """Validate currency code format"""
        if not isinstance(currency, str):
            return False

        # Only allow 3-letter uppercase codes
        currency_pattern = r'^[A-Z]{3}$'
        return bool(re.match(currency_pattern, currency))

    @staticmethod
    def validate_numeric_string(num_str: str, allow_negative: bool = False) -> bool:
        """Validate numeric string to prevent injection"""
        if not isinstance(num_str, str):
            return False

        pattern = r'^-?\d+(\.\d+)?$' if allow_negative else r'^\d+(\.\d+)?$'
        return bool(re.match(pattern, num_str))

class InputValidator:
    """Input validation utilities"""

    @staticmethod
    def validate_range_params(start_date: str, end_date: str) -> tuple[bool, str]:
        """Validate date range parameters"""
        if not SecurityValidator.validate_date_string(start_date):
            return False, "Invalid start_date format. Use YYYY-MM-DD"

        if not SecurityValidator.validate_date_string(end_date):
            return False, "Invalid end_date format. Use YYYY-MM-DD"

        if start_date > end_date:
            return False, "start_date cannot be after end_date"

        return True, ""

    @staticmethod
    def validate_ur_range_params(start_year: Union[str, int], start_month: Union[str, int],
                                end_year: Union[str, int], end_month: Union[str, int]) -> tuple[bool, str]:
        """Validate UR range parameters"""
        try:
            # Convert to int if string
            if isinstance(start_year, str):
                if not SecurityValidator.validate_numeric_string(start_year, False):
                    return False, "Invalid start_year format"
                start_year = int(start_year)

            if isinstance(start_month, str):
                if not SecurityValidator.validate_numeric_string(start_month, False):
                    return False, "Invalid start_month format"
                start_month = int(start_month)

            if isinstance(end_year, str):
                if not SecurityValidator.validate_numeric_string(end_year, False):
                    return False, "Invalid end_year format"
                end_year = int(end_year)

            if isinstance(end_month, str):
                if not SecurityValidator.validate_numeric_string(end_month, False):
                    return False, "Invalid end_month format"
                end_month = int(end_month)

            # Validate ranges
            if not (1 <= start_month <= 12):
                return False, "start_month must be between 1 and 12"

            if not (1 <= end_month <= 12):
                return False, "end_month must be between 1 and 12"

            # Validate period order
            if (end_year < start_year) or (end_year == start_year and end_month < start_month):
                return False, "End period must be after start period"

            return True, ""

        except (ValueError, TypeError):
            return False, "Invalid parameter types"

    @staticmethod
    def validate_currency_param(currency: str) -> tuple[bool, str]:
        """Validate currency parameter"""
        if not SecurityValidator.validate_currency_code(currency):
            from constants import VALID_CURRENCY_CODES
            return False, f"Invalid currency code. Supported: {', '.join(VALID_CURRENCY_CODES)}"

        return True, ""

def sanitize_request_data(data: Union[Dict, List]) -> Union[Dict, List]:
    """Convenience function to sanitize request data"""
    if isinstance(data, dict):
        return SecurityValidator.sanitize_dict(data)
    elif isinstance(data, list):
        return SecurityValidator.sanitize_list(data)
    else:
        return data
