from lexer_analyzer import tokenize
from syntax_analyzer import SyntaxAnalyzer

code = """HAI
    WAZZUP
        I HAS A number ITZ 17
    BUHBYE
    number R MAEK number YARN
    VISIBLE number
KTHXBYE"""

tokens = tokenize(code)
analyzer = SyntaxAnalyzer(tokens)

# Patch parse_expression to debug
original_parse = analyzer.parse_expression
def debug_parse():
    print(f'  parse_expression called, token: {analyzer.current_token}')
    result = original_parse()
    print(f'  parse_expression returned: {result!r}')
    return result
analyzer.parse_expression = debug_parse

result = analyzer.parse_program()
print(f'Final number: {result.get("number")}')
