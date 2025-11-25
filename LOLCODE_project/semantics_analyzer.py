'''
CMSC 124: LOLCODE Semantics Evaluator
Handles all semantic execution: operations, variables, control flow, I/O
'''

# semantics evaluator for LOLCODE
from typecaster import TypeCaster

class SemanticsEvaluator:
    def __init__(self, symbol_table, emit_function=None):
        self.symbol_table = symbol_table
        self.output_buffer = []
        self.emit_function = emit_function  # For GUI output
        self.functions = {}  # Function storage
    
    # evaluate arithmetic operations
    def evaluate_arithmetic(self, operation, operand1, operand2):
        # convert operands to numeric values using TypeCaster
        val1 = TypeCaster.implicit_cast_to_numeric(operand1)
        val2 = TypeCaster.implicit_cast_to_numeric(operand2)
        
        # NOOB propagation: if any operand is NOOB or cannot be converted, return NOOB
        if val1 is None or val2 is None:
            return 'NOOB'

        # Check for division by zero - return NOOB instead of error
        if operation in ['QUOSHUNT OF', 'MOD OF'] and val2 == 0:
            return 'NOOB'

        # perform the operation
        try:
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
                return 'NOOB'  # Unknown operation
            
            return result
        except Exception:
            # Any runtime error during operation returns NOOB
            return 'NOOB'

    # evaluate boolean operations
    def evaluate_boolean(self, operation, operand1, operand2):
        # Check for NOOB operands - propagate NOOB
        if operand1 == 'NOOB' or operand2 == 'NOOB':
            return 'NOOB'
        
        # evaluate boolean operations using TypeCaster
        try:
            val1 = TypeCaster.implicit_cast_to_troof(operand1)
            val2 = TypeCaster.implicit_cast_to_troof(operand2)
        except Exception:
            return 'NOOB'  # Propagate NOOB on conversion error
        
        try:
            if operation == 'BOTH OF':  # AND
                result = val1 and val2
            elif operation == 'EITHER OF':  # OR
                result = val1 or val2
            elif operation == 'WON OF':  # XOR
                result = val1 ^ val2  # Use XOR operator instead of !=
            else:
                return 'NOOB'  # Unknown operation
            
            return 'WIN' if result else 'FAIL'
        except Exception:
            return 'NOOB'
    
    # evaluate comparison operations
    def evaluate_comparison(self, operation, operand1, operand2):
        # get types for error reporting
        type1 = self._get_operand_type(operand1)
        type2 = self._get_operand_type(operand2)
        
        # evaluate comparison operations using TypeCaster
        val1 = TypeCaster.implicit_cast_to_numeric(operand1)
        val2 = TypeCaster.implicit_cast_to_numeric(operand2)
        
        if val1 is None or val2 is None:
            # handle NOOB comparisons specially
            if type1 == "NOOB" or type2 == "NOOB":
                # NOOB can only be compared for equality
                if operation == 'BOTH SAEM':
                    result = (type1 == "NOOB" and type2 == "NOOB")
                elif operation == 'DIFFRINT':
                    result = not (type1 == "NOOB" and type2 == "NOOB")
                else:
                    return 'NOOB'  # Relational comparison with NOOB returns NOOB
            else:
                # try string comparison for non-NOOB values
                val1 = str(operand1)
                val2 = str(operand2)
                
                if operation == 'BOTH SAEM':
                    result = val1 == val2
                elif operation == 'DIFFRINT':
                    result = val1 != val2
                else:
                    return 'NOOB'  # Unknown operation
        else:
            # numeric comparison
            if operation == 'BOTH SAEM':
                result = val1 == val2
            elif operation == 'DIFFRINT':
                result = val1 != val2
            else:
                return 'NOOB'  # Unknown operation
        
        return 'WIN' if result else 'FAIL'
    
    def evaluate_relational_comparison(self, comparison_op, value, minmax_op, operand1, operand2):
        """
        Evaluate relational comparisons using BIGGR OF and SMALLR OF.
        
        LOLCODE relational comparison patterns:
        - x >= y: BOTH SAEM x AN BIGGR OF x AN y
        - x < y:  DIFFRINT x AN BIGGR OF x AN y
        - x <= y: BOTH SAEM x AN SMALLR OF x AN y
        - x > y:  DIFFRINT x AN SMALLR OF x AN y
        
        Args:
            comparison_op: 'BOTH SAEM' or 'DIFFRINT'
            value: The value to compare (x in the patterns above)
            minmax_op: 'BIGGR OF' or 'SMALLR OF'
            operand1: First operand of the min/max operation
            operand2: Second operand of the min/max operation
        
        Returns:
            'WIN' or 'FAIL'
        """
        # Get types for error reporting
        type_val = self._get_operand_type(value)
        type1 = self._get_operand_type(operand1)
        type2 = self._get_operand_type(operand2)
        
        # Convert to numeric values using TypeCaster
        val = TypeCaster.implicit_cast_to_numeric(value)
        val1 = TypeCaster.implicit_cast_to_numeric(operand1)
        val2 = TypeCaster.implicit_cast_to_numeric(operand2)
        
        # NOOB propagation: if any operand cannot be converted, return NOOB
        if val is None or val1 is None or val2 is None:
            return 'NOOB'
        
        try:
            # Evaluate the min/max operation
            if minmax_op == 'BIGGR OF':
                minmax_result = max(val1, val2)
            elif minmax_op == 'SMALLR OF':
                minmax_result = min(val1, val2)
            else:
                return 'NOOB'  # Unknown operation
            
            # Compare value with min/max result
            if comparison_op == 'BOTH SAEM':
                # BOTH SAEM x AN BIGGR OF x AN y => x >= y (x equals max of x and y)
                # BOTH SAEM x AN SMALLR OF x AN y => x <= y (x equals min of x and y)
                result = val == minmax_result
            elif comparison_op == 'DIFFRINT':
                # DIFFRINT x AN BIGGR OF x AN y => x < y (x differs from max of x and y)
                # DIFFRINT x AN SMALLR OF x AN y => x > y (x differs from min of x and y)
                result = val != minmax_result
            else:
                return 'NOOB'  # Unknown operation
            
            return 'WIN' if result else 'FAIL'
        except Exception:
            return 'NOOB'
    
    # evaluate unary NOT operation
    def evaluate_unary_not(self, operand):
        # evaluate NOT operation using TypeCaster
        val = TypeCaster.implicit_cast_to_troof(operand)
        return 'FAIL' if val else 'WIN'
    
    # evaluate IT variable for conditional logic
    def evaluate_it_condition(self):
        # evaluate IT variable for conditional logic
        if "IT" not in self.symbol_table:
            # if IT doesn't exist, default to False
            return False
        
        # get IT value
        it_value = self.symbol_table["IT"].get("value", "NOOB")
        return TypeCaster.implicit_cast_to_troof(it_value)
    
    #  evaluate string concatenation
    def evaluate_concatenation(self, operands):
        # Validate operands count
        self.validate_concatenation_operands(operands)
        
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
        """
        Wrapper for TypeCaster.implicit_cast_to_numeric for backward compatibility.
        Use TypeCaster directly for new code.
        """
        return TypeCaster.implicit_cast_to_numeric(value)
    
    def _get_operand_type(self, value):
        """
        Get the LOLCODE type of an operand for error reporting.
        Uses TypeCaster for consistent type inference.
        """
        # check if it's a variable reference
        if isinstance(value, str) and value in self.symbol_table:
            return self.symbol_table[value].get('type', 'YARN')
        
        # Use TypeCaster for type inference
        return TypeCaster.infer_type(value)
    
    def _to_bool(self, value):
        """
        Wrapper for TypeCaster.implicit_cast_to_troof for backward compatibility.
        Use TypeCaster directly for new code.
        """
        return TypeCaster.implicit_cast_to_troof(value)
    
    # handle VISIBLE statement
    def get_output(self):
        return ''.join(self.output_buffer)
    
    # append to output buffer
    def clear_output(self):
        self.output_buffer = []

    # store input value
    def store_input(self, variable_name, value):
        # Use semantic validation
        self.check_variable_declared(variable_name)
        
        # clean and process the input value
        processed_value = self._process_input_value(value)
        
        # update existing variable - always store as YARN per LOLCODE spec
        self.symbol_table[variable_name]['value'] = processed_value
        self.symbol_table[variable_name]['type'] = 'YARN'

    def _process_input_value(self, value):
        # process and clean input value
        if value is None or value == "":
            return "NOOB"
        
        # Convert to string and strip whitespace
        str_value = str(value).strip()
        
        # Handle empty string as NOOB
        if not str_value:
            return "NOOB"
            
        return str_value


    
    # ==================== VARIABLE MANAGEMENT ====================
    
    def declare_variable(self, variable_name, initial_value=None, initial_type=None):
        # declare a variable in the symbol table
        # Use semantic validation
        self.check_variable_not_redeclared(variable_name)
        
        if initial_value is not None: # if initial value is not None
            self.symbol_table[variable_name] = { # store in symbol table
                "value": initial_value,
                "type": initial_type if initial_type else self._infer_type(initial_value)
            }
        else:
            self.symbol_table[variable_name] = {"value": "NOOB", "type": "NOOB"}
    
    def assign_variable(self, variable_name, value, value_type=None):
        # assign a value to an existing variable
        # Use semantic validation
        self.check_variable_declared(variable_name)
        
        self.symbol_table[variable_name] = {
            "value": value,
            "type": value_type if value_type else self._infer_type(value)
        }
    
    def get_variable(self, variable_name):
        # get variable value from symbol table
        # Use semantic validation
        self.check_variable_declared(variable_name)
        return self.symbol_table[variable_name]["value"]
    
    def infer_type(self, value):
        """
        Public method to infer LOLCODE type from Python value.
        Uses TypeCaster for consistent type inference.
        """
        return TypeCaster.infer_type(value)
    
    def _infer_type(self, value):
        """Private wrapper for backward compatibility"""
        return self.infer_type(value)
    
    # ==================== OUTPUT EXECUTION ====================
    
    def execute_output(self, output_parts):
        # execute visible statement - output to console
        output_strings = []
        for part in output_parts:
            output_strings.append(str(part))
        
        final_output = " ".join(output_strings) # concatenate output strings
        
        # emit to GUI if available
        if self.emit_function:
            self.emit_function(final_output + "\n")
        
        # store in IT
        self.symbol_table["IT"] = {"value": final_output, "type": "YARN"}
        
        return final_output
    
    # ==================== CONDITIONAL EXECUTION ====================
    
    def should_execute_branch(self, branch_type, condition_value=None):
        # determine if a conditional branch should execute
        if branch_type == 'YA RLY':
            # execute if IT is WIN
            return self.evaluate_it_condition()
        elif branch_type == 'MEBBE':
            # execute if condition evaluates to WIN
            return self._to_bool(condition_value)
        elif branch_type == 'NO WAI':
            # execute as else (caller determines)
            return True
        return False
    
    # ==================== LOOP EXECUTION ====================
    
    def evaluate_loop_condition(self, loop_type, condition_value):
        # evaluate loop condition
        condition_bool = self._to_bool(condition_value)
        
        # evaluate loop type
        if loop_type == 'TIL':
            # continue until condition is true
            return not condition_bool
        elif loop_type == 'WILE':
            # continue while condition is true
            return condition_bool
        return False
    
    def increment_variable(self, variable_name):
        # increment a variable (UPPIN)
        # Use semantic validation
        self.validate_loop_variable(variable_name)
        
        current_value = self.symbol_table[variable_name]["value"]
        try: # try to increment
            new_value = int(current_value) + 1 
            self.symbol_table[variable_name]["value"] = new_value
            self.symbol_table[variable_name]["type"] = "NUMBR"
        except (ValueError, TypeError):
            raise ValueError(f"Cannot increment non-numeric variable '{variable_name}'")
    
    def decrement_variable(self, variable_name):
        # decrement a variable (NERFIN)
        # Use semantic validation
        self.validate_loop_variable(variable_name)
        
        current_value = self.symbol_table[variable_name]["value"]
        try:
            new_value = int(current_value) - 1
            self.symbol_table[variable_name]["value"] = new_value
            self.symbol_table[variable_name]["type"] = "NUMBR"
        except (ValueError, TypeError):
            raise ValueError(f"Cannot decrement non-numeric variable '{variable_name}'")
    
    # ==================== SWITCH-CASE EXECUTION ====================
    
    def match_case(self, switch_value, case_value): # check if switch value matches case value
        return str(switch_value) == str(case_value)
    
    # ==================== FUNCTION EXECUTION ====================
    
    def define_function(self, function_name, parameters, body_start_line):
        # define a function
        if function_name in self.functions:
            raise ValueError(f"Function '{function_name}' already defined")
        
        # Validate parameters for duplicates
        self._validate_function_parameters(parameters)
        
        # store function info
        self.functions[function_name] = {
            "name": function_name,
            "parameters": parameters,
            "body_start": body_start_line
        }
    
    def _validate_function_parameters(self, parameters):
        """
        Validate function parameters for duplicates.
        Raises ValueError if duplicate parameter names found.
        """
        seen = set()
        for param in parameters:
            if param in seen:
                raise ValueError(f"Duplicate parameter name '{param}' in function definition")
            seen.add(param)
    
    def prepare_function_call(self, function_name, arguments):
        # prepare for function call by binding arguments to parameters
        if function_name not in self.functions:
            raise ValueError(f"Function '{function_name}' not defined") 
        
        function_info = self.functions[function_name] # get function info
        parameters = function_info["parameters"] # get parameters
        
        # Use semantic validation
        self.validate_function_arguments(function_name, len(parameters), len(arguments))
        
        # Save previous values of parameters for scope management
        saved_values = {}
        for param in parameters:
            if param in self.symbol_table:
                saved_values[param] = self.symbol_table[param].copy()
        
        # bind arguments to parameters in symbol table
        for param, arg in zip(parameters, arguments):
            self.symbol_table[param] = {
                "value": arg,
                "type": self._infer_type(arg)
            }
        
        # Store saved values in function_info for restoration after call
        function_info["_saved_scope"] = saved_values
        
        return function_info
    
    def return_value(self, value):
        # handle function return value (FOUND YR)
        self.symbol_table["IT"] = {
            "value": value,
            "type": self._infer_type(value)
        }
    
    def return_void(self):
        # handle void return (GTFO in function)
        self.symbol_table["IT"] = {"value": "NOOB", "type": "NOOB"}
    
    def execute_function(self, function_name, arguments, parse_callback):
        """
        Execute a function with given arguments.
        This method handles all semantic aspects of function execution:
        - Validates function exists
        - Validates argument count
        - Binds arguments to parameters
        - Manages function scope
        - Executes function body via callback
        - Restores scope after execution
        
        Args:
            function_name: Name of the function to execute
            arguments: List of argument values
            parse_callback: Callback function to parse/execute the function body
                           Should accept (start_line, end_marker) and return when done
        
        Returns:
            The return value stored in IT after function execution
        """
        # Prepare function call (validates and binds parameters)
        func_info = self.prepare_function_call(function_name, arguments)
        
        # Execute the function body using the provided callback
        # The callback handles the parsing/execution of statements
        try:
            parse_callback(func_info['body_start'], 'IF U SAY SO')
        finally:
            # Always restore scope, even if execution fails
            self._restore_function_scope(func_info)
        
        # Return the result from IT
        return self.symbol_table.get('IT', {}).get('value', 'NOOB')
    
    def _restore_function_scope(self, func_info):
        """
        Restore the symbol table scope after function execution.
        Removes parameters and restores any previous values.
        """
        if '_saved_scope' in func_info:
            saved_scope = func_info['_saved_scope']
            parameters = func_info['parameters']
            
            for param in parameters:
                if param in saved_scope:
                    # Restore previous value
                    self.symbol_table[param] = saved_scope[param]
                elif param in self.symbol_table:
                    # Remove parameter if it didn't exist before
                    del self.symbol_table[param]
            
            # Clean up
            del func_info['_saved_scope']
    
    # ==================== RESULT STORAGE ====================
    
    def store_result(self, value, value_type=None):
        # store result in IT variable (implicit variable for expression results)
        self.symbol_table["IT"] = {
            "value": value,
            "type": value_type if value_type else self._infer_type(value)
        }
    
    def update_variable_type(self, variable_name, new_type):
        # update the type of an existing variable (for typecasting)
        if variable_name not in self.symbol_table: 
            raise ValueError(f"Variable '{variable_name}' not declared") # raise error if variable is not declared
        
        self.symbol_table[variable_name]["type"] = new_type # update the type of the variable
    
    # ==================== EXPRESSION EVALUATION ====================
    
    def evaluate_expression(self, expression):
        # if it's already a literal value, return it
        if expression is None:
            return None
        
        # handle dict-based expression trees from parser
        if isinstance(expression, dict):
            expr_type = expression.get('type')
            
            # evaluate literal expressions
            if expr_type == 'literal':
                return expression.get('value')
            
            # evaluate variable expressions 
            elif expr_type == 'variable':
                var_name = expression.get('name')
                return self.get_variable(var_name)
            
            # evaluate operation expressions
            elif expr_type == 'operation':
                return self.evaluate_operation(expression)
            
            # evaluate concatenation operations
            elif expr_type == 'concatenation':
                operands = expression.get('operands', [])
                return self.evaluate_concatenation(operands)
            
            # evaluate typecast operations
            elif expr_type == 'typecast':
                return self.evaluate_typecast(expression)
        
        # if it's a plain value, return it
        return expression
    
    def evaluate_operation(self, operation_expr):
        # evaluate operation expression
        operation = operation_expr.get('operation')
        operands = operation_expr.get('operands', [])
        
        # Evaluate operands first
        evaluated_operands = []
        for operand in operands:
            evaluated_operands.append(self.evaluate_expression(operand))
        
        # Route to appropriate handler based on operation type
        if operation == 'NOT':
            return self.evaluate_unary_not(evaluated_operands[0])
        
        # evaluate binary operations
        elif operation in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            return self.evaluate_arithmetic(operation, evaluated_operands[0], evaluated_operands[1])
        
        # evaluate boolean operations
        elif operation in ['BOTH OF', 'EITHER OF', 'WON OF']:
            return self.evaluate_boolean(operation, evaluated_operands[0], evaluated_operands[1])
        
        # evaluate comparison operations
        elif operation in ['BOTH SAEM', 'DIFFRINT']:
            return self.evaluate_comparison(operation, evaluated_operands[0], evaluated_operands[1])
        
        # evaluate infinite arity operations
        elif operation in ['ALL OF', 'ANY OF']:
            return self.evaluate_infinite_arity(operation, evaluated_operands)
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def evaluate_infinite_arity(self, operation, operands): 
        # evaluate infinite arity operations (ALL OF, ANY OF)
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
            result = 'FAIL' # default to FAIL
        
        return result
    
    def evaluate_typecast(self, typecast_expr):
        value = self.evaluate_expression(typecast_expr.get('value')) # get value from expression
        target_type = typecast_expr.get('target_type') # get target type
         
        # return typecasted value
        return self.typecast_value(value, target_type) 
    
    # MAEK ... A ...
    def typecast_value(self, value, target_type):
        """
        Convert value to target type using TypeCaster for consistency.
        Used for MAEK operations.
        """
        try:
            return TypeCaster.explicit_cast(value, target_type)
        except ValueError as e:
            # If explicit cast fails, return NOOB
            raise ValueError(f"Cannot cast '{value}' to {target_type}: {str(e)}")
        except Exception:
            return 'NOOB' 
    
    def typecast_variable(self, variable_name, target_type):
        # IS NOW A
        if variable_name not in self.symbol_table: # if variable is not declared
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        current_value = self.symbol_table[variable_name]['value']
        new_value = self.typecast_value(current_value, target_type)
        
        self.symbol_table[variable_name]['value'] = new_value
        self.symbol_table[variable_name]['type'] = target_type
    
    # ==================== SEMANTIC VALIDATION METHODS ====================
    
    def check_variable_declared(self, variable_name):
        """
        Check if a variable is declared in the symbol table.
        Raises ValueError if not declared.
        """
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' used before declaration")
        return True
    
    def check_variable_not_redeclared(self, variable_name):
        """
        Check if a variable is NOT already declared (for new declarations).
        Raises ValueError if already declared.
        """
        if variable_name in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' is already declared")
        return True
    
    def validate_numeric_operand(self, value, operation_name, operand_position=""):
        """
        Validate that an operand can be converted to a numeric value.
        Raises ValueError with descriptive message if invalid.
        """
        operand_type = self._get_operand_type(value)
        
        if operand_type == "NOOB":
            raise ValueError(f"Cannot perform {operation_name} with NOOB value{' (' + operand_position + ')' if operand_position else ''}")
        
        numeric_val = self._to_numeric(value)
        if numeric_val is None:
            raise ValueError(f"Cannot convert {operand_type} value '{value}' to number for {operation_name}")
        
        return numeric_val
    
    def validate_division_by_zero(self, divisor, operation_name):
        """
        Check for division by zero.
        Raises ValueError if divisor is zero.
        """
        if divisor == 0:
            raise ValueError(f"Division by zero in {operation_name} operation")
        return True
    
    def validate_concatenation_operands(self, operands):
        """
        Validate SMOOSH operation has at least 2 operands.
        Raises ValueError if insufficient operands.
        """
        if not operands:
            raise ValueError("SMOOSH requires at least 2 operands, got 0")
        elif len(operands) == 1:
            raise ValueError(f"SMOOSH requires at least 2 operands, got 1")
        return True
    
    def validate_loop_variable(self, variable_name):
        """
        Validate that a loop variable exists and can be incremented/decremented.
        Raises ValueError if invalid.
        """
        if variable_name not in self.symbol_table:
            raise ValueError(f"Loop variable '{variable_name}' not declared")
        
        current_value = self.symbol_table[variable_name].get('value')
        try:
            int(current_value)
        except (ValueError, TypeError):
            raise ValueError(f"Loop variable '{variable_name}' must be numeric, got {self._get_operand_type(current_value)}")
        
        return True
    
    def validate_switch_cases(self, case_values):
        """
        Check for duplicate case values in switch statement.
        Raises ValueError if duplicates found.
        """
        seen = set()
        for case_value in case_values:
            if case_value in seen:
                raise ValueError(f"Duplicate case value '{case_value}' in switch statement")
            seen.add(case_value)
        return True
    
    def validate_function_arguments(self, function_name, expected_count, actual_count):
        """
        Validate that function call has correct number of arguments.
        Raises ValueError if mismatch.
        """
        if actual_count != expected_count:
            raise ValueError(f"Function '{function_name}' expects {expected_count} argument(s), got {actual_count}")
        return True
