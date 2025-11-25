"""
TypeCaster Module for LOLCODE Interpreter
Handles all implicit and explicit type conversions/coercions
following LOLCODE specification for consistent type handling.
"""

class TypeCaster:
    """
    Centralized type casting.
    Provides consistent implicit and explicit type conversions.
    """
    
    @staticmethod
    def implicit_cast_to_numeric(value):
        """
        Implicitly cast a value to numeric (NUMBR or NUMBAR).
        
        LOLCODE type coercion rules for numeric:
        - NUMBR/NUMBAR: Return as-is
        - TROOF: WIN -> 1, FAIL -> 0
        - YARN: Parse string to number if possible
        - NOOB: Return None (cannot be converted)
        
        Args:
            value: Value to convert to numeric
            
        Returns:
            int or float if conversion successful, None otherwise
        """
        # Already numeric
        if isinstance(value, (int, float)):
            return value
        
        # Handle string values
        if isinstance(value, str):
            # NOOB cannot be converted to numeric
            if value == "NOOB":
                return None
            
            # TROOF to numeric: WIN=1, FAIL=0
            value_upper = value.upper()
            if value_upper == 'WIN':
                return 1
            elif value_upper == 'FAIL':
                return 0
            
            # Try to parse YARN as number
            try:
                # Integer if no decimal point
                if '.' not in value:
                    return int(value)
                else:
                    return float(value)
            except (ValueError, AttributeError):
                # Cannot convert this string to number
                return None
        
        # Boolean to numeric
        if isinstance(value, bool):
            return 1 if value else 0
        
        # Cannot convert
        return None
    
    @staticmethod
    def implicit_cast_to_troof(value):
        """
        Implicitly cast a value to TROOF (boolean).
        
        LOLCODE type coercion rules for TROOF:
        - TROOF: Return as-is
        - NUMBR/NUMBAR: 0 -> FAIL, non-zero -> WIN
        - YARN: Empty string -> FAIL, non-empty -> WIN
        - NOOB: -> FAIL
        
        Args:
            value: Value to convert to boolean
            
        Returns:
            bool (True for WIN, False for FAIL)
        """
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
            
            # Non-empty YARN is truthy
            return len(value) > 0
        
        # Numeric to boolean: 0 is falsy, non-zero is truthy
        if isinstance(value, (int, float)):
            return value != 0
        
        # Default: falsy
        return False
    
    @staticmethod
    def implicit_cast_to_yarn(value):
        """
        Implicitly cast a value to YARN (string).
        
        All types can be converted to YARN.
        
        Args:
            value: Value to convert to string
            
        Returns:
            str representation of the value
        """
        if isinstance(value, str):
            return value
        
        if isinstance(value, bool):
            return 'WIN' if value else 'FAIL'
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if value is None or value == 'NOOB':
            return 'NOOB'
        
        return str(value)
    
    @staticmethod
    def explicit_cast(value, target_type):
        """
        Explicitly cast a value to a target LOLCODE type.
        Used for IS NOW A and MAEK operations.
        
        Args:
            value: Value to cast
            target_type: Target LOLCODE type ('NUMBR', 'NUMBAR', 'YARN', 'TROOF')
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If conversion is not possible
        """
        if target_type == 'NUMBR':
            numeric_val = TypeCaster.implicit_cast_to_numeric(value)
            if numeric_val is None:
                raise ValueError(f"Cannot cast '{value}' to NUMBR")
            return int(numeric_val)
        
        elif target_type == 'NUMBAR':
            numeric_val = TypeCaster.implicit_cast_to_numeric(value)
            if numeric_val is None:
                raise ValueError(f"Cannot cast '{value}' to NUMBAR")
            return float(numeric_val)
        
        elif target_type == 'YARN':
            return TypeCaster.implicit_cast_to_yarn(value)
        
        elif target_type == 'TROOF':
            bool_val = TypeCaster.implicit_cast_to_troof(value)
            return 'WIN' if bool_val else 'FAIL'
        
        elif target_type == 'NOOB':
            return 'NOOB'
        
        else:
            raise ValueError(f"Unknown target type: {target_type}")
    
    @staticmethod
    def can_compare(value1, value2):
        """
        Check if two values can be compared.
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            bool: True if values can be compared
        """
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
        """
        Infer the LOLCODE type of a value.
        
        Args:
            value: Value to infer type for
            
        Returns:
            str: LOLCODE type name
        """
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
