'''
CMSC 124: LOLCODE Syntax Analyzer
- Sophia Ysabel Garcia
- James Andrei Tadeja
- Ron Russell Velasco
'''

from lexer_analyzer import tokenize, readFile
from semantics_analyzer import SemanticsEvaluator

# syntax analyzer for LOLCODE
class SyntaxAnalyzer:
    def __init__(self, tokens, log_function=None, input_function=None):
        # organize tokens by line number
        self.lines = self._organize_tokens_by_line(tokens)
        self.current_line_number = min(self.lines.keys()) if self.lines else None
        self.current_tokens = self.lines[self.current_line_number] if self.lines else []
        self.current_position = 0
        self.current_token = self.current_tokens[0] if self.current_tokens else None
        self.error_messages = []
        self.in_wazzup_block = False
        self.inside_switch_block = False

        self.log_function = log_function
        self.input_function = input_function
        
        # semantics evaluator with its own symbol table
        symbol_table = {"IT": {"value": "NOOB", "type": "NOOB"}}
        self.semantics = SemanticsEvaluator(symbol_table, emit_function=self.emit)
        
        # Flag to track GTFO in switch blocks
        self.gtfo_in_switch = False
        
        # Flags to track GTFO in loops
        self.inside_loop = False
        self.gtfo_in_loop = False
        
        # Track explicit typecast type for proper assignment
        self._last_typecast_type = None

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

    def _is_valid_variable_name(self, name):
        import re
        # Pattern: starts with letter, followed by letters/numbers/underscores
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, name))

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

    def _get_input(self, prompt):
        # Get input from user - handles both GUI and command line contexts
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
        if not self.current_token:
            return None

        # for number literals
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
        
        # for variables, look up their value using semantics
        elif self.current_token.type == 'Variable Identifier':
            var_name = self.current_token.value
            try:
                result = self.semantics.get_variable(var_name)
            except ValueError as e:
                # Variable not declared - log error but continue with NOOB
                self.log_syntax_error(f"Runtime Error: {str(e)}")
                result = 'NOOB'
            self.advance_to_next_token()
            return result
        
        # for operations, parse and evaluate them
        elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
            return self.parse_and_evaluate_operation()
        
        # for string concatenation
        elif self.current_token.type == 'String Concatenation':
            return self.parse_and_evaluate_concatenation()
        
        # for typecasting (MAEK A x TROOF)
        elif self.current_token.type == 'Typecasting Operation':
            return self.parse_and_evaluate_typecasting()
        
        else:
            return None

    def evaluate_expression_tokens(self, tokens):
        # Evaluate an expression given a list of tokens by temporarily swapping
        # the parser state to those tokens, calling `parse_expression`, then
        # restoring the previous state.
        # save parser state
        saved_state = (
            self.current_line_number,
            self.current_tokens,
            self.current_position,
            self.current_token
        )

        # set temporary state for evaluation
        self.current_tokens = tokens
        self.current_position = 0
        self.current_token = self.current_tokens[0] if self.current_tokens else None

        try:
            result = self.parse_expression()
        finally:
            # restore previous state
            (self.current_line_number,
             self.current_tokens,
             self.current_position,
             self.current_token) = saved_state

        return result

    def parse_and_evaluate_operation(self):
        # Parse and evaluate an operation, delegating computation to semantics
        operation = self.current_token.value
        self.advance_to_next_token()

        # Handle different operation types
        if operation == 'NOT':
            return self._parse_and_eval_unary_operation(operation)
        elif operation in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            return self._parse_and_eval_binary_operation(operation)
        elif operation in ['BOTH OF', 'EITHER OF', 'WON OF']:
            return self._parse_and_eval_boolean_operation(operation)
        elif operation in ['BOTH SAEM', 'DIFFRINT']:
            return self._parse_and_eval_comparison_operation(operation)
        elif operation in ['ALL OF', 'ANY OF']:
            return self._parse_and_eval_infinite_arity_operation(operation)
        elif operation == 'SMOOSH':
            return self.parse_and_evaluate_concatenation()
        else:
            return None
    
    def _parse_and_eval_unary_operation(self, operation):
        # Parse and evaluate NOT operation using semantics
        if not self.current_token:
            return None
        
        # Get the operand value
        operand_value = self.parse_expression()
        
        if operand_value is None:
            return None
        
        # Use semantics to evaluate
        result = self.semantics.evaluate_unary_not(operand_value)
        
        # Store result in IT variable using semantics
        self.semantics.store_result(result, "TROOF")
        
        return result
    
    def _parse_and_eval_binary_operation(self, operation):
        # Parse and evaluate arithmetic binary operations using semantics
        # Get first operand
        first_operand = self.parse_expression()
        
        # Expect AN keyword between operands
        if not self.current_token or self.current_token.value != 'AN':
            return None
        self.advance_to_next_token()
        
        # Get second operand
        second_operand = self.parse_expression()
        
        # Use semantics to evaluate - raises error if typecast fails
        try:
            result = self.semantics.evaluate_arithmetic(operation, first_operand, second_operand)
        except ValueError as e:
            self.log_syntax_error(f"Runtime Error: {e}")
            return 'NOOB'
        
        # Infer result type using semantics
        result_type = self.semantics.infer_type(result)
        
        # Store result in IT variable using semantics
        self.semantics.store_result(result, result_type)
        
        return result
    
    def _parse_and_eval_boolean_operation(self, operation):
        # Parse and evaluate boolean operations using semantics
        # Get first operand
        first_operand = self.parse_expression()
        
        # Expect AN keyword
        if not self.current_token or self.current_token.value != 'AN':
            return None
        self.advance_to_next_token()
        
        # Get second operand
        second_operand = self.parse_expression()
        
        # Use semantics to evaluate (returns NOOB on error)
        result = self.semantics.evaluate_boolean(operation, first_operand, second_operand)
        
        # Store result in IT variable using semantics
        self.semantics.store_result(result, "TROOF")
        
        return result
    
    def _parse_and_eval_comparison_operation(self, operation):
        # Parse and evaluate comparison operations using semantics
        # Get first operand
        first_operand = self.parse_expression()
        
        # Expect AN keyword
        if not self.current_token or self.current_token.value != 'AN':
            return None
        self.advance_to_next_token()
        
        # Check for relational comparison pattern:
        # BOTH SAEM x AN BIGGR OF x AN y (x >= y)
        # DIFFRINT x AN BIGGR OF x AN y (x < y)
        # BOTH SAEM x AN SMALLR OF x AN y (x <= y)
        # DIFFRINT x AN SMALLR OF x AN y (x > y)
        if self.current_token and self.current_token.value in ['BIGGR OF', 'SMALLR OF']:
            minmax_op = self.current_token.value
            self.advance_to_next_token()
            
            # Get operands for BIGGR OF / SMALLR OF
            minmax_operand1 = self.parse_expression()
            
            # Expect AN keyword
            if not self.current_token or self.current_token.value != 'AN':
                self.log_syntax_error(f"Expected 'AN' after first operand of {minmax_op}")
                return "NOOB"
            self.advance_to_next_token()
            
            minmax_operand2 = self.parse_expression()
            
            # Use semantics to evaluate relational comparison - raises error if typecast fails
            try:
                result = self.semantics.evaluate_relational_comparison(
                    operation, first_operand, minmax_op, minmax_operand1, minmax_operand2
                )
            except ValueError as e:
                self.log_syntax_error(f"Runtime Error: {e}")
                return "NOOB"
            
            # Store result in IT variable using semantics
            self.semantics.store_result(result, "TROOF")
            
            return result
        else:
            # Regular comparison (BOTH SAEM or DIFFRINT)
            second_operand = self.parse_expression()
            
            # Use semantics to evaluate (returns NOOB on error)
            result = self.semantics.evaluate_comparison(operation, first_operand, second_operand)
            
            # Store result in IT variable using semantics
            self.semantics.store_result(result, "TROOF")
            
            return result
    
    def _parse_and_eval_infinite_arity_operation(self, operation, nested=False):
        # Parse and evaluate ALL OF or ANY OF operations using semantics
        # ALL OF and ANY OF cannot be nested into each other or themselves
        if nested:
            self.log_syntax_error(f"Cannot nest {operation} inside another ALL OF or ANY OF")
            return 'NOOB'
        
        operands = []
        
        while self.current_token and self.current_token.value != 'MKAY':
            # Skip AN delimiter
            if self.current_token.value == 'AN':
                self.advance_to_next_token()
                continue
            
            # Check for nested ALL OF or ANY OF - NOT allowed
            if self.current_token and self.current_token.value in ['ALL OF', 'ANY OF']:
                self.log_syntax_error(f"Cannot nest {self.current_token.value} inside {operation}")
                return 'NOOB'
            
            # Evaluate operand (other boolean ops like NOT, BOTH OF, etc. are allowed)
            operand = self.parse_expression()
            if operand is not None:
                operands.append(operand)
            else:
                break
        
        # Consume MKAY
        if self.current_token and self.current_token.value == 'MKAY':
            self.advance_to_next_token()
        else:
            self.log_syntax_error(f"Expected 'MKAY' to close {operation}")
        
        # Use semantics to evaluate
        result = self.semantics.evaluate_infinite_arity(operation, operands)
        
        # Store in IT using semantics
        self.semantics.store_result(result, "TROOF")
        
        return result
    
    def parse_and_evaluate_concatenation(self):
        """Parse and evaluate SMOOSH using semantics"""
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
                try:
                    operands.append(self.semantics.get_variable(var_name))
                except ValueError as e:
                    self.log_syntax_error(f"Runtime Error: {str(e)}")
                    operands.append('NOOB')
                self.advance_to_next_token()
            elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
                result = self.parse_and_evaluate_operation()
                operands.append(result)
            elif self.current_token.type == 'String Concatenation':
                break
            else:
                break
        
        # Use semantics to concatenate (includes validation)
        try:
            result = self.semantics.evaluate_concatenation(operands)
        except ValueError as e:
            self.log_syntax_error(f"Runtime Error: {str(e)}")
            result = ''
        
        # Store in IT using semantics
        self.semantics.store_result(result, "YARN")
        
        return result
    
    def parse_and_evaluate_typecasting(self):
        # Parse and evaluate MAEK [A] <var> <type> typecasting using semantics
        # MAEK returns the typecast value to IT, does NOT modify the original variable
        # Syntax: MAEK var1 A NUMBAR  OR  MAEK var1 NUMBAR (A is optional)
        if self.current_token.value == 'MAEK':
            self.advance_to_next_token()

            # 'A' is optional after MAEK
            if self.current_token and self.current_token.value == 'A':
                self.advance_to_next_token()

            if not self.current_token:
                self.log_syntax_error("Expected value to cast after 'MAEK'")
                return None

            # Get the value to cast
            if self.current_token.type == 'Variable Identifier':
                var_name = self.current_token.value
                try:
                    cast_value = self.semantics.get_variable(var_name)
                except ValueError:
                    cast_value = 'NOOB'
            else:
                cast_value = self.current_token.value
            
            self.advance_to_next_token()
            
            # Check for optional 'A' between value and type (MAEK var A TYPE)
            if self.current_token and self.current_token.value == 'A':
                self.advance_to_next_token()

            if not self.current_token or self.current_token.type != 'Type Literal':
                self.log_syntax_error("Expected type literal in MAEK operation")
                return None

            target_type = self.current_token.value
            self.advance_to_next_token()
            
            # Store the explicit target type for use in assignment
            self._last_typecast_type = target_type

            # Use semantics to perform typecast - handle errors gracefully
            try:
                return self.semantics.typecast_value(cast_value, target_type)
            except ValueError as e:
                self.log_syntax_error(f"Runtime Error: {e}")
                return 'NOOB'
        
        return None

    def parse_variable_declaration(self):
        # Enforce that variable declarations must be inside WAZZUP block
        if not self.in_wazzup_block:
            self.log_syntax_error("Variable declaration using 'I HAS A' must be inside WAZZUP...BUHBYE block")
            # Still consume the tokens to avoid cascading errors
            self.advance_to_next_token()
            if self.current_token and self.current_token.type == 'Variable Identifier':
                self.advance_to_next_token()
            return
        
        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Variable name is missing or invalid after 'I HAS A'")
            return

        variable_name = self.current_token.value
        
        # Validate variable name format (must start with letter, then letters/numbers/underscores)
        if not self._is_valid_variable_name(variable_name):
            self.log_syntax_error(f"Invalid variable name '{variable_name}'. Variable names must start with a letter, followed by letters, numbers, or underscores only")
            return
        
        self.advance_to_next_token()

        if self.current_token and self.current_token.value == "ITZ":
            self.advance_to_next_token()

            if not self.current_token:
                self.log_syntax_error(f"Missing expression to initialize variable '{variable_name}' after 'ITZ'")
                return

            # Parse and evaluate expression to get actual value
            value = self.parse_expression()
            
            # Check for unexpected tokens after the initialization expression
            if self.current_token:
                self.log_syntax_error(f"Unexpected token '{self.current_token.value}' after variable initialization. Expected end of line or comment.")
                return
            
            # Let semantics infer the type from the value
            data_type = self.semantics.infer_type(value)
            
            # Use semantics to declare variable
            try:
                self.semantics.declare_variable(variable_name, value, data_type)
            except ValueError as e:
                self.log_syntax_error(str(e))
        else:
            # Check for unexpected tokens after variable name (when no ITZ)
            if self.current_token:
                self.log_syntax_error(f"Unexpected token '{self.current_token.value}' after variable declaration. Expected end of line or comment.")
                return
            
            # Use semantics to declare uninitialized variable
            try:
                self.semantics.declare_variable(variable_name)
            except ValueError as e:
                self.log_syntax_error(str(e))

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

        # Parse and evaluate expression to get actual value
        value = self.parse_expression()
        
        # Check for unexpected tokens after the assignment expression
        if self.current_token:
            self.log_syntax_error(f"Unexpected token '{self.current_token.value}' after assignment expression. Expected end of line or comment.")
            return
        
        # Check if this was an explicit typecast (MAEK) - use that type instead of inferring
        if self._last_typecast_type:
            data_type = self._last_typecast_type
            self._last_typecast_type = None  # Reset after use
        else:
            # Determine type based on value using semantics
            data_type = self.semantics.infer_type(value)
        
        # Use semantics to assign variable
        try:
            self.semantics.assign_variable(variable_name, value, data_type)
        except ValueError as e:
            self.log_syntax_error(str(e))

    def parse_typecasting(self):
        # Handles IS NOW A (modifies variable) and MAEK in statement context
        if self.current_token.value == 'MAEK':
            # This path handles MAEK when called from statement context
            # Note: standalone MAEK is handled in parse_line which stores to IT
            self.advance_to_next_token()

            # 'A' is optional after MAEK
            if self.current_token and self.current_token.value == 'A':
                self.advance_to_next_token()

            if not self.current_token:
                self.log_syntax_error("Expected value to cast after 'MAEK'")
                return

            cast_value = self.current_token.value
            self.advance_to_next_token()
            
            # Check for optional 'A' between value and type
            if self.current_token and self.current_token.value == 'A':
                self.advance_to_next_token()

            if not self.current_token or self.current_token.type != 'Type Literal':
                self.log_syntax_error("Expected type literal in MAEK operation")
                return

            self.advance_to_next_token()
        else:
            # IS NOW A - modifies the variable's type in place
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
            # Use semantics to typecast variable (IS NOW A) - modifies variable in place
            try:
                self.semantics.typecast_variable(variable_name, target_type)
            except ValueError as e:
                self.log_syntax_error(str(e))

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
                # get variable value using semantics
                varname = self.current_token.value
                try:
                    val = self.semantics.get_variable(varname)
                    output.append(str(val))
                except ValueError as e:
                    # Variable not declared - this is an error
                    self.log_syntax_error(f"Undefined variable: {varname}")
                    return
                self.advance_to_next_token()
            elif self.current_token.type == 'YARN Literal':
                output.append(self.current_token.value)
                self.advance_to_next_token()
            elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation']:
                # Parse and evaluate operation to get actual result
                result = self.parse_and_evaluate_operation()
                output.append(str(result))
            elif self.current_token.type == 'String Concatenation':
                # Parse and evaluate concatenation to get actual result
                result = self.parse_and_evaluate_concatenation()
                output.append(str(result))
                break
            elif self.current_token.type in ['Parameter Delimiter', 'Output Separator']:
                self.advance_to_next_token()
            else:
                # Unexpected token found - this is an error
                self.log_syntax_error(f"Unexpected token '{self.current_token.value}' in VISIBLE statement. Expected expression, separator, or end of line.")
                return

        # Use semantics to execute output
        if output:
            self.semantics.execute_output(output)

    def parse_input(self):
        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Missing variable identifier after GIMMEH")
            return

        variable_name = self.current_token.value
        
        self.advance_to_next_token()
        
        # Check for unexpected tokens after variable name
        if self.current_token:
            self.log_syntax_error(f"Unexpected token '{self.current_token.value}' after GIMMEH statement. Expected end of line or comment.")
            return
        
        # Capture input and store it in the variable
        try:
            input_value = self._get_input(f"Enter value for {variable_name}: ")
            # Let semantics handle validation and storage
            self.semantics.store_input(variable_name, input_value)
        except ValueError as e:
            # Semantics will raise ValueError if variable not declared
            self.log_syntax_error(f"Undefined variable '{variable_name}' - must be declared in WAZZUP block")
        except Exception as e:
            self.log_syntax_error(f"Error capturing input for '{variable_name}': {str(e)}")

    def parse_conditional(self):
        # Parse and execute conditional logic (O RLY?) per LOLCODE specification
        if self.current_token.value != 'O RLY?':
            self.log_syntax_error("Expected 'O RLY?' for conditional block")
            return

        # Use semantics to determine which branch to execute
        branch_executed = self.semantics.should_execute_branch('YA RLY')
        
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
            
            # Parse and evaluate MEBBE expression only if no previous branch executed
            if not branch_executed:
                mebbe_expression = self.parse_expression()
                # Use semantics to check if MEBBE should execute
                mebbe_result = self.semantics.should_execute_branch('MEBBE', mebbe_expression)
            else:
                # Skip expression evaluation if a branch already executed
                self.parse_expression()  # Still need to consume the expression
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
        # Execute a conditional block until one of the end keywords is reached
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
        # Skip a conditional block without executing until one of the end keywords is reached
        while True:
            if not self.current_token:
                if not self.advance_to_next_line():
                    break
                continue

            if self.current_token.value in end_keywords:
                break

            self.advance_to_next_line()
    
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

        loop_operation = self.current_token.value  # 'UPPIN' or 'NERFIN'
        self.advance_to_next_token()

        if not self.current_token or self.current_token.value != 'YR':
            self.log_syntax_error("Expected 'YR' after loop operation")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Expected variable name after 'YR'")
            return

        loop_variable = self.current_token.value
        self.advance_to_next_token()

        # TIL/WILE condition is OPTIONAL - check if present
        loop_type = None  # None means infinite loop (only GTFO can exit)
        condition_tokens = []
        
        if self.current_token and self.current_token.value in ['TIL', 'WILE']:
            loop_type = self.current_token.value
            self.advance_to_next_token()

            # Capture condition expression tokens
            condition_tokens = self.current_tokens[self.current_position:]
            if not condition_tokens:
                self.log_syntax_error("Invalid loop condition expression")
                return

        # Move to the first line of the loop body
        self.advance_to_next_line()

        # Save the start of the loop body so we can reset to it for each iteration
        loop_body_start_line = self.current_line_number
        loop_body_start_position = 0

        # Track if we're inside this loop for GTFO handling
        self.inside_loop = True
        self.gtfo_in_loop = False

        # Main loop execution
        loop_executed_at_least_once = False
        while True:
            # Evaluate condition if TIL/WILE was specified
            if loop_type is not None:
                condition_value = self.evaluate_expression_tokens(condition_tokens)
                try:
                    should_continue = self.semantics.evaluate_loop_condition(loop_type, condition_value)
                except Exception as e:
                    self.log_syntax_error(f"Runtime Error evaluating loop condition: {e}")
                    self.inside_loop = False
                    return

                if not should_continue:
                    break
            # If no condition (infinite loop), always continue unless GTFO

            loop_executed_at_least_once = True

            # Execute loop body from saved start
            if loop_body_start_line is None:
                break

            self.current_line_number = loop_body_start_line
            self.current_tokens = self.lines[self.current_line_number]
            self.current_position = loop_body_start_position
            self.current_token = self.current_tokens[self.current_position] if self.current_tokens else None

            # Execute until we hit the loop terminator or GTFO
            while self.current_token and self.current_token.value != 'IM OUTTA YR':
                self.parse_line()
                
                # Check for GTFO (break) inside loop
                if self.gtfo_in_loop:
                    break
                    
                if getattr(self, 'returning', False):
                    break
                self.advance_to_next_line()

            # Check if GTFO was issued - break out of loop entirely
            if self.gtfo_in_loop:
                break

            # After executing body, update loop variable using semantics
            try:
                if loop_operation == 'UPPIN':
                    self.semantics.increment_variable(loop_variable)
                else:
                    self.semantics.decrement_variable(loop_variable)
            except Exception as e:
                self.log_syntax_error(f"Runtime Error updating loop variable: {e}")
                self.inside_loop = False
                return

            # If the next token is the loop terminator, break out
            if not self.current_line_number:
                break

        # Reset loop flags
        self.inside_loop = False
        self.gtfo_in_loop = False

        # After loop terminates, advance until we find the closing IM OUTTA YR
        if not loop_executed_at_least_once:
            # Skip lines until we find IM OUTTA YR
            while self.current_line_number is not None:
                if self.current_token and self.current_token.value == 'IM OUTTA YR':
                    break
                self.advance_to_next_line()
        else:
            # Loop executed at least once, find IM OUTTA YR
            while self.current_token is None or self.current_token.value != 'IM OUTTA YR':
                if self.current_line_number is None:
                    break
                if self.current_token and self.current_token.value == 'IM OUTTA YR':
                    break
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

        # Get the IT variable value for comparison
        try:
            switch_value = self.semantics.get_variable('IT')
        except ValueError:
            switch_value = 'NOOB'

        self.advance_to_next_line()
        found_cases = False
        matched_case = False  # Track if a case has matched (for fall-through)
        self.gtfo_in_switch = False  # Reset GTFO flag
        case_values = []  # Track case values for duplicate detection

        while True:
            if not self.current_token:
                if not self.advance_to_next_line():
                    break
                continue

            if self.current_token.value == 'OIC':
                break

            # If GTFO was encountered, skip all remaining cases to OIC
            if self.gtfo_in_switch:
                if self.current_token.value == 'OMG':
                    # Skip the OMG case entirely
                    self.advance_to_next_token()  # Skip 'OMG'
                    if self.current_token and self.current_token.type in ['NUMBR Literal', 'NUMBAR Literal', 'YARN Literal', 'TROOF Literal']:
                        case_values.append(self.current_token.value)  # Still track for duplicate detection
                        self.advance_to_next_line()
                    # Skip the case body
                    while True:
                        if not self.current_token:
                            if not self.advance_to_next_line():
                                break
                            continue
                        if self.current_token.value in ['OMG', 'OMGWTF', 'OIC']:
                            break
                        self.advance_to_next_line()
                    continue
                elif self.current_token.value == 'OMGWTF':
                    # Skip the OMGWTF case entirely
                    self.advance_to_next_line()
                    while True:
                        if not self.current_token:
                            if not self.advance_to_next_line():
                                break
                            continue
                        if self.current_token.value == 'OIC':
                            break
                        self.advance_to_next_line()
                    continue
                elif self.current_token.value == 'OIC':
                    break
                else:
                    self.advance_to_next_line()
                    continue

            if self.current_token.value == 'OMG':
                found_cases = True
                self.advance_to_next_token()

                if not self.current_token or self.current_token.type not in ['NUMBR Literal', 'NUMBAR Literal', 'YARN Literal', 'TROOF Literal']:
                    self.log_syntax_error("Expected literal value after 'OMG'")
                    return

                case_value = self.current_token.value
                case_values.append(case_value)
                
                self.advance_to_next_line()

                # Check if this case matches OR if we're in fall-through mode
                if matched_case or self.semantics.match_case(switch_value, case_value):
                    matched_case = True  # Enable fall-through for subsequent cases
                    
                    # Execute this case block until OMG, OMGWTF, OIC, or GTFO
                    while True:
                        if not self.current_token:
                            if not self.advance_to_next_line():
                                break
                            continue

                        if self.current_token.value in ['OMG', 'OMGWTF', 'OIC']:
                            break

                        # Check for GTFO flag set by parse_line
                        if self.gtfo_in_switch:
                            break

                        self.parse_line()
                        self.advance_to_next_line()
                    
                    # Continue to next case (fall-through if no GTFO)
                    continue
                else:
                    # Skip this case block - doesn't match and not in fall-through
                    while True:
                        if not self.current_token:
                            if not self.advance_to_next_line():
                                break
                            continue

                        if self.current_token.value in ['OMG', 'OMGWTF', 'OIC']:
                            break

                        self.advance_to_next_line()

            elif self.current_token.value == 'OMGWTF':
                found_cases = True
                
                # Execute default if in fall-through OR if no case matched yet
                if matched_case or not matched_case:
                    # Always execute OMGWTF if we reach it (either fall-through or no match)
                    # But only if we're in fall-through mode OR no case has matched
                    should_execute = matched_case or True  # Fall-through continues here
                    
                    # Actually, OMGWTF executes if: (1) no case matched, or (2) we're falling through
                    self.advance_to_next_line()

                    while True:
                        if not self.current_token:
                            if not self.advance_to_next_line():
                                break
                            continue

                        if self.current_token.value == 'OIC':
                            break

                        # Check for GTFO flag set by parse_line
                        if self.gtfo_in_switch:
                            break

                        self.parse_line()
                        self.advance_to_next_line()
                    continue
            else:
                self.parse_line()
                self.advance_to_next_line()

        if not self.current_token or self.current_token.value != 'OIC':
            self.log_syntax_error("Switch must end with 'OIC'")
        if not found_cases:
            self.log_syntax_error("Switch must have at least one case (OMG/OMGWTF)")
        
        # Validate for duplicate case values using semantics
        try:
            self.semantics.validate_switch_cases(case_values)
        except ValueError as e:
            self.log_syntax_error(str(e))

        self.inside_switch_block = False
        self.gtfo_in_switch = False  # Reset flag when exiting switch

    def parse_function(self):
        if self.current_token.value != 'HOW IZ I':
            self.log_syntax_error("Function must start with 'HOW IZ I'")
            return

        self.advance_to_next_token() # move past 'HOW IZ I'

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Expected function name after 'HOW IZ I'")
            return

        function_name = self.current_token.value
        self.advance_to_next_token()

        # parse parameters
        parameters = []
        while self.current_token:
            if self.current_token.value == 'YR':
                self.advance_to_next_token()

                if not self.current_token or self.current_token.type != 'Variable Identifier':
                    self.log_syntax_error("Expected parameter name after 'YR'")
                    return

                parameter_name = self.current_token.value 
                parameters.append(parameter_name) # store parameter name
                self.advance_to_next_token() # move past parameter

                # check for AN between multiple parameters
                if self.current_token and self.current_token.value == 'AN':
                    self.advance_to_next_token()
                elif self.current_token and self.current_token.value == 'YR':
                    self.log_syntax_error("Expected 'AN' between multiple parameters")
                    return
            else:
                break

        self.advance_to_next_line() 
        
        # Store function definition with start line using semantics
        # We are currently at the first line of the body
        try:
            self.semantics.define_function(function_name, parameters, self.current_line_number)
        except ValueError as e:
            self.log_syntax_error(str(e))
            return

        # Skip function body
        while True: 
            if not self.current_token:
                if not self.advance_to_next_line():
                    break
                continue

            # check for function end
            if self.current_token.value == 'IF U SAY SO':
                break
            
            # Just skip lines until we find the end
            self.advance_to_next_line()

        if not self.current_token or self.current_token.value != 'IF U SAY SO':
            self.log_syntax_error("Function must end with 'IF U SAY SO'")
        else:
            self.advance_to_next_token()

    def parse_functioncall(self):
        # parse function call syntax and delegate execution to semantics
        if self.current_token.value != 'I IZ':
            self.log_syntax_error("Function call must start with 'I IZ'")
            return

        self.advance_to_next_token()

        if not self.current_token or self.current_token.type != 'Variable Identifier':
            self.log_syntax_error("Expected function name after 'I IZ'")
            return

        function_name = self.current_token.value
        self.advance_to_next_token()
        
        # Parse arguments (syntax parsing only)
        arguments = []
        while self.current_token:
            if self.current_token.value == 'YR':
                self.advance_to_next_token()

                if not self.current_token:
                    self.log_syntax_error("Expected argument after 'YR'")
                    return

                if self.current_token.value == 'I IZ':
                    # Nested function call
                    self.parse_functioncall()
                    # Result is in IT
                    try:
                        val = self.semantics.get_variable('IT')
                        arguments.append(val)
                    except ValueError:
                        arguments.append("NOOB")
                else:
                    # Parse expression for argument
                    val = self.parse_expression()
                    arguments.append(val)

                if self.current_token and self.current_token.value == 'AN':
                    self.advance_to_next_token()
                else:
                    break
            else:
                break
        
        # Delegate execution to semantics
        try:
            # Create a callback for executing the function body
            def execute_body(start_line, end_marker):
                # Save current parser state
                saved_state = (
                    self.current_line_number,
                    self.current_tokens,
                    self.current_position,
                    self.current_token
                )
                
                # Jump to function body
                self.current_line_number = start_line
                self.current_tokens = self.lines[self.current_line_number]
                self.current_position = 0
                self.current_token = self.current_tokens[0] if self.current_tokens else None
                
                # Execute body until end marker or return
                self.returning = False
                try:
                    while self.current_line_number is not None:
                        if not self.current_token:
                            if not self.advance_to_next_line():
                                break
                            continue
                        
                        if self.current_token.value == end_marker:
                            break
                        
                        self.parse_line()
                        
                        if getattr(self, 'returning', False):
                            break
                        
                        self.advance_to_next_line()
                finally:
                    # Restore parser state
                    (self.current_line_number,
                     self.current_tokens,
                     self.current_position,
                     self.current_token) = saved_state
                    self.returning = False
            
            # Execute function via semantics (handles scope management)
            self.semantics.execute_function(function_name, arguments, execute_body)
            
        except ValueError as e:
            self.log_syntax_error(str(e))

    def parse_line(self):
        # print(f"\nParsing line {self.current_line_number}: {[t.value for t in self.current_tokens]}")

        # Skip execution if syntax errors have been found
        if self.error_messages:
            return

        while self.current_token:
            # check for invalid tokens first
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
                # Variable declarations must be inside WAZZUP block
                self.parse_variable_declaration()
            elif self.current_token.type == 'Output Keyword':
                self.parse_print()
                # after printing, we're done with this line
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
            elif self.current_token.value == 'FOUND YR':
                self.advance_to_next_token()
                if not self.current_token:
                    self.log_syntax_error("Expected return value after 'FOUND YR'")
                    return
                
                # Parse return value
                ret_val = self.parse_expression()
                self.semantics.return_value(ret_val)
                self.returning = True
                return
            elif self.current_token.value == 'GTFO':
                # GTFO can be a break (in loops/switch) or void return (in functions)
                self.advance_to_next_token()
                
                # Priority: loop > switch > function return
                if self.inside_loop:
                    # GTFO breaks out of the loop
                    self.gtfo_in_loop = True
                    return
                elif self.inside_switch_block:
                    # GTFO breaks out of switch
                    self.gtfo_in_switch = True
                    return
                else:
                    # GTFO in function context is void return
                    self.semantics.return_void()
                    self.returning = True
                return
            elif self.current_token.value in ['OMG', 'OMGWTF']:
                if not self.inside_switch_block:
                    self.log_syntax_error(f"Found '{self.current_token.value}' without preceding 'WTF?'")
                    return
                self.advance_to_next_token()
            elif self.current_token.type in ['Arithmetic Operation', 'Boolean Operation', 'Comparison Operation', 'String Concatenation']:
                # Parse and evaluate expression, stores result in IT via semantics
                result = self.parse_expression()
                
                # Infer type using semantics
                result_type = self.semantics.infer_type(result)
                
                # Store result in IT using semantics
                self.semantics.store_result(result, result_type)
                return
            elif self.current_token.value == 'MAEK':
                # Standalone MAEK expression - stores result in IT
                # MAEK var1 A NUMBAR -> returns result to IT, does NOT modify var1
                result = self.parse_and_evaluate_typecasting()
                
                if result is not None:
                    # Infer type and store result in IT using semantics
                    result_type = self.semantics.infer_type(result)
                    self.semantics.store_result(result, result_type)
                return
            elif self.current_token.type == 'Variable Identifier':
                next_token = self.current_tokens[self.current_position + 1] if self.current_position + 1 < len(self.current_tokens) else None
                if next_token and next_token.type == 'Variable Assignment':
                    self.parse_assignment()
                elif next_token and next_token.type == 'Typecasting Operation':
                    self.parse_typecasting()
                elif not next_token:
                    # Standalone variable - check if next line starts with WTF? or O RLY?
                    line_numbers = sorted(self.lines.keys())
                    current_index = line_numbers.index(self.current_line_number)
                    next_line_number = line_numbers[current_index + 1] if current_index + 1 < len(line_numbers) else None
                    
                    if next_line_number:
                        next_line_tokens = self.lines[next_line_number]
                        if next_line_tokens and next_line_tokens[0].value in ['WTF?', 'O RLY?']:
                            # Standalone expression before switch or conditional
                            # Copy variable value to IT using semantics
                            try:
                                var_value = self.semantics.get_variable(self.current_token.value)
                                var_type = self.semantics.infer_type(var_value)
                                self.semantics.store_result(var_value, var_type)
                            except ValueError:
                                self.log_syntax_error(f"Undefined variable '{self.current_token.value}'")
                                return
                            self.advance_to_next_token()
                            return
                    
                    # invalid: standalone identifier not before WTF? or O RLY?
                    self.log_syntax_error("Unknown statement", found=self.current_token.value)
                    return
                else:
                    # unknown statement starting with Variable Identifier
                    self.log_syntax_error("Unknown statement", found=self.current_token.value)
                    return
            else:
                # general fallback for unrecognized tokens
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

        # Return the symbol table from semantics
        return self.semantics.symbol_table



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
                    
                    # tokenize
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
