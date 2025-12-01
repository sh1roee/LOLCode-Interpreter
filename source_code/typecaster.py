# this is the typecaster po
import re

class TypeCaster:
    # Centralized type casting.
    # Provides consistent implicit and explicit type conversions.
    
    @staticmethod
    def implicit_cast_to_numeric(value):
        # Implicitly cast a value to numeric (NUMBR or NUMBAR).
        # NOOBs cannot be implicitly typecast to numeric - results in error
        # Already numeric
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
        
        # Handle string values
        if isinstance(value, str):
            # NOOB cannot be implicitly converted to numeric - return None to signal error
            if value == "NOOB":
                return None
            
            # TROOF to numeric: WIN=1, FAIL=0
            value_upper = value.upper()
            if value_upper == 'WIN':
                return 1
            elif value_upper == 'FAIL':
                return 0
            
            # Try to parse YARN as number
            # YARN can only be cast if it contains only numerical, hyphen, period characters
            if TypeCaster._is_valid_numeric_yarn(value):
                try:
                    if '.' not in value:
                        return int(value)
                    else:
                        return float(value)
                except (ValueError, AttributeError):
                    return None
            else:
                return None
        
        # Boolean to numeric: WIN=1, FAIL=0
        if isinstance(value, bool):
            return 1 if value else 0
        
        # Cannot convert
        return None
    
    @staticmethod
    def _is_valid_numeric_yarn(value):
        """Check if YARN contains only numerical, hyphen, and period characters."""
        if not value:
            return False
        # Allow: digits, single hyphen at start (negative), single period (decimal)
        # Pattern: optional minus, digits, optional decimal with digits
        pattern = r'^-?[0-9]+(\.[0-9]+)?$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def implicit_cast_to_troof(value):
        # Implicitly cast a value to TROOF (boolean).
        # Already boolean
        if isinstance(value, bool):
            return value
        
        # Handle string values
        if isinstance(value, str):
            # TROOF literals
            value_upper = value.upper()
            if value_upper == 'WIN':
                return True
            elif value_upper == 'FAIL':
                return False
            
            # NOOB is falsy
            if value == 'NOOB' or value == '':
                return False
            
            # If YARN looks numeric, use numeric truthiness ("0" -> False)
            try:
                if '.' in value:
                    num = float(value)
                else:
                    num = int(value)
                return num != 0
            except ValueError:
                # Not numeric; fall back to non-empty string truthiness
                pass
            
            # Non-empty YARN is truthy
            return len(value) > 0
        
        # Numeric to boolean: 0 is falsy, non-zero is truthy
        if isinstance(value, (int, float)):
            return value != 0
        
        # Default: falsy
        return False
    
    @staticmethod
    def implicit_cast_to_yarn(value):
        # Implicitly cast a value to YARN (string).
        if isinstance(value, str):
            return value
        
        if isinstance(value, bool):
            return 'WIN' if value else 'FAIL'
        
        # NUMBAR to YARN: truncate to 2 decimal places
        if isinstance(value, float):
            # Format to 2 decimal places, but remove trailing zeros
            formatted = f"{value:.2f}"
            # Remove unnecessary trailing zeros after decimal
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
                # If we stripped everything after decimal, keep at least .0 for floats
                if '.' not in formatted and isinstance(value, float) and value != int(value):
                    formatted = f"{value:.1f}"
            return formatted
        
        # NUMBR to YARN: just convert to string
        if isinstance(value, int):
            return str(value)
        
        if value is None or value == 'NOOB':
            return 'NOOB'
        
        return str(value)
    
    @staticmethod
    def explicit_cast(value, target_type):
        # Explicitly cast a value to a target LOLCODE type.
        # NOOB explicit casting results in empty/zero values
        is_noob = (value == 'NOOB' or value is None)
        
        if target_type == 'NUMBR':
            # NOOB -> 0
            if is_noob:
                return 0
            numeric_val = TypeCaster.implicit_cast_to_numeric(value)
            if numeric_val is None:
                raise ValueError(f"Cannot cast '{value}' to NUMBR")
            # NUMBAR to NUMBR: truncate decimal portion
            return int(numeric_val)
        
        elif target_type == 'NUMBAR':
            # NOOB -> 0.0
            if is_noob:
                return 0.0
            numeric_val = TypeCaster.implicit_cast_to_numeric(value)
            if numeric_val is None:
                raise ValueError(f"Cannot cast '{value}' to NUMBAR")
            # NUMBR to NUMBAR: just convert to float, value retained
            return float(numeric_val)
        
        elif target_type == 'YARN':
            # NOOB -> "" (empty string)
            if is_noob:
                return ""
            # NUMBAR to YARN: truncate to 2 decimal places
            if isinstance(value, float):
                formatted = f"{value:.2f}"
                if '.' in formatted:
                    formatted = formatted.rstrip('0').rstrip('.')
                return formatted
            # NUMBR to YARN: just convert to string
            return TypeCaster.implicit_cast_to_yarn(value)
        
        elif target_type == 'TROOF':
            # NOOB -> FAIL
            if is_noob:
                return 'FAIL'
            bool_val = TypeCaster.implicit_cast_to_troof(value)
            return 'WIN' if bool_val else 'FAIL'
        
        elif target_type == 'NOOB':
            return 'NOOB'
        
        else:
            raise ValueError(f"Unknown target type: {target_type}")
    
    @staticmethod
    def can_compare(value1, value2):
        # Check if two values can be compared.
        # NOOB can only be compared with NOOB
        if value1 == 'NOOB' or value2 == 'NOOB':
            return value1 == 'NOOB' and value2 == 'NOOB'
        
        # Try numeric comparison
        num1 = TypeCaster.implicit_cast_to_numeric(value1)
        num2 = TypeCaster.implicit_cast_to_numeric(value2)
        
        if num1 is not None and num2 is not None:
            return True
        
        # Fall back to string comparison
        return True
    
    @staticmethod
    def infer_type(value):
        # Infer the LOLCODE type of a value.
        if isinstance(value, bool) or value in ['WIN', 'FAIL']:
            return 'TROOF'
        elif isinstance(value, int):
            return 'NUMBR'
        elif isinstance(value, float):
            return 'NUMBAR'
        elif isinstance(value, str):
            if value == 'NOOB':
                return 'NOOB'
            
            # Try to determine if it's a numeric string
            try:
                if '.' in value:
                    float(value)
                    return 'NUMBAR'
                else:
                    int(value)
                    return 'NUMBR'
            except ValueError:
                return 'YARN'
        
        return 'NOOB'
