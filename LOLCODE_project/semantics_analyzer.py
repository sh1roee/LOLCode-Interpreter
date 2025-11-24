'''
CMSC 124: LOLCODE Semantics Evaluator
Handles all semantic execution: operations, variables, control flow, I/O
'''

#  semantics evaluator for LOLCODE
class SemanticsEvaluator:
    def __init__(self, symbol_table, emit_function=None):
        self.symbol_table = symbol_table
        self.output_buffer = []
        self.emit_function = emit_function  # For GUI output
        self.functions = {}  # Function storage
    
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
        
        Raises:
            ValueError: If variable not declared
        """
        # Validate variable exists
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        # Clean and process the input value
        processed_value = self._process_input_value(value)
        
        # Update existing variable - always store as YARN per LOLCODE spec
        self.symbol_table[variable_name]['value'] = processed_value
        self.symbol_table[variable_name]['type'] = 'YARN'

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
    
    # ==================== VARIABLE MANAGEMENT ====================
    
    def declare_variable(self, variable_name, initial_value=None, initial_type=None):
        """
        Declare a variable in the symbol table
        """
        if variable_name in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' already declared")
        
        if initial_value is not None:
            self.symbol_table[variable_name] = {
                "value": initial_value,
                "type": initial_type if initial_type else self._infer_type(initial_value)
            }
        else:
            self.symbol_table[variable_name] = {"value": "NOOB", "type": "NOOB"}
    
    def assign_variable(self, variable_name, value, value_type=None):
        """
        Assign a value to an existing variable
        """
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        self.symbol_table[variable_name] = {
            "value": value,
            "type": value_type if value_type else self._infer_type(value)
        }
    
    def get_variable(self, variable_name):
        """
        Get variable value from symbol table
        """
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        return self.symbol_table[variable_name]["value"]
    
    def _infer_type(self, value):
        """
        Infer LOLCODE type from Python value
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
            return 'YARN'
        return 'NOOB'
    
    # ==================== OUTPUT EXECUTION ====================
    
    def execute_output(self, output_parts):
        """
        Execute VISIBLE statement - output to console
        Args:
            output_parts: List of values to output
        Returns:
            The concatenated output string
        """
        output_strings = []
        for part in output_parts:
            output_strings.append(str(part))
        
        final_output = " ".join(output_strings)
        
        # Emit to GUI if available
        if self.emit_function:
            self.emit_function(final_output + "\n")
        
        # Store in IT
        self.symbol_table["IT"] = {"value": final_output, "type": "YARN"}
        
        return final_output
    
    # ==================== CONDITIONAL EXECUTION ====================
    
    def should_execute_branch(self, branch_type, condition_value=None):
        """
        Determine if a conditional branch should execute
        Args:
            branch_type: 'YA RLY', 'MEBBE', or 'NO WAI'
            condition_value: For MEBBE, the condition to evaluate
        Returns:
            True if branch should execute, False otherwise
        """
        if branch_type == 'YA RLY':
            # Execute if IT is WIN
            return self.evaluate_it_condition()
        elif branch_type == 'MEBBE':
            # Execute if condition evaluates to WIN
            return self._to_bool(condition_value)
        elif branch_type == 'NO WAI':
            # Execute as else (caller determines)
            return True
        return False
    
    # ==================== LOOP EXECUTION ====================
    
    def evaluate_loop_condition(self, loop_type, condition_value):
        """
        Evaluate loop continuation condition
        Args:
            loop_type: 'TIL' or 'WILE'
            condition_value: The condition result
        Returns:
            True if loop should continue, False otherwise
        """
        condition_bool = self._to_bool(condition_value)
        
        if loop_type == 'TIL':
            # Continue until condition is true
            return not condition_bool
        elif loop_type == 'WILE':
            # Continue while condition is true
            return condition_bool
        return False
    
    def increment_variable(self, variable_name):
        """
        Increment a variable (UPPIN)
        """
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        current_value = self.symbol_table[variable_name]["value"]
        try:
            new_value = int(current_value) + 1
            self.symbol_table[variable_name]["value"] = new_value
            self.symbol_table[variable_name]["type"] = "NUMBR"
        except (ValueError, TypeError):
            raise ValueError(f"Cannot increment non-numeric variable '{variable_name}'")
    
    def decrement_variable(self, variable_name):
        """
        Decrement a variable (NERFIN)
        """
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        current_value = self.symbol_table[variable_name]["value"]
        try:
            new_value = int(current_value) - 1
            self.symbol_table[variable_name]["value"] = new_value
            self.symbol_table[variable_name]["type"] = "NUMBR"
        except (ValueError, TypeError):
            raise ValueError(f"Cannot decrement non-numeric variable '{variable_name}'")
    
    # ==================== SWITCH-CASE EXECUTION ====================
    
    def match_case(self, switch_value, case_value):
        """
        Check if switch value matches case value
        """
        return str(switch_value) == str(case_value)
    
    # ==================== FUNCTION EXECUTION ====================
    
    def define_function(self, function_name, parameters, body_start_line):
        """
        Store function definition
        Args:
            function_name: Name of the function
            parameters: List of parameter names
            body_start_line: Line number where function body starts
        """
        if function_name in self.functions:
            raise ValueError(f"Function '{function_name}' already defined")
        
        self.functions[function_name] = {
            "name": function_name,
            "parameters": parameters,
            "body_start": body_start_line
        }
    
    def prepare_function_call(self, function_name, arguments):
        """
        Prepare for function call by binding arguments to parameters
        Args:
            function_name: Name of function to call
            arguments: List of argument values
        Returns:
            Function info dict
        """
        if function_name not in self.functions:
            raise ValueError(f"Function '{function_name}' not defined")
        
        function_info = self.functions[function_name]
        parameters = function_info["parameters"]
        
        if len(arguments) != len(parameters):
            raise ValueError(f"Function '{function_name}' expects {len(parameters)} arguments, got {len(arguments)}")
        
        # Bind arguments to parameters in symbol table
        for param, arg in zip(parameters, arguments):
            self.symbol_table[param] = {
                "value": arg,
                "type": self._infer_type(arg)
            }
        
        return function_info
    
    def return_value(self, value):
        """
        Handle function return value (FOUND YR)
        """
        self.symbol_table["IT"] = {
            "value": value,
            "type": self._infer_type(value)
        }
    
    def return_void(self):
        """
        Handle void return (GTFO in function)
        """
        self.symbol_table["IT"] = {"value": "NOOB", "type": "NOOB"}
    
    # ==================== RESULT STORAGE ====================
    
    def store_result(self, value, value_type=None):
        """
        Store result in IT variable (implicit variable for expression results)
        """
        self.symbol_table["IT"] = {
            "value": value,
            "type": value_type if value_type else self._infer_type(value)
        }
    
    def update_variable_type(self, variable_name, new_type):
        """
        Update the type of an existing variable (for typecasting)
        """
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        self.symbol_table[variable_name]["type"] = new_type
    
    # ==================== EXPRESSION EVALUATION ====================
    
    def evaluate_expression(self, expression):
        """
        Evaluate any expression (literal, variable reference, or operation result)
        This is the main entry point for evaluating expressions from syntax analyzer
        
        Args:
            expression: Can be:
                - A literal value (int, float, str, bool)
                - A dict with 'type' and other fields describing an expression
                - An operation result
        
        Returns:
            The evaluated value
        """
        # If it's already a literal value, return it
        if expression is None:
            return None
        
        # Handle dict-based expression trees from parser
        if isinstance(expression, dict):
            expr_type = expression.get('type')
            
            if expr_type == 'literal':
                return expression.get('value')
            
            elif expr_type == 'variable':
                var_name = expression.get('name')
                return self.get_variable(var_name)
            
            elif expr_type == 'operation':
                return self.evaluate_operation(expression)
            
            elif expr_type == 'concatenation':
                operands = expression.get('operands', [])
                return self.evaluate_concatenation(operands)
            
            elif expr_type == 'typecast':
                return self.evaluate_typecast(expression)
        
        # If it's a plain value, return it
        return expression
    
    def evaluate_operation(self, operation_expr):
        """
        Evaluate an operation expression
        
        Args:
            operation_expr: Dict with 'operation' and 'operands' keys
        
        Returns:
            The result of the operation
        """
        operation = operation_expr.get('operation')
        operands = operation_expr.get('operands', [])
        
        # Evaluate operands first
        evaluated_operands = []
        for operand in operands:
            evaluated_operands.append(self.evaluate_expression(operand))
        
        # Route to appropriate handler based on operation type
        if operation == 'NOT':
            return self.evaluate_unary_not(evaluated_operands[0])
        
        elif operation in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            return self.evaluate_arithmetic(operation, evaluated_operands[0], evaluated_operands[1])
        
        elif operation in ['BOTH OF', 'EITHER OF', 'WON OF']:
            return self.evaluate_boolean(operation, evaluated_operands[0], evaluated_operands[1])
        
        elif operation in ['BOTH SAEM', 'DIFFRINT']:
            return self.evaluate_comparison(operation, evaluated_operands[0], evaluated_operands[1])
        
        elif operation in ['ALL OF', 'ANY OF']:
            return self.evaluate_infinite_arity(operation, evaluated_operands)
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def evaluate_infinite_arity(self, operation, operands):
        """
        Evaluate infinite arity operations (ALL OF, ANY OF)
        
        Args:
            operation: 'ALL OF' or 'ANY OF'
            operands: List of operand values
        
        Returns:
            'WIN' or 'FAIL'
        """
        if operation == 'ALL OF':
            # All operands must be truthy
            result = 'WIN'
            for op in operands:
                if not self._to_bool(op):
                    result = 'FAIL'
                    break
        elif operation == 'ANY OF':
            # At least one operand must be truthy
            result = 'FAIL'
            for op in operands:
                if self._to_bool(op):
                    result = 'WIN'
                    break
        else:
            result = 'FAIL'
        
        return result
    
    def evaluate_typecast(self, typecast_expr):
        """
        Perform explicit typecasting (MAEK ... A ...)
        
        Args:
            typecast_expr: Dict with 'value' and 'target_type' keys
        
        Returns:
            The typecasted value
        """
        value = self.evaluate_expression(typecast_expr.get('value'))
        target_type = typecast_expr.get('target_type')
        
        return self.typecast_value(value, target_type)
    
    def typecast_value(self, value, target_type):
        """
        Convert a value to the specified LOLCODE type
        
        Args:
            value: The value to convert
            target_type: LOLCODE type ('TROOF', 'NUMBR', 'NUMBAR', 'YARN')
        
        Returns:
            The converted value
        """
        try:
            if target_type == 'TROOF':
                # Convert to boolean
                if value == 'NOOB' or value == '' or value == 0 or value == 0.0:
                    return 'FAIL'
                else:
                    return 'WIN'
            
            elif target_type == 'NUMBR':
                # Convert to integer
                if isinstance(value, str):
                    if value == 'WIN':
                        return 1
                    elif value == 'FAIL':
                        return 0
                    elif value == 'NOOB':
                        return 0
                    else:
                        return int(float(value))
                return int(value)
            
            elif target_type == 'NUMBAR':
                # Convert to float
                if isinstance(value, str):
                    if value == 'WIN':
                        return 1.0
                    elif value == 'FAIL':
                        return 0.0
                    elif value == 'NOOB':
                        return 0.0
                    else:
                        return float(value)
                return float(value)
            
            elif target_type == 'YARN':
                # Convert to string
                return str(value)
            
            else:
                return value
        
        except (ValueError, TypeError):
            return 'NOOB'
    
    def typecast_variable(self, variable_name, target_type):
        """
        Perform in-place typecast of a variable (IS NOW A)
        
        Args:
            variable_name: Name of the variable to typecast
            target_type: Target LOLCODE type
        """
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        current_value = self.symbol_table[variable_name]['value']
        new_value = self.typecast_value(current_value, target_type)
        
        self.symbol_table[variable_name]['value'] = new_value
        self.symbol_table[variable_name]['type'] = target_type
