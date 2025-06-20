"""Helper utilities and common functions."""

import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

# Setup logging
logger = logging.getLogger(__name__)


def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input by trimming and limiting length."""
    if not isinstance(value, str):
        value = str(value)
    
    # Trim whitespace
    value = value.strip()
    
    # Limit length if specified
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def parse_decimal(value: Any, precision: int = 2) -> Optional[Decimal]:
    """Parse value to Decimal with error handling."""
    if value is None:
        return None
    
    try:
        if isinstance(value, str):
            # Remove any non-numeric characters except decimal point and minus
            cleaned = re.sub(r'[^\d.-]', '', value)
            if not cleaned:
                return None
            value = cleaned
        
        decimal_value = Decimal(str(value))
        
        # Round to specified precision
        if precision >= 0:
            quantize_value = Decimal('0.' + '0' * precision)
            decimal_value = decimal_value.quantize(quantize_value)
        
        return decimal_value
        
    except (InvalidOperation, ValueError, TypeError):
        return None


def parse_integer(value: Any) -> Optional[int]:
    """Parse value to integer with error handling."""
    if value is None:
        return None
    
    try:
        if isinstance(value, str):
            # Remove any non-numeric characters except minus
            cleaned = re.sub(r'[^\d-]', '', value)
            if not cleaned:
                return None
            value = cleaned
        
        return int(float(value))
        
    except (ValueError, TypeError):
        return None


def normalize_category(category: str) -> str:
    """Normalize category name for consistency."""
    if not category:
        return ""
    
    # Clean and capitalize each word
    words = category.strip().split()
    normalized_words = [word.capitalize() for word in words if word]
    
    return " ".join(normalized_words)


def normalize_sku(sku: str) -> str:
    """Normalize SKU for consistency."""
    if not sku:
        return ""
    
    # Convert to uppercase and remove spaces
    return sku.strip().upper().replace(" ", "")


def parse_tags(tags_input: Any) -> Optional[Dict[str, List[str]]]:
    """Parse tags from various input formats."""
    if not tags_input:
        return None
    
    try:
        if isinstance(tags_input, str):
            # Split by comma and clean each tag
            tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            if tags_list:
                return {"tags": tags_list}
        
        elif isinstance(tags_input, list):
            # Already a list, just clean it
            tags_list = [str(tag).strip() for tag in tags_input if str(tag).strip()]
            if tags_list:
                return {"tags": tags_list}
        
        elif isinstance(tags_input, dict):
            # Already a dict, validate it has the right structure
            if "tags" in tags_input and isinstance(tags_input["tags"], list):
                return tags_input
    
    except Exception as e:
        logger.warning(f"Error parsing tags: {e}")
    
    return None


def format_price(price: Decimal) -> str:
    """Format price for display."""
    if price is None:
        return "$0.00"
    
    return f"${price:.2f}"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime for display."""
    if dt is None:
        return ""
    
    return dt.strftime(format_str)


def calculate_pagination(total: int, page: int, size: int) -> Dict[str, int]:
    """Calculate pagination metadata."""
    if size <= 0:
        size = 20
    
    if page <= 0:
        page = 1
    
    pages = (total + size - 1) // size
    offset = (page - 1) * size
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "offset": offset,
        "has_next": page < pages,
        "has_prev": page > 1
    }


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension."""
    if not filename:
        return False
    
    file_ext = filename.lower().split('.')[-1]
    return f".{file_ext}" in [ext.lower() for ext in allowed_extensions]


def generate_sku(name: str, category: str = "", sequence: int = 1) -> str:
    """Generate a SKU from product name and category."""
    # Take first 3 characters of name (letters only)
    name_part = re.sub(r'[^a-zA-Z]', '', name.upper())[:3].ljust(3, 'X')
    
    # Take first 2 characters of category (letters only)
    category_part = re.sub(r'[^a-zA-Z]', '', category.upper())[:2].ljust(2, 'X')
    
    # Add sequence number
    sequence_part = f"{sequence:04d}"
    
    return f"{name_part}{category_part}{sequence_part}"


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
    """Mask sensitive fields in a dictionary."""
    masked_data = data.copy()
    
    for field in sensitive_fields:
        if field in masked_data:
            value = masked_data[field]
            if isinstance(value, str) and len(value) > 4:
                masked_data[field] = value[:2] + "*" * (len(value) - 4) + value[-2:]
            else:
                masked_data[field] = "***"
    
    return masked_data


class ErrorCollector:
    """Helper class to collect and manage validation errors."""
    
    def __init__(self):
        """Initialize error collector."""
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def add_error(self, field: str, message: str, row: Optional[int] = None) -> None:
        """Add an error."""
        error_dict = {"field": field, "message": message}
        if row is not None:
            error_dict["row"] = row
        self.errors.append(error_dict)
    
    def add_warning(self, field: str, message: str, row: Optional[int] = None) -> None:
        """Add a warning."""
        warning_dict = {"field": field, "message": message}
        if row is not None:
            warning_dict["row"] = row
        self.warnings.append(warning_dict)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors and warnings."""
        return {
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }
    
    def clear(self) -> None:
        """Clear all errors and warnings."""
        self.errors.clear()
        self.warnings.clear()
