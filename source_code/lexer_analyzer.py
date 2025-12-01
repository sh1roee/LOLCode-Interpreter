'''
CMSC 124: LOLCODE Lexical Analyzer (Modified for Parser Integration)
- Sophia Ysabel Garcia
- James Andrei Tadeja
- Ron Russell Velasco
'''
import re, os

tokens = [
    # Code Delimiters
    (r'HAI\b', 'Code Delimiter'),
    (r'KTHXBYE\b', 'Code Delimiter'),
    
    # Comments 
    (r'BTW.*', 'Comment Line'),
    (r'OBTW\b', 'Comment Line'),
    (r'TLDR\b', 'Comment Line'),
    
    # Variable Declaration Section 
    (r'WAZZUP\b', 'Variable Declaration Section'),
    (r'BUHBYE\b', 'Variable Declaration Section'),
    # Variable Declaration and Assignment
    (r'I HAS A\b', 'Variable Declaration'),
    (r'ITZ\b', 'Variable Assignment'),
    (r'R\b', 'Variable Assignment'),
    
    # Arithmetic Operations 
    (r'SUM OF\b', 'Arithmetic Operation'),
    (r'DIFF OF\b', 'Arithmetic Operation'),
    (r'PRODUKT OF\b', 'Arithmetic Operation'),
    (r'QUOSHUNT OF\b', 'Arithmetic Operation'),
    (r'MOD OF\b', 'Arithmetic Operation'),
    (r'BIGGR OF\b', 'Arithmetic Operation'),
    (r'SMALLR OF\b', 'Arithmetic Operation'),
    
    # Boolean Operations
    (r'BOTH OF\b', 'Boolean Operation'),
    (r'EITHER OF\b', 'Boolean Operation'),
    (r'WON OF\b', 'Boolean Operation'),
    (r'NOT\b', 'Boolean Operation'),
    (r'ANY OF\b', 'Boolean Operation'),
    (r'ALL OF\b', 'Boolean Operation'),
    
    # Comparison Operations
    (r'BOTH SAEM\b', 'Comparison Operation'),
    (r'DIFFRINT\b', 'Comparison Operation'),
    
    # String Operations
    (r'SMOOSH\b', 'String Concatenation'),
    
    # Typecasting
    (r'IS NOW A\b', 'Typecasting Operation'),
    (r'MAEK\b', 'Typecasting Operation'),
    (r'A\b', 'Typecasting Operation'),
    
    # I/O Operations
    (r'VISIBLE\b', 'Output Keyword'),
    (r'!', 'Output Separator'),  # Newline suppression
    (r'\+', 'Output Separator'),
    (r'GIMMEH\b', 'Input Keyword'),
    
    # Conditionals 
    (r'O RLY\?', 'If-then Keyword'),
    (r'YA RLY\b', 'If-then Keyword'),
    (r'MEBBE\b', 'If-then Keyword'),
    (r'NO WAI\b', 'If-then Keyword'),
    (r'OIC\b', 'Exit Keyword'),
    
    # Switch-Case
    (r'WTF\?', 'Switch-Case Keyword'),
    (r'OMG\b', 'Switch-Case Keyword'),
    (r'OMGWTF\b', 'Switch-Case Keyword'),
    
    # Loops
    (r'IM IN YR\b', 'Loop Keyword'),
    (r'IM OUTTA YR\b', 'Loop Keyword'),
    (r'UPPIN\b', 'Loop Operation'),
    (r'NERFIN\b', 'Loop Operation'),
    (r'YR\b', 'Loop Variable Assignment'),
    (r'TIL\b', 'Loop Keyword'),
    (r'WILE\b', 'Loop Keyword'),
    
    # Functions
    (r'HOW IZ I\b', 'Function Keyword'),
    (r'IF U SAY SO\b', 'Function Keyword'),
    (r'FOUND YR\b', 'Return Keyword'),
    (r'GTFO\b', 'Return Keyword'),
    (r'I IZ\b', 'Function Call'),
    (r'MKAY\b', 'Function Call Delimiter'),
    
    # Literals - STRING MUST COME BEFORE OTHER PATTERNS
    (r'\"[^\"]*\"', 'YARN Literal'),  # Closed strings
    (r'-?[0-9]+\.[0-9]+', 'NUMBAR Literal'),
    (r'-?[0-9]+', 'NUMBR Literal'),
    (r'(WIN|FAIL)', 'TROOF Literal'),
    (r'(NUMBR|NUMBAR|YARN|TROOF|NOOB)', 'Type Literal'),
    
    # Parameter Delimiter
    (r'AN\b', 'Parameter Delimiter'),
    
    # Else, Identifiers
    (r'[a-zA-Z][a-zA-Z0-9_]*', 'Variable Identifier'),
]

# Token class to hold structured token data
class Token:
    def __init__(self, token_type, value, line_number):
        self.type = token_type
        self.value = value
        self.line_number = line_number
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line {self.line_number})"

# function to display output (for menu use)
def showOutput(tokens_found):
    if not tokens_found:
        print("No tokens found.")
        return
    
    # print header
    print("\n{:<30} {:<30} {:<10}".format("Token", "Category", "Line"))
    print("-" * 70)
    
    for token in tokens_found:
        if isinstance(token, Token):
            print("{:<30} {:<30} {:<10}".format(token.value, token.type, token.line_number))
        else:  # backward compatibility for tuple format
            print("{:<30} {:<30}".format(token[0], token[1]))
    
    print("-" * 70)
    print(f"Total tokens: {len(tokens_found)}\n")

# NEW: Core tokenize function that returns Token objects with line numbers
def tokenize(file_content):
    """
    Tokenizes LOLCODE content and returns a list of Token objects.
    
    Args:
        file_content: String containing LOLCODE source code
    
    Returns:
        List of Token objects, each with type, value, and line_number
    """
    if not file_content:
        return []
    
    tokens_found = []
    lines = file_content.split('\n')
    
    in_multiline_comment = False
    
    # process each line
    for line_num, line in enumerate(lines, 1):
        # skips empty lines
        if not line.strip():
            continue
        
        # handle multiline comments
        if in_multiline_comment:
            if 'TLDR' in line:
                in_multiline_comment = False
            continue
        
        # check if this line starts a multiline comment
        if re.match(r'^\s*OBTW\b', line):
            in_multiline_comment = True
            continue
        
        # check if this line is a single-line comment
        if re.match(r'^\s*BTW\b', line):
            continue
        
        position = 0
        
        while position < len(line):
            # skips spaces
            if line[position].isspace():
                position += 1
                continue
            
            matched = False
            
            # Special handling for string literals (both closed and unclosed)
            if line[position] == '"':
                closing_quote = line.find('"', position + 1)
                if closing_quote == -1:
                    # Unclosed string - mark entire rest of line as invalid
                    invalid_string = line[position:]
                    tokens_found.append(Token('INVALID TOKEN', invalid_string, line_num))
                    break  # Stop processing this line
                else:
                    # Properly closed string - strip the quotes
                    string_value = line[position+1:closing_quote]  # Remove quotes
                    tokens_found.append(Token('YARN Literal', string_value, line_num))
                    position = closing_quote + 1
                    matched = True
                    continue
            
            # check each token pattern
            for pattern, token_type in tokens:
                regex = re.compile(pattern)
                match = regex.match(line, position)
                
                if match:
                    lexeme = match.group(0)
                    
                    # skip comments
                    if token_type == 'Comment Line':
                        if lexeme.startswith('BTW'):
                            position = len(line)
                        else:
                            position = match.end()
                        matched = True
                        break
                    
                    # Skip YARN Literal pattern since we handle strings above
                    if token_type == 'YARN Literal':
                        continue
                    
                    # add valid token with line number
                    tokens_found.append(Token(token_type, lexeme, line_num))
                    position = match.end()
                    matched = True
                    break
            
            # handle invalid tokens
            if not matched:
                end_pos = position
                while end_pos < len(line) and not line[end_pos].isspace():
                    end_pos += 1
                
                invalid_lexeme = line[position:end_pos]
                tokens_found.append(Token('INVALID TOKEN', invalid_lexeme, line_num))
                position = end_pos
    
    return tokens_found

# function to tokenize content (wrapper for backward compatibility)
def tokenizer(content):
    """
    Processes content dictionary and displays tokenized results.
    Returns dictionary with filename as key and list of Token objects as value.
    """
    if not content:
        return None
    
    all_results = {}
    
    # process each file
    for filename, file_content in content.items():
        print(f"\n--- Tokenizing and Analyzing: {filename} ---")
        
        # use the new tokenize function
        tokens_found = tokenize(file_content)
        
        all_results[filename] = tokens_found
        showOutput(tokens_found)
    
    return all_results
        
def readFile():
    # get path from user
    path = input("Enter the LOLCODE file or directory path: ").strip()
    try:
        # check if path exists
        if not os.path.exists(path):
            print(f"Error: Path '{path}' does not exist.")
            return None
        
        # single file case
        if os.path.isfile(path):
            if not path.endswith(".lol"):
                print(f"Error: Invalid file type. Only .lol files are supported.")
                return None
            
            # read the file
            try:
                with open(path, "r", encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(path)
                return {filename: content}
            
            except Exception as e:
                print(f"Error reading file '{path}': {e}")
                return None
        
        # directory case
        elif os.path.isdir(path):
            files_content = {}
            lol_files = [f for f in os.listdir(path) if f.endswith(".lol")]
            
            if not lol_files:
                print(f"Warning: No .lol files found in directory '{path}'.")
                return None
            
            for filename in lol_files:
                filepath = os.path.join(path, filename)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        files_content[filename] = f.read()
                
                except Exception as e:
                    print(f"Error reading file '{filename}': {e}. Skipping.")
                    continue
            
            if not files_content:
                print(f"Error: Failed to read any files from directory '{path}'.")
                return None
            
            print(f"Successfully read {len(files_content)} file(s) from directory.")
            return files_content
        
        else:
            print(f"Error: '{path}' is neither a file nor a directory.")
            return None
    
    except Exception as e:
        print(f"Unexpected error when processing '{path}': {e}")
        return None

# menu function
def menu():
    print("-----------------------------------")
    print("LOLCODE Lexical Analyzer")
    print("-----------------------------------")
    print("[1] Read and Analyze LOLCODE File/Directory")
    print("[2] Type LOLCODE String to Analyze")
    print("[3] Exit\n")

# main function
def main():
    while True:
        menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            content = readFile()
            if content:
                tokenizer(content)
            else:
                print("No content to analyze.")
        elif choice == '2':
            input_string = input("Enter LOLCODE string to analyze: ").replace("\\n", "\n")
            if input_string.strip():
                content = {"Input String": input_string}
                tokenizer(content)
            else:
                print("No input string provided.")
        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")            

if __name__ == "__main__":
    main()