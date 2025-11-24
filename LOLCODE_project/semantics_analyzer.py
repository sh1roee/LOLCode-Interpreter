'''
CMSC 124: LOLCODE Semantics Evaluator (30% - Basic Operations)
Implements: arithmetic, concatenation, boolean, comparison, assignment, VISIBLE
'''

#  semantics evaluator for LOLCODE
class SemanticsEvaluator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.output_buffer = []
    
    # evaluate arithmetic operations
    def evaluate_arithmetic(self, operation, operand1, operand2):
        # Get the original types for better error messages
        type1 = self._get_operand_type(operand1)
        type2 = self._get_operand_type(operand2)
        
        # convert operands to numeric values
        val1 = self._to_numeric(operand1)
        val2 = self._to_numeric(operand2)
        
        # Check for invalid operands and provide specific error messages
        if val1 is None:
            if type1 == "NOOB":
                raise ValueError(f"Cannot perform {operation} with NOOB value (first operand)")
            else:
                raise ValueError(f"Cannot convert {type1} value '{operand1}' to number for {operation}")
        
        if val2 is None:
            if type2 == "NOOB":
                raise ValueError(f"Cannot perform {operation} with NOOB value (second operand)")
            else:
                raise ValueError(f"Cannot convert {type2} value '{operand2}' to number for {operation}")

        # Check for division by zero with specific messages
        if operation in ['QUOSHUNT OF', 'MOD OF'] and val2 == 0:
            raise ValueError(f"Division by zero in {operation} operation")

        # perform the operation
        if operation == 'SUM OF':
            result = val1 + val2
        elif operation == 'DIFF OF':
            result = val1 - val2
        elif operation == 'PRODUKT OF':
            result = val1 * val2
        elif operation == 'QUOSHUNT OF':
            result = val1 / val2
        elif operation == 'MOD OF':
            result = val1 % val2
        elif operation == 'BIGGR OF':
            result = max(val1, val2)
        elif operation == 'SMALLR OF':
            result = min(val1, val2)
        else:
            raise ValueError(f"Unknown arithmetic operation: {operation}")
        
        return result

    # evaluate boolean operations
    def evaluate_boolean(self, operation, operand1, operand2):
        # Get types for error reporting
        type1 = self._get_operand_type(operand1)
        type2 = self._get_operand_type(operand2)
        
        # evaluate boolean operations
        try:
            val1 = self._to_bool(operand1)
            val2 = self._to_bool(operand2)
        except Exception:
            raise ValueError(f"Cannot perform boolean {operation} with types {type1} and {type2}")
        
        if operation == 'BOTH OF':  # AND
            result = val1 and val2
        elif operation == 'EITHER OF':  # OR
            result = val1 or val2
        elif operation == 'WON OF':  # XOR
            result = val1 != val2
        else:
            raise ValueError(f"Unknown boolean operation: {operation}")
        
        return 'WIN' if result else 'FAIL'
    
    # evaluate comparison operations
    def evaluate_comparison(self, operation, operand1, operand2):
        # Get types for error reporting
        type1 = self._get_operand_type(operand1)
        type2 = self._get_operand_type(operand2)
        
        val1 = self._to_numeric(operand1)
        val2 = self._to_numeric(operand2)
        
        if val1 is None or val2 is None:
            # Handle NOOB comparisons specially
            if type1 == "NOOB" or type2 == "NOOB":
                # NOOB can only be compared for equality
                if operation == 'BOTH SAEM':
                    result = (type1 == "NOOB" and type2 == "NOOB")
                elif operation == 'DIFFRINT':
                    result = not (type1 == "NOOB" and type2 == "NOOB")
                else:
                    raise ValueError(f"Cannot perform {operation} comparison with NOOB value")
            else:
                # try string comparison for non-NOOB values
                val1 = str(operand1)
                val2 = str(operand2)
                
                if operation == 'BOTH SAEM':
                    result = val1 == val2
                elif operation == 'DIFFRINT':
                    result = val1 != val2
                else:
                    raise ValueError(f"Unknown comparison operation: {operation}")
        else:
            # numeric comparison
            if operation == 'BOTH SAEM':
                result = val1 == val2
            elif operation == 'DIFFRINT':
                result = val1 != val2
            else:
                raise ValueError(f"Unknown comparison operation: {operation}")
        
        return 'WIN' if result else 'FAIL'
    
    # evaluate unary NOT operation
    def evaluate_unary_not(self, operand):
        # evaluate NOT operation
        val = self._to_bool(operand)
        return 'FAIL' if val else 'WIN'
    
    # evaluate IT variable for conditional logic
    def evaluate_it_condition(self):
        """
        Evaluate the IT variable as a boolean for conditional statements
        Returns True if IT evaluates to WIN, False otherwise
        """
        if "IT" not in self.symbol_table:
            # If IT doesn't exist, default to False
            return False
        
        it_value = self.symbol_table["IT"].get("value", "NOOB")
        return self._to_bool(it_value)
    
    #  evaluate string concatenation
    def evaluate_concatenation(self, operands):
        result = []
        for operand in operands:
            result.append(str(operand))
        return ''.join(result)
    
    def resolve_value(self, token_value, token_type):
        if token_type == 'Variable Identifier':
            if token_value in self.symbol_table:
                return self.symbol_table[token_value].get('value', 'NOOB')
            return 'NOOB'
        elif token_type in ['NUMBR Literal', 'NUMBAR Literal']:
            return token_value
        elif token_type == 'TROOF Literal':
            return token_value
        elif token_type == 'YARN Literal':
            return token_value
        else:
            return token_value
    
    def _to_numeric(self, value):
        if isinstance(value, (int, float)):
            return value
        
        # handle string inputs
        if isinstance(value, str):
            # handle NOOB
            if value == "NOOB":
                return None
                
            # handle TROOF values
            value_upper = value.upper()
            if value_upper == 'WIN':
                return 1
            elif value_upper == 'FAIL':
                return 0
            
            # try to parse as number (this handles YARN from GIMMEH)
            try:
                # First try integer conversion
                if '.' not in value:
                    return int(value)
                else:
                    # Try float conversion
                    return float(value)
            except (ValueError, AttributeError):
                # try to resolve as variable
                if value in self.symbol_table:
                    var_value = self.symbol_table[value].get('value')
                    if var_value != value:  # Avoid infinite recursion
                        return self._to_numeric(var_value)
                return None
        
        return None
    
    def _get_operand_type(self, value):
        """
        Get the LOLCODE type of an operand for error reporting
        """
        if isinstance(value, str):
            # Check if it's a variable reference
            if value in self.symbol_table:
                return self.symbol_table[value].get('type', 'YARN')
            
            # Check literal types
            if value.upper() in ['WIN', 'FAIL']:
                return 'TROOF'
            elif value == 'NOOB' or value == '':
                return 'NOOB'
            
            # Try to determine if it's a number
            try:
                if '.' in value:
                    float(value)
                    return 'NUMBAR'
                else:
                    int(value)
                    return 'NUMBR'
            except ValueError:
                return 'YARN'
        
        elif isinstance(value, int):
            return 'NUMBR'
        elif isinstance(value, float):
            return 'NUMBAR'
        elif isinstance(value, bool):
            return 'TROOF'
        else:
            return 'YARN'
    
    # convert to boolean
    def _to_bool(self, value):
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value_upper = value.upper()
            if value_upper == 'WIN':
                return True
            elif value_upper == 'FAIL':
                return False
            
            # check if variable
            if value in self.symbol_table:
                return self._to_bool(self.symbol_table[value].get('value'))
            
            # empty string is false
            return len(value) > 0
        
        if isinstance(value, (int, float)):
            return value != 0
        
        return False
    
    # handle VISIBLE statement
    def get_output(self):
        return ''.join(self.output_buffer)
    
    # append to output buffer
    def clear_output(self):
        self.output_buffer = []

    # store input value
    def store_input(self, variable_name, value):
        """
        Store user input in the specified variable as YARN per LOLCODE specification
        GIMMEH always stores input as YARN (string), type conversion happens during operations
        """
        # Clean and process the input value
        processed_value = self._process_input_value(value)
        
        if variable_name in self.symbol_table:
            # Update existing variable - always store as YARN per LOLCODE spec
            self.symbol_table[variable_name]['value'] = processed_value
            self.symbol_table[variable_name]['type'] = 'YARN'
        else:
            # Should have been declared, but if not, create it (loose semantics)
            self.symbol_table[variable_name] = {"value": processed_value, "type": "YARN"}

    def _process_input_value(self, value):
        """
        Process and clean input value
        """
        if value is None or value == "":
            return "NOOB"
        
        # Convert to string and strip whitespace
        str_value = str(value).strip()
        
        # Handle empty string as NOOB
        if not str_value:
            return "NOOB"
            
        return str_value

    def _infer_input_type(self, value):
        """
        Infer the LOLCODE type from input value
        """
        if value == "NOOB":
            return "NOOB"
        
        # Check for TROOF values
        value_upper = value.upper()
        if value_upper in ["WIN", "FAIL"]:
            return "TROOF"
        
        # Check for NUMBR (integer)
        try:
            int(value)
            return "NUMBR"
        except ValueError:
            pass
        
        # Check for NUMBAR (float)
        try:
            float(value)
            return "NUMBAR"
        except ValueError:
            pass
        
        # Default to YARN (string)
        return "YARN"
