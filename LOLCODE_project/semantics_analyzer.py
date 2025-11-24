'''
CMSC 124: LOLCODE Semantics Evaluator
Handles all semantic execution: operations, variables, control flow, I/O
'''

# semantics evaluator for LOLCODE
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
        # get types for error reporting
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
        # get types for error reporting
        type1 = self._get_operand_type(operand1)
        type2 = self._get_operand_type(operand2)
        
        # evaluate comparison operations
        val1 = self._to_numeric(operand1)
        val2 = self._to_numeric(operand2)
        
        if val1 is None or val2 is None:
            # handle NOOB comparisons specially
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
        # evaluate IT variable for conditional logic
        if "IT" not in self.symbol_table:
            # if IT doesn't exist, default to False
            return False
        
        # get IT value
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
                # first try integer conversion
                if '.' not in value:
                    return int(value)
                else:
                    # try float conversion
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
        # get the LOLCODE type of an operand for error reporting
        if isinstance(value, str):
            # check if it's a variable reference
            if value in self.symbol_table:
                return self.symbol_table[value].get('type', 'YARN')
            
            # check literal types
            if value.upper() in ['WIN', 'FAIL']:
                return 'TROOF'
            elif value == 'NOOB' or value == '':
                return 'NOOB'
            
            # try to determine if it's a number
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
        # validate variable exists
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        
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

    def _infer_input_type(self, value):
        # infer the LOLCODE type from input value
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
        # declare a variable in the symbol table
        if variable_name in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' already declared")
        
        if initial_value is not None: # if initial value is not None
            self.symbol_table[variable_name] = { # store in symbol table
                "value": initial_value,
                "type": initial_type if initial_type else self._infer_type(initial_value)
            }
        else:
            self.symbol_table[variable_name] = {"value": "NOOB", "type": "NOOB"}
    
    def assign_variable(self, variable_name, value, value_type=None):
        # assign a value to an existing variable
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        self.symbol_table[variable_name] = {
            "value": value,
            "type": value_type if value_type else self._infer_type(value)
        }
    
    def get_variable(self, variable_name):
        # get variable value from symbol table
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared")
        return self.symbol_table[variable_name]["value"]
    
    def _infer_type(self, value):
        # infer LOLCODE type from Python value
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
        if variable_name not in self.symbol_table:
            raise ValueError(f"Variable '{variable_name}' not declared") # check if variable is declared
        
        current_value = self.symbol_table[variable_name]["value"]
        try: # try to increment
            new_value = int(current_value) + 1 
            self.symbol_table[variable_name]["value"] = new_value
            self.symbol_table[variable_name]["type"] = "NUMBR"
        except (ValueError, TypeError):
            raise ValueError(f"Cannot increment non-numeric variable '{variable_name}'")
    
    def decrement_variable(self, variable_name):
        # decrement a variable (NERFIN)
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
    
    def match_case(self, switch_value, case_value): # check if switch value matches case value
        return str(switch_value) == str(case_value)
    
    # ==================== FUNCTION EXECUTION ====================
    
    def define_function(self, function_name, parameters, body_start_line):
        # define a function
        if function_name in self.functions:
            raise ValueError(f"Function '{function_name}' already defined")
        
        # store function info
        self.functions[function_name] = {
            "name": function_name,
            "parameters": parameters,
            "body_start": body_start_line
        }
    
    def prepare_function_call(self, function_name, arguments):
        # prepare for function call by binding arguments to parameters
        if function_name not in self.functions:
            raise ValueError(f"Function '{function_name}' not defined") 
        
        function_info = self.functions[function_name] # get function info
        parameters = function_info["parameters"] # get parameters
        
        if len(arguments) != len(parameters): # check if number of arguments matches
            raise ValueError(f"Function '{function_name}' expects {len(parameters)} arguments, got {len(arguments)}")
        
        # bind arguments to parameters in symbol table
        for param, arg in zip(parameters, arguments):
            self.symbol_table[param] = {
                "value": arg,
                "type": self._infer_type(arg)
            }
        
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
    def typecast_value(self, value, target_type): # convert value to target type
        try:
            if target_type == 'TROOF': # 
                # Convert to boolean
                if value == 'NOOB' or value == '' or value == 0 or value == 0.0:
                    return 'FAIL'
                else:
                    return 'WIN'
            
            # NUMBR
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
            
            # NUMBAR
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
            
            # YARN
            elif target_type == 'YARN':
                # Convert to string
                return str(value)
            
            else:
                return value
        
        # if conversion fails
        except (ValueError, TypeError):
            return 'NOOB' 
    
    def typecast_variable(self, variable_name, target_type):
        # IS NOW A
        if variable_name not in self.symbol_table: # if variable is not declared
            raise ValueError(f"Variable '{variable_name}' not declared")
        
        current_value = self.symbol_table[variable_name]['value']
        new_value = self.typecast_value(current_value, target_type)
        
        self.symbol_table[variable_name]['value'] = new_value
        self.symbol_table[variable_name]['type'] = target_type
