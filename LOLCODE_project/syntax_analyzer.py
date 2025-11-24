'''
CMSC 124: LOLCODE Syntax Analyzer
- Sophia Ysabel Garcia
- James Andrei Tadeja
- Ron Russell Velasco
'''

from lexer_analyzer import tokenize, readFile
from semantics_analyzer import SemanticsEvaluator

class SyntaxAnalyzer:
    def __init__(self, tokens, log_function=None, input_function=None):
        # organize tokens by line number
        self.lines = self._organize_tokens_by_line(tokens)
        self.current_line_number = min(self.lines.keys()) if self.lines else None
        self.current_tokens = self.lines[self.current_line_number] if self.lines else []
        self.current_position = 0
        self.current_token = self.current_tokens[0] if self.current_tokens else None
        self.error_messages = []
        self.variables = {"IT": {"value": "NOOB", "type": "NOOB"}}
        self.in_wazzup_block = False
        self.inside_switch_block = False

        self.log_function = log_function
        self.input_function = input_function
        
        # semantics evaluator
        self.semantics = SemanticsEvaluator(self.variables)

    def emit(self, message):
        if message is None:
            return
        if not isinstance(message, str):
            message = str(message)
        if self.log_function:
            # send to GUI console
            self.log_function(message)
        else:
            print(message)


    def _organize_tokens_by_line(self, tokens):
        # group all tokens by their line numbers so we can process line by line
        lines = {}
        for token in tokens:
            # skip comment tokens since we dont need to parse them
            if token.type != "Comment Line":
                if token.line_number not in lines:
                    lines[token.line_number] = []
                lines[token.line_number].append(token)
        return lines

    def log_syntax_error(self, message, expected=None, found=None):
        # format error message depending on what info we have
        if expected and found:
            error_message = (
                f"Syntax Error: {message}. Expected '{expected}', but found '{found}' "
                f"(line {self.current_line_number})"
            )
        elif expected:
            error_message = (
                f"Syntax Error: {message}. Expected '{expected}' "
                f"(line {self.current_line_number})"
            )
        else:
            error_message = f"Syntax Error: {message} (line {self.current_line_number})"

        # save error and display it
        self.error_messages.append(error_message)
        self.emit(error_message + "\n")

    def print_variables(self):
        print("\nVariables:")
        for identifier, identifier_info in self.variables.items():
            value = identifier_info.get("value", "undefined")
            var_type = identifier_info.get("type", "unknown")
            print(f"  {identifier}: value={value}, type={var_type}")

    def _get_input(self, prompt):
        """
        Get input from user - handles both GUI and command line contexts
        """
        if self.input_function:
            # GUI context - use GUI's input method
            try:
                return self.input_function(prompt)
            except Exception as e:
                self.emit(f"GUI input failed: {e}. Using default value.\n")
                return "NOOB"
        else:
            # Command line context - use standard input
            try:
                return input(prompt)
            except (EOFError, KeyboardInterrupt):
                return "NOOB"  # Default value if input fails


    def advance_to_next_line(self):
        # move to the next line of code
        if self.current_line_number is None:
            self.current_tokens = []
            self.current_token = None
            return

        # get all line numbers in order
        line_numbers = sorted(self.lines.keys())
        current_index = line_numbers.index(self.current_line_number)
        next_line_index = current_index + 1
        
        # if theres a next line, move to it
        if next_line_index < len(line_numbers):
            self.current_line_number = line_numbers[next_line_index]
            self.current_tokens = self.lines[self.current_line_number]
            self.current_position = 0
            self.current_token = self.current_tokens[0] if self.current_tokens else None
        else:
            # no more lines, were done
            self.current_tokens = []
            self.current_token = None
            self.current_line_number = None

    def advance_to_next_token(self):
        # move to the next token on the current line
        if self.current_position < len(self.current_tokens) - 1:
            self.current_position += 1
            self.current_token = self.current_tokens[self.current_position]
        else:
            # no more tokens on this line
            self.current_token = None

    def parse_expression(self):
        # parse any kind of expression and return its string representation
        if not self.current_token:
            return None

        # handle literals (numbers, booleans)
        if self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal', 'TROOF Literal']:
            result = self.current_token.value
            self.advance_to_next_token()
            return result
        # handle strings
        elif self.current_token.type == 'YARN Literal':
            result = self.current_token.value
            self.advance_to_next_token()
            return result
        # handle variables
        elif self.current_token.type == 'Variable Identifier':
            var_name = self.current_token.value
            self.advance_to_next_token()
            return f"{var_name}"
        # handle operations (arithmetic, boolean, comparison)
        elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
            return self.parse_operation()
        # handle string concatenation
        elif self.current_token.type == 'String Concatenation':
            return self.parse_concatenation()
        else:
            return None
    
    def evaluate_expression(self):
        # evaluate an expression and return actual computed value
        if not self.current_token:
            return None

        # for number literals, just return the value
        if self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal']:
            result = self.current_token.value
            self.advance_to_next_token()
            return result
        # for boolean literals (WIN/FAIL)
        elif self.current_token.type == 'TROOF Literal':
            result = self.current_token.value
            self.advance_to_next_token()
            return result
        # for string literals
        elif self.current_token.type == 'YARN Literal':
            result = self.current_token.value
            self.advance_to_next_token()
            return result
        # for variables, look up their value in the symbol table
        elif self.current_token.type == 'Variable Identifier':
            var_name = self.current_token.value
            if var_name in self.variables:
                result = self.variables[var_name].get('value', 'NOOB')
            else:
                result = 'NOOB'
            self.advance_to_next_token()
            return result
        # for operations, evaluate them and return the result
        elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
            return self.evaluate_operation()
        # for string concatenation
        elif self.current_token.type == 'String Concatenation':
            return self.evaluate_concatenation()
        # for typecasting (MAEK A x TROOF)
        elif self.current_token.type == 'Typecasting Operation':
            return self.evaluate_typecasting()
        else:
            return None

    def parse_operation(self):
        # figure out what kind of operation this is and parse it accordingly
        operation = self.current_token.value
        self.advance_to_next_token()

        # unary operation (only takes one operand)
        if operation == 'NOT':
            return self.parse_unary_operation(operation)
        # arithmetic operations (take two operands)
        elif operation in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            return self.parse_binary_operation(operation)
        # infinite arity operations (can take multiple operands)
        elif operation in ['ALL OF', 'ANY OF']:
            return self.parse_infinite_arity_operation(operation)
        # boolean and comparison operations (take two operands)
        elif operation in ['BOTH OF', 'EITHER OF', 'WON OF', 'BOTH SAEM', 'DIFFRINT']:
            return self.parse_binary_operation(operation)
        # string concatenation
        elif operation == 'SMOOSH':
            return self.parse_concatenation()
        else:
            self.log_syntax_error("Unknown operation", found=operation)
            return f"Unknown operation '{operation}'"
    
    def evaluate_operation(self):
        # evaluate operation and return computed result
        operation = self.current_token.value
        self.advance_to_next_token()

        if operation == 'NOT':
            return self.evaluate_unary_operation(operation)
        elif operation in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            return self.evaluate_binary_operation(operation)
        elif operation in ['BOTH OF', 'EITHER OF', 'WON OF']:
            return self.evaluate_boolean_operation(operation)
        elif operation in ['BOTH SAEM', 'DIFFRINT']:
            return self.evaluate_comparison_operation(operation)
        elif operation in ['ALL OF', 'ANY OF']:
            return self.evaluate_infinite_arity_operation(operation)
        elif operation == 'SMOOSH':
            return self.evaluate_concatenation()
        else:
            return None

    def parse_unary_operation(self, operation):
        # parse operations that only take one operand (like NOT)
        if not self.current_token:
            self.log_syntax_error(f"Expected operand for '{operation}'")
            return f"{operation} Missing Operand"

        # check if its a simple value or variable
        if self.current_token.type in ['TROOF Literal', 'Variable Identifier']:
            operand = self.current_token.value
            self.advance_to_next_token()
            return f"{operation} {operand}"
        # or if its another operation (nested)
        elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
            operand = self.parse_operation()
            return f"{operation} {operand}"
        else:
            self.log_syntax_error(f"Expected TROOF, variable, or operation for '{operation}'")
            return f"{operation} Invalid Operand"

    def parse_binary_operation(self, operation):
        # parse operations that take two operands (like SUM OF x AN y)
        def parse_single_operand():
            # helper function to parse one operand
            if not self.current_token:
                return None

            # check if its a literal or variable
            if self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal', 'TROOF Literal', 'Variable Identifier', 'YARN Literal']:
                operand = self.current_token.value
                self.advance_to_next_token()
                return operand
            # or if its a nested operation
            elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
                return self.parse_operation()
            else:
                return None

        # get the first operand
        first_operand = parse_single_operand()
        if first_operand is None:
            self.log_syntax_error(f"Missing first operand for '{operation}'")
            return f"{operation} Missing First Operand"

        # expect AN keyword between operands
        if not self.current_token or self.current_token.value != 'AN':
            self.log_syntax_error(f"Missing 'AN' after first operand in '{operation}'")
            return f"{operation} {first_operand} Missing AN"

        self.advance_to_next_token()

        # get the second operand
        second_operand = parse_single_operand()
        if second_operand is None:
            self.log_syntax_error(f"Missing second operand for '{operation}'")
            return f"{operation} {first_operand} AN Missing Second Operand"

        return f"{operation} {first_operand} AN {second_operand}"

    def parse_infinite_arity_operation(self, operation):
        # parse operations that can take multiple operands (like ALL OF x AN y AN z MKAY)
        operands = []
        first_operand_parsed = False

        # keep going until we hit MKAY
        while self.current_token and self.current_token.value != 'MKAY':
            # handle AN separators between operands
            if self.current_token.value == 'AN':
                if not first_operand_parsed:
                    self.log_syntax_error(f"Unexpected 'AN' at the start of {operation}")
                    return f"{operation} Invalid Start with AN"
                self.advance_to_next_token()
                continue

            # parse literals and variables
            if self.current_token.type in ['TROOF Literal', 'NUMBR Literal', 'NUMBAR Literal', 'Variable Identifier', 'YARN Literal']:
                operands.append(self.current_token.value)
                first_operand_parsed = True
                self.advance_to_next_token()
            # parse nested operations
            elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
                operand = self.parse_operation()
                operands.append(operand)
                first_operand_parsed = True
            else:
                break

        # make sure we have MKAY at the end
        if not self.current_token or self.current_token.value != 'MKAY':
            self.log_syntax_error(f"Missing 'MKAY' at the end of {operation}")
            return f"{operation} {' AN '.join(operands)} Missing MKAY"

        self.advance_to_next_token()

        # make sure we got at least one operand
        if not operands:
            self.log_syntax_error(f"No operands provided for {operation}")
            return f"{operation} Missing Operands"

        return f"{operation} {' AN '.join(operands)} MKAY"

    def parse_concatenation(self):
        operands = []
        first_operand_parsed = False

        # consume the first SMOOSH token if present
        if self.current_token and \
        self.current_token.type == 'String Concatenation' and \
        self.current_token.value == 'SMOOSH':
            self.advance_to_next_token()

        while self.current_token:

            # AN separator
            if self.current_token.value == 'AN':
                if not first_operand_parsed:
                    self.log_syntax_error("Unexpected 'AN' at the start of SMOOSH")
                    self.advance_to_next_token()
                    return "SMOOSH Invalid Start with AN"
                self.advance_to_next_token()
                continue

            # Literals + variables
            if self.current_token.type in [
                'NUMBR Literal', 'NUMBAR Literal',
                'TROOF Literal', 'Variable Identifier',
                'YARN Literal'
            ]:
                val = self.current_token.value
                # For variables, resolve their value
                if self.current_token.type == 'Variable Identifier' and val in self.variables:
                    val = self.variables[val].get('value', 'NOOB')
                operands.append(str(val))
                first_operand_parsed = True
                self.advance_to_next_token()
                continue

            # Arithmetic / Boolean / Comparison expressions
            if self.current_token.type in [
                'Arithmetic Operation', 'Boolean Operation', 'Comparison Operation'
            ]:
                operation_output = self.parse_operation()
                operands.append(operation_output)
                first_operand_parsed = True
                continue

            # nested SMOOSH not allowed
            if self.current_token.type == 'String Concatenation':
                self.log_syntax_error("Nested SMOOSH not allowed")
                self.advance_to_next_token()
                return "SMOOSH Nested Error"

            # End of SMOOSH expression
            break

        # Validation
        if not operands:
            self.log_syntax_error("No operands specified after SMOOSH")
            return "SMOOSH Missing Operands"

        if len(operands) == 1:
            self.log_syntax_error("Only one operand specified after SMOOSH, requires at least two")
            return f"SMOOSH {' + '.join(operands)} Missing AN"

        return f"{' + '.join(operands)}"

    def evaluate_unary_operation(self, operation):
        # evaluate NOT operation with actual values
        if not self.current_token:
            return None
        
        # get the operand value
        operand_value = self.evaluate_expression()
        
        if operand_value is None:
            return None
        
        # do the NOT operation using semantics
        result = self.semantics.evaluate_unary_not(operand_value)
        
        # store result in IT variable
        self.variables['IT'] = {"value": result, "type": "TROOF"}
        
        return result
    
    def evaluate_binary_operation(self, operation):
        # evaluate arithmetic binary operations with actual values
        # get first operand
        first_operand = self.evaluate_expression()
        
        # expect AN keyword between operands
        if not self.current_token or self.current_token.value != 'AN':
            return None
        self.advance_to_next_token()
        
        # get second operand
        second_operand = self.evaluate_expression()
        
        # do the actual arithmetic using semantics
        try:
            result = self.semantics.evaluate_arithmetic(operation, first_operand, second_operand)
            
            # figure out if result is float or int
            result_type = 'NUMBAR' if isinstance(result, float) else 'NUMBR'
            
            # store result in IT variable
            self.variables['IT'] = {"value": result, "type": result_type}
            
            return result
        except ValueError as e:
            # Handle semantic errors
            self.log_syntax_error(f"Runtime Error: {str(e)}")
            return "NOOB"
    
    def evaluate_boolean_operation(self, operation):
        # evaluate boolean operations with actual values
        # get first operand
        first_operand = self.evaluate_expression()
        
        # expect AN keyword
        if not self.current_token or self.current_token.value != 'AN':
            return None
        self.advance_to_next_token()
        
        # get second operand
        second_operand = self.evaluate_expression()
        
        # do the boolean operation using semantics
        try:
            result = self.semantics.evaluate_boolean(operation, first_operand, second_operand)
            
            # store result in IT variable
            self.variables['IT'] = {"value": result, "type": "TROOF"}
            
            return result
        except ValueError as e:
            # Handle semantic errors
            self.log_syntax_error(f"Runtime Error: {str(e)}")
            return "NOOB"
    
    def evaluate_comparison_operation(self, operation):
        # evaluate comparison operations with actual values
        # get first operand
        first_operand = self.evaluate_expression()
        
        # expect AN keyword
        if not self.current_token or self.current_token.value != 'AN':
            return None
        self.advance_to_next_token()
        
        # get second operand
        second_operand = self.evaluate_expression()
        
        # do the comparison using semantics
        try:
            result = self.semantics.evaluate_comparison(operation, first_operand, second_operand)
            
            # store result in IT variable
            self.variables['IT'] = {"value": result, "type": "TROOF"}
            
            return result
        except ValueError as e:
            # Handle semantic errors
            self.log_syntax_error(f"Runtime Error: {str(e)}")
            return "NOOB"
    
    def evaluate_infinite_arity_operation(self, operation):
        # evaluate ALL OF or ANY OF operations with actual values
        operands = []
        
        while self.current_token and self.current_token.value != 'MKAY':
            # Skip AN delimiter
            if self.current_token.value == 'AN':
                self.advance_to_next_token()
                continue
            
            # Evaluate operand
            operand = self.evaluate_expression()
            if operand is not None:
                operands.append(operand)
            else:
                break
        
        # Consume MKAY
        if self.current_token and self.current_token.value == 'MKAY':
            self.advance_to_next_token()
        
        # Perform the operation
        if operation == 'ALL OF':
            # All operands must be truthy (WIN or non-zero/non-empty)
            result = 'WIN'
            for op in operands:
                if op == 'FAIL' or op == 0 or op == 0.0 or op == '' or op == 'NOOB':
                    result = 'FAIL'
                    break
        elif operation == 'ANY OF':
            # At least one operand must be truthy
            result = 'FAIL'
            for op in operands:
                if op != 'FAIL' and op != 0 and op != 0.0 and op != '' and op != 'NOOB':
                    result = 'WIN'
                    break
        else:
            result = 'FAIL'
        
        # Store in IT
        self.variables['IT'] = {"value": result, "type": "TROOF"}
        
        return result
    
    def evaluate_concatenation(self):
        # evaluate SMOOSH with actual values
        operands = []
        
        # Consume SMOOSH if present
        if self.current_token and self.current_token.type == 'String Concatenation':
            self.advance_to_next_token()
        
        while self.current_token:
            # AN separator
            if self.current_token.value == 'AN':
                self.advance_to_next_token()
                continue
            
            # Get operand value
            if self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal', 'TROOF Literal', 'YARN Literal']:
                operands.append(self.current_token.value)
                self.advance_to_next_token()
            elif self.current_token.type == 'Variable Identifier':
                var_name = self.current_token.value
                if var_name in self.variables:
                    operands.append(self.variables[var_name].get('value', 'NOOB'))
                else:
                    operands.append(var_name)
                self.advance_to_next_token()
            elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
                result = self.evaluate_operation()
                operands.append(result)
            elif self.current_token.type == 'String Concatenation':
                break
            else:
                break
        
        # Concatenate
        result = self.semantics.evaluate_concatenation(operands)
        
        # Store in IT
        self.variables['IT'] = {"value": result, "type": "YARN"}
        
        return result

    def parse_variable_declaration(self):
        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Variable name is missing or invalid after 'I HAS A'")
            return

        variable_name = self.current_token.value
        self.advance_to_next_token()

        if self.current_token and self.current_token.value == "ITZ":
            self.advance_to_next_token()

            if not self.current_token:
                self.log_syntax_error(f"Missing expression to initialize variable '{variable_name}' after 'ITZ'")
                return

            if self.current_token.type == 'YARN Literal':
                data_type = 'YARN'
            elif self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal', 'TROOF Literal']:
                data_type = self.current_token.type.split()[0]
            else:
                data_type = None

            # Evaluate expression to get actual value
            value = self.evaluate_expression()
            self.variables[variable_name] = {"value": value, "type": data_type}
        else:
            self.variables[variable_name] = {"value": "NOOB", "type": "NOOB"}

    def parse_assignment(self):
        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Invalid variable name for assignment")
            return

        variable_name = self.current_token.value
        self.advance_to_next_token()

        if not self.current_token or self.current_token.value != "R":
            self.log_syntax_error("Expected assignment operator 'R'")
            return

        self.advance_to_next_token()

        if not self.current_token:
            self.log_syntax_error("Missing value after assignment operator")
            return

        # Evaluate expression to get actual value
        value = self.evaluate_expression()
        
        # Determine type
        if isinstance(value, float):
            data_type = 'NUMBAR'
        elif isinstance(value, int):
            data_type = 'NUMBR'
        elif value in ['WIN', 'FAIL']:
            data_type = 'TROOF'
        elif isinstance(value, str):
            data_type = 'YARN'
        else:
            data_type = None
        
        self.variables[variable_name] = {"value": value, "type": data_type}

    def evaluate_typecasting(self):
        # evaluate MAEK A <var> <type> typecasting and return the casted value
        if self.current_token.value == 'MAEK':
            self.advance_to_next_token()

            if not self.current_token or self.current_token.value != 'A':
                self.log_syntax_error("Expected 'A' after 'MAEK'")
                return None

            self.advance_to_next_token()

            if not self.current_token:
                self.log_syntax_error("Expected value to cast after 'MAEK A'")
                return None

            # Get the value to cast
            if self.current_token.type == 'Variable Identifier':
                var_name = self.current_token.value
                if var_name in self.variables:
                    cast_value = self.variables[var_name].get('value', 'NOOB')
                else:
                    cast_value = 'NOOB'
            else:
                cast_value = self.current_token.value
            
            self.advance_to_next_token()

            if not self.current_token or self.current_token.type != 'Type Literal':
                self.log_syntax_error("Expected type literal after value in 'MAEK A' operation")
                return None

            target_type = self.current_token.value
            self.advance_to_next_token()

            # Perform the type conversion
            try:
                if target_type == 'TROOF':
                    # Convert to boolean
                    if cast_value == 'NOOB' or cast_value == '' or cast_value == 0 or cast_value == 0.0:
                        return 'FAIL'
                    else:
                        return 'WIN'
                elif target_type == 'NUMBR':
                    # Convert to integer
                    if isinstance(cast_value, str):
                        if cast_value == 'WIN':
                            return 1
                        elif cast_value == 'FAIL':
                            return 0
                        else:
                            return int(float(cast_value))
                    return int(cast_value)
                elif target_type == 'NUMBAR':
                    # Convert to float
                    if isinstance(cast_value, str):
                        if cast_value == 'WIN':
                            return 1.0
                        elif cast_value == 'FAIL':
                            return 0.0
                        else:
                            return float(cast_value)
                    return float(cast_value)
                elif target_type == 'YARN':
                    # Convert to string
                    return str(cast_value)
                else:
                    return cast_value
            except (ValueError, TypeError):
                return 'NOOB'
        
        return None

    def parse_typecasting(self):
        if self.current_token.value == 'MAEK':
            self.advance_to_next_token()

            if not self.current_token or self.current_token.value != 'A':
                self.log_syntax_error("Expected 'A' after 'MAEK'")
                return

            self.advance_to_next_token()

            if not self.current_token:
                self.log_syntax_error("Expected value to cast after 'MAEK A'")
                return

            cast_value = self.current_token.value
            self.advance_to_next_token()

            if not self.current_token or self.current_token.type != 'Type Literal':
                self.log_syntax_error("Expected type literal after value in 'MAEK A' operation")
                return

            self.advance_to_next_token()
        else:
            variable_name = self.current_token.value
            self.advance_to_next_token()

            if not self.current_token or self.current_token.value != 'IS NOW A':
                self.log_syntax_error("Expected 'IS NOW A' for typecasting")
                return

            self.advance_to_next_token()

            if not self.current_token or self.current_token.type != 'Type Literal':
                self.log_syntax_error("Expected type literal after 'IS NOW A'")
                return

            target_type = self.current_token.value
            self.advance_to_next_token()
            if variable_name in self.variables:
                self.variables[variable_name]['type'] = target_type

    def parse_print(self):
        self.advance_to_next_token()

        if not self.current_token:
            self.log_syntax_error("No output specified after VISIBLE")
            return

        output = []
        while self.current_token:
            if self.current_token.type == 'INVALID TOKEN':
                self.log_syntax_error(f"Invalid token in VISIBLE statement", found=self.current_token.value)
                return

            if self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal', 'TROOF Literal']:
                output.append(str(self.current_token.value))
                self.advance_to_next_token()
            elif self.current_token.type == 'Variable Identifier':
                # append variable value if exists, else name
                varname = self.current_token.value
                if varname in self.variables:
                    val = self.variables[varname].get("value", "NOOB")
                    output.append(str(val))
                else:
                    output.append(str(varname))
                self.advance_to_next_token()
            elif self.current_token.type == 'YARN Literal':
                output.append(self.current_token.value)
                self.advance_to_next_token()
            elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
                # Evaluate operation to get actual result
                result = self.evaluate_operation()
                output.append(str(result))
            elif self.current_token.type == 'String Concatenation':
                # Evaluate concatenation to get actual result
                result = self.evaluate_concatenation()
                output.append(str(result))
                break
            elif self.current_token.type in ['Parameter Delimiter', 'Output Separator']:
                self.advance_to_next_token()
            else:
                break

        # join and store result - semantics handles output
        final_output = " ".join(output).strip()
        if final_output:
            # store to IT
            self.variables["IT"] = {"value": final_output, "type": "YARN"}
            # Emit to console (GUI display)
            self.emit(final_output + "\n")

    def parse_input(self):
        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Missing variable identifier after GIMMEH")
            return

        variable_name = self.current_token.value
        
        # Check if variable was declared in WAZZUP block
        if variable_name not in self.variables:
            self.log_syntax_error(f"Undefined variable '{variable_name}' - must be declared in WAZZUP block")
            return
        
        # Capture input and store it in the variable
        try:
            input_value = self._get_input(f"Enter value for {variable_name}: ")
            self.semantics.store_input(variable_name, input_value)
            
            # Update the syntax analyzer's symbol table as well
            processed_value = self.semantics._process_input_value(input_value)
            self.variables[variable_name] = {"value": processed_value, "type": "YARN"}
            
        except Exception as e:
            self.log_syntax_error(f"Error capturing input for '{variable_name}': {str(e)}")
        
        self.advance_to_next_token()

    def parse_conditional(self):
        """
        Parse and execute conditional logic (O RLY?) per LOLCODE specification
        
        Syntax: <expression> O RLY?
                  YA RLY
                    <code block>
                  [MEBBE <expression>
                    <code block>]...
                  [NO WAI
                    <code block>]
                  OIC
        
        Semantics:
        - Evaluates IT variable (set by expression before O RLY?)
        - Executes YA RLY block if IT is WIN (true)
        - Evaluates MEBBE expressions in order, executes first WIN block
        - Executes NO WAI block only if no previous block executed
        - Ensures ONLY ONE branch executes (mutually exclusive)
        """
        if self.current_token.value != 'O RLY?':
            self.log_syntax_error("Expected 'O RLY?' for conditional block")
            return

        # Evaluate IT variable to determine which branch to execute
        branch_executed = self.semantics.evaluate_it_condition()
        
        self.advance_to_next_line()

        if not self.current_token or self.current_token.value != 'YA RLY':
            self.log_syntax_error("Expected 'YA RLY' after 'O RLY?'")
            return

        self.advance_to_next_line()

        # Execute or skip YA RLY block based on IT variable
        if branch_executed:
            self._execute_conditional_block(['MEBBE', 'NO WAI', 'OIC'])
        else:
            self._skip_conditional_block(['MEBBE', 'NO WAI', 'OIC'])

        # Handle MEBBE (else-if) blocks - only evaluate if no branch executed yet
        while self.current_token and self.current_token.value == 'MEBBE':
            self.advance_to_next_token()
            
            # Evaluate MEBBE expression only if no previous branch executed
            if not branch_executed:
                mebbe_expression = self.evaluate_expression()
                mebbe_result = self._to_bool(mebbe_expression)
            else:
                # Skip expression evaluation if a branch already executed
                self.evaluate_expression()  # Still need to consume the expression
                mebbe_result = False
            
            self.advance_to_next_line()
            
            # Execute MEBBE block if condition is True and no previous block executed
            if not branch_executed and mebbe_result:
                branch_executed = True  # Mark that we executed a block
                self._execute_conditional_block(['MEBBE', 'NO WAI', 'OIC'])
            else:
                self._skip_conditional_block(['MEBBE', 'NO WAI', 'OIC'])

        # Handle NO WAI (else) block - only execute if no branch executed yet
        if self.current_token and self.current_token.value == 'NO WAI':
            self.advance_to_next_line()

            if not branch_executed:
                self._execute_conditional_block(['OIC'])
            else:
                self._skip_conditional_block(['OIC'])

        if not self.current_token or self.current_token.value != 'OIC':
            self.log_syntax_error("Expected 'OIC' to close 'O RLY?' block")
    
    def _execute_conditional_block(self, end_keywords):
        """
        Execute a conditional block until one of the end keywords is reached
        
        Args:
            end_keywords: List of keywords that mark the end of this block
        """
        while True:
            if not self.current_token:
                if not self.advance_to_next_line():
                    break
                continue

            if self.current_token.value in end_keywords:
                break

            self.parse_line()
            self.advance_to_next_line()
    
    def _skip_conditional_block(self, end_keywords):
        """
        Skip a conditional block without executing until one of the end keywords is reached
        
        Args:
            end_keywords: List of keywords that mark the end of this block
        """
        while True:
            if not self.current_token:
                if not self.advance_to_next_line():
                    break
                continue

            if self.current_token.value in end_keywords:
                break

            self.advance_to_next_line()
    
    def _to_bool(self, value):
        """
        Helper method to convert a value to boolean
        """
        return self.semantics._to_bool(value)

    def parse_loop(self):
        if self.current_token.value != 'IM IN YR':
            self.log_syntax_error("Expected 'IM IN YR' to define a loop")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Expected loop label after 'IM IN YR'")
            return

        loop_label = self.current_token.value
        self.advance_to_next_token()

        if not self.current_token or self.current_token.value not in ['UPPIN', 'NERFIN']:
            self.log_syntax_error("Expected loop operation (UPPIN/NERFIN) after loop label")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.value != 'YR':
            self.log_syntax_error("Expected 'YR' after loop operation")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Expected variable name after 'YR'")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.value not in ['TIL', 'WILE']:
            self.log_syntax_error("Expected loop condition (TIL/WILE) after loop variable")
            return

        self.advance_to_next_token()

        condition_expression = self.parse_expression()
        if condition_expression is None:
            self.log_syntax_error("Invalid loop condition expression")
            return

        self.advance_to_next_line()

        while True:
            if not self.current_token:
                if not self.advance_to_next_line():
                    break
                continue

            if self.current_token.value == 'IM OUTTA YR':
                break

            self.parse_line()
            self.advance_to_next_line()

        if not self.current_token or self.current_token.value != 'IM OUTTA YR':
            self.log_syntax_error(f"Expected 'IM OUTTA YR {loop_label}' to close loop")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.value != loop_label:
            self.log_syntax_error(f"Expected loop label '{loop_label}' after 'IM OUTTA YR'")
        else:
            self.advance_to_next_token()

    def parse_switch(self):
        self.inside_switch_block = True

        if self.current_token.value != 'WTF?':
            self.log_syntax_error("Switch must start with 'WTF?'")
            return

        self.advance_to_next_line()
        found_cases = False

        while True:
            if not self.current_token:
                if not self.advance_to_next_line():
                    break
                continue

            if self.current_token.value == 'OIC':
                break

            if self.current_token.value == 'OMG':
                found_cases = True
                self.advance_to_next_token()

                if not self.current_token or self.current_token.type not in ['NUMBR Literal', 'NUMBAR Literal', 'YARN Literal', 'TROOF Literal']:
                    self.log_syntax_error("Expected literal value after 'OMG'")
                    return

                self.advance_to_next_line()

                while True:
                    if not self.current_token:
                        if not self.advance_to_next_line():
                            break
                        continue

                    if self.current_token.value in ['OMG', 'OMGWTF', 'OIC']:
                        break

                    self.parse_line()
                    self.advance_to_next_line()

            elif self.current_token.value == 'OMGWTF':
                found_cases = True
                self.advance_to_next_line()

                while True:
                    if not self.current_token:
                        if not self.advance_to_next_line():
                            break
                        continue

                    if self.current_token.value == 'OIC':
                        break

                    self.parse_line()
                    self.advance_to_next_line()
            else:
                self.parse_line()
                self.advance_to_next_line()

        if not self.current_token or self.current_token.value != 'OIC':
            self.log_syntax_error("Switch must end with 'OIC'")
        if not found_cases:
            self.log_syntax_error("Switch must have at least one case (OMG/OMGWTF)")

        self.inside_switch_block = False

    def parse_function(self):
        if self.current_token.value != 'HOW IZ I':
            self.log_syntax_error("Function must start with 'HOW IZ I'")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Expected function name after 'HOW IZ I'")
            return

        function_name = self.current_token.value
        self.advance_to_next_token()

        parameters = []
        while self.current_token:
            if self.current_token.value == 'YR':
                self.advance_to_next_token()

                if not self.current_token or self.current_token.type != 'Variable Identifier':
                    self.log_syntax_error("Expected parameter name after 'YR'")
                    return

                parameter_name = self.current_token.value
                parameters.append(parameter_name)
                self.advance_to_next_token()

                if self.current_token and self.current_token.value == 'AN':
                    self.advance_to_next_token()
                elif self.current_token and self.current_token.value == 'YR':
                    self.log_syntax_error("Expected 'AN' between multiple parameters")
                    return
            else:
                break

        self.advance_to_next_line()

        while True:
            if not self.current_token:
                if not self.advance_to_next_line():
                    break
                continue

            if self.current_token.value == 'IF U SAY SO':
                break

            if self.current_token.value == 'FOUND YR':
                self.advance_to_next_token()

                if not self.current_token:
                    self.log_syntax_error("Expected return value after 'FOUND YR'")
                    return

                if self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal', 'TROOF Literal', 'YARN Literal', 'Variable Identifier']:
                    self.advance_to_next_token()
                elif self.current_token.type == 'Arithmetic Operation':
                    self.parse_operation()
                else:
                    self.log_syntax_error("Invalid return value")
                    return

                self.advance_to_next_line()
                continue

            if self.current_token.value == 'GTFO':
                # GTFO is a void return (no value)
                self.advance_to_next_token()
                self.advance_to_next_line()
                continue

            self.parse_line()
            self.advance_to_next_line()

        if not self.current_token or self.current_token.value != 'IF U SAY SO':
            self.log_syntax_error("Function must end with 'IF U SAY SO'")
        else:
            self.advance_to_next_token()

    def parse_functioncall(self):
        if self.current_token.value != 'I IZ':
            self.log_syntax_error("Function call must start with 'I IZ'")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Expected function name after 'I IZ'")
            return

        function_name = self.current_token.value
        self.advance_to_next_token()

        while self.current_token:
            if self.current_token.value == 'YR':
                self.advance_to_next_token()

                if not self.current_token:
                    self.log_syntax_error("Expected argument after 'YR'")
                    return

                if self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal', 'TROOF Literal', 'YARN Literal', 'Variable Identifier']:
                    self.advance_to_next_token()
                elif self.current_token.type == 'Arithmetic Operation':
                    self.parse_operation()
                elif self.current_token.value == 'I IZ':
                    self.parse_functioncall()
                else:
                    self.log_syntax_error("Expected literal, variable, or function call after 'YR'")
                    return

                if self.current_token and self.current_token.value == 'AN':
                    self.advance_to_next_token()
                else:
                    break
            else:
                break

    def parse_line(self):
        print(f"\nParsing line {self.current_line_number}: {[t.value for t in self.current_tokens]}")

        while self.current_token:
            # Check for invalid tokens first
            if self.current_token.type == 'INVALID TOKEN':
                self.log_syntax_error(f"Invalid token '{self.current_token.value}'")
                return

            if self.current_token.value == 'WAZZUP':
                self.in_wazzup_block = True
                self.advance_to_next_token()
            elif self.current_token.value == 'BUHBYE' and self.in_wazzup_block:
                self.in_wazzup_block = False
                self.advance_to_next_token()
            elif self.current_token.value == 'I HAS A':
                # Allow variable declarations both inside and outside WAZZUP block
                self.parse_variable_declaration()
            elif self.current_token.type == 'Output Keyword':
                self.parse_print()
                # After printing, we're done with this line
                return
            elif self.current_token.type == 'Input Keyword':
                self.parse_input()
            elif self.current_token.value == 'O RLY?':
                self.parse_conditional()
                return
            elif self.current_token.value == 'IM IN YR':
                self.parse_loop()
                return
            elif self.current_token.value == 'HOW IZ I':
                self.parse_function()
                return
            elif self.current_token.value == 'I IZ':
                self.parse_functioncall()
            elif self.current_token.value == 'WTF?':
                self.parse_switch()
                return
            elif self.current_token.value == 'GTFO':
                # GTFO can be a break (in loops/switch) or void return (in functions)
                self.advance_to_next_token()
                return
            elif self.current_token.value in ['OMG', 'OMGWTF']:
                if not self.inside_switch_block:
                    self.log_syntax_error(f"Found '{self.current_token.value}' without preceding 'WTF?'")
                    return
                self.advance_to_next_token()
            elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation', 'String Concatenation']:
                # Standalone expression - evaluates and stores result in IT
                result = self.evaluate_expression()
                
                # Determine type
                if isinstance(result, float):
                    result_type = 'NUMBAR'
                elif isinstance(result, int):
                    result_type = 'NUMBR'
                elif result in ['WIN', 'FAIL']:
                    result_type = 'TROOF'
                elif isinstance(result, str):
                    result_type = 'YARN'
                else:
                    result_type = None
                
                self.variables['IT'] = {"value": result, "type": result_type}
                return
            elif self.current_token.type == 'Variable Identifier':
                next_token = self.current_tokens[self.current_position + 1] if self.current_position + 1 < len(self.current_tokens) else None
                if next_token and next_token.type == 'Variable Assignment':
                    self.parse_assignment()
                elif next_token and next_token.type == 'Typecasting Operation':
                    self.parse_typecasting()
                elif not next_token:
                    # Standalone variable expression - only valid if next line is WTF? (switch case)
                    # Check if the next line starts with WTF?
                    line_numbers = sorted(self.lines.keys())
                    current_index = line_numbers.index(self.current_line_number)
                    next_line_number = line_numbers[current_index + 1] if current_index + 1 < len(line_numbers) else None
                    
                    if next_line_number:
                        next_line_tokens = self.lines[next_line_number]
                        if next_line_tokens and next_line_tokens[0].value == 'WTF?':
                            # Valid: standalone expression before switch
                            if self.current_token.value not in self.variables:
                                self.log_syntax_error(f"Undefined variable '{self.current_token.value}'")
                                return
                            self.variables['IT'] = self.variables.get(self.current_token.value, {"value": None, "type": None})
                            self.advance_to_next_token()
                            return
                    
                    # Invalid: standalone identifier not before WTF?
                    self.log_syntax_error("Unknown statement", found=self.current_token.value)
                    return
                else:
                    # Unknown statement starting with Variable Identifier
                    self.log_syntax_error("Unknown statement", found=self.current_token.value)
                    return
            else:
                # General fallback for unrecognized tokens
                self.log_syntax_error("Unexpected or invalid statement", found=self.current_token.value)
                return

            self.advance_to_next_token()

    def parse_program(self):
        self.emit("\n" + "="*60 + "\n")
        self.emit("SYNTAX ANALYSIS\n")
        self.emit("="*60 + "\n")

        if self.current_token and self.current_token.value == "HAI":
            self.emit("\nProgram starts with 'HAI'\n")
            self.advance_to_next_line()

            while self.current_line_number is not None and self.current_token:
                if self.current_token.value == "KTHXBYE":
                    break

                self.parse_line()

                if self.error_messages and "Function must end with 'IF U SAY SO'" in self.error_messages[-1]:
                    break

                self.advance_to_next_line()

            if self.current_token and self.current_token.value == "KTHXBYE":
                self.emit("\nProgram ends with 'KTHXBYE'\n")
            else:
                if not any("Program must end with 'KTHXBYE'" in e for e in self.error_messages):
                    self.log_syntax_error("Program must end with 'KTHXBYE'")
        else:
            self.log_syntax_error("Program must start with 'HAI'")

        self.emit("\n" + "="*60 + "\n")
        self.emit("SYNTAX ANALYSIS RESULTS\n")
        self.emit("="*60 + "\n")

        if self.error_messages:
            self.emit("\nErrors Found:\n")
            for error in self.error_messages:
                self.emit(f"  {error}\n")
        else:
            self.emit("\nNo syntax errors found!\n")

        return self.variables



def analyze_syntax(tokens):
    # analyze syntax from tokenized LOLCODE
    analyzer = SyntaxAnalyzer(tokens)
    return analyzer.parse_program()


def menu():
    print("\n-----------------------------------")
    print("LOLCODE Syntax Analyzer")
    print("-----------------------------------")
    print("[1] Analyze LOLCODE File/Directory")
    print("[2] Analyze LOLCODE String")
    print("[3] Exit")


def main():
    while True:
        menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            content = readFile()
            if content:
                for filename, file_content in content.items():
                    print(f"\n{'='*60}")
                    print(f"File: {filename}")
                    print('='*60)
                    
                    # Tokenize
                    tokens = tokenize(file_content)
                    
                    # Analyze syntax
                    analyze_syntax(tokens)
            else:
                print("No content to analyze.")

        elif choice == '2':
            input_string = input("Enter LOLCODE string to analyze: ").replace("\\n", "\n")
            if input_string.strip():
                # Tokenize
                tokens = tokenize(input_string)
                
                # Analyze syntax
                analyze_syntax(tokens)
            else:
                print("No input string provided.")

        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
