from lexer_analyzer import tokenize

# Test case 1: PRODUCKT (misspelled)
code1 = 'VISIBLE "Tip: " PRODUCKT OF input AN 0.1'
tokens1 = tokenize(code1)
print("Test 1: PRODUCKT (misspelled)")
for t in tokens1:
    print(f"  {t.type}: {t.value}")

print()

# Test 2: TITE (undefined identifier)
code2 = 'VISIBLE DIFF OF 2022 AN input TITE'
tokens2 = tokenize(code2)
print("Test 2: TITE (undefined identifier)")
for t in tokens2:
    print(f"  {t.type}: {t.value}")
