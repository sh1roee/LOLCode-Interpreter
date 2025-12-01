from lexer_analyzer import tokenize
from syntax_analyzer import SyntaxAnalyzer

test_cases = [
    ("HAI with extra tokens", '''HAI hello world
    WAZZUP
        I HAS A x
    BUHBYE
KTHXBYE'''),
    
    ("KTHXBYE with extra tokens", '''HAI
    WAZZUP
        I HAS A x
    BUHBYE
KTHXBYE ok pi'''),
    
    ("Both delimiters with extra tokens", '''HAI extra
    WAZZUP
        I HAS A x
    BUHBYE
KTHXBYE more stuff'''),
    
    ("Valid delimiters", '''HAI
    WAZZUP
        I HAS A x
    BUHBYE
KTHXBYE'''),
]

print("="*70)
print("TESTING CODE DELIMITER VALIDATION")
print("="*70)

for test_name, code in test_cases:
    print(f"\nTest: {test_name}")
    print("-" * 70)
    
    tokens = tokenize(code)
    parser = SyntaxAnalyzer(tokens)
    parser.parse_program()
    
    if "Valid" in test_name:
        if not parser.error_messages:
            print(f"✓ PASS - No errors (valid syntax)")
        else:
            print(f"✗ FAIL - Unexpected error: {parser.error_messages[0]}")
    else:
        if parser.error_messages:
            print(f"✓ PASS - Error detected:")
            for error in parser.error_messages:
                print(f"    {error}")
        else:
            print(f"✗ FAIL - No error detected!")

print("\n" + "="*70)
