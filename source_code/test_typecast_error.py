from lexer_analyzer import tokenize
from syntax_analyzer import SyntaxAnalyzer

code = '''HAI
    WAZZUP
        I HAS A y
    BUHBYE
    
    y R 100
    y IS NOW A NUMBAR ?
    VISIBLE y
KTHXBYE'''

print("Testing: y IS NOW A NUMBAR ?")
print("="*60)

# Tokenize
tokens = tokenize(code)

print("\nTokens on line 7:")
for token in tokens:
    if token.line_number == 7:
        print(f"  {token.type:<30} = '{token.value}'")

print("\n" + "="*60)
print("Parsing...")
print("="*60)

# Parse and analyze
parser = SyntaxAnalyzer(tokens)
parser.parse_program()

print("\n" + "="*60)
if parser.error_messages:
    print("[OK] Error correctly detected!")
    for error in parser.error_messages:
        print(f"  {error}")
else:
    print("[FAIL] No error detected - bug still present!")
