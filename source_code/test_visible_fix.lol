HAI
	WAZZUP
		I HAS A choice
		I HAS A input
		I HAS A validVar ITZ "I am valid"
	BUHBYE
	
	BTW Test 1: Valid quoted string - should work
	VISIBLE "Test 1: Valid quoted string"
	VISIBLE "TITE"
	VISIBLE ""
	
	BTW Test 2: Valid variable - should work
	VISIBLE "Test 2: Valid variable"
	VISIBLE validVar
	VISIBLE ""
	
	BTW Test 3: Valid arithmetic operation - should work
	input R 2000
	VISIBLE "Test 3: Valid arithmetic"
	VISIBLE DIFF OF 2022 AN input
	VISIBLE ""
	
	BTW Test 4: Undefined variable in VISIBLE - should ERROR
	VISIBLE "Test 4: Undefined variable (should error)"
	VISIBLE DIFF OF 2022 AN input TITE
	
KTHXBYE
