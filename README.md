# LOLCODE Interpreter

## Overview

A LOLCODE interpreter featuring a GUI built with CustomTkinter. This interpreter handles lexical analysis, syntax parsing, semantic analysis, and program execution—all within an intuitive interface.


## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher - [Download Python](https://www.python.org/downloads/)
- pip - Python package installer (comes with Python)

## Installation

### Step 1: Clone or Download the Repository

### Step 2: Install Required Dependencies

The project requires the following Python packages:

| Package | Version | Purpose |
|---------|---------|---------|
| `customtkinter` | Latest | Modern GUI framework |
| `tkinter` | Built-in | Standard GUI toolkit (comes with Python) |

Install CustomTkinter using pip:

```bash
pip install customtkinter
```

### Step 3: Verify Installation

Check that all dependencies are installed:

```bash
python -c "import customtkinter; import tkinter; print('✓ All dependencies installed successfully!')"
```

## Running the Project

### Quick Start

Navigate to the `LOLCODE_project` directory and run the main file:

```bash
cd LOLCODE_project
python main.py
```

### What to Expect

When you launch the application, you'll see:

1. Text Editor (Left Panel) - Write or paste LOLCODE programs
2. Lexemes Table (Center Panel) - Displays tokens after execution
3. Symbol Table (Right Panel) - Shows variables and their values
4. Console (Bottom Panel) - Program output and user input

## Project Structure

```
124proj/
├── LOLCODE_project/
│   ├── gui.py                    # Main GUI implementation
│   ├── main.py                   # Application entry point
│   ├── lexer_analyzer.py         # Tokenization and lexical analysis
│   ├── syntax_analyzer.py        # Parsing and syntax validation
│   ├── semantics_analyzer.py     # Semantic analysis and execution
│   ├── typecaster.py             # Type conversion utilities
│   └── project-testcases/        # Sample LOLCODE programs
└── README.md                     # This file
```

### Component Overview

| File | Description |
|------|-------------|
| `gui.py` | Modern GUI with resizable panels, code editor, and console |
| `lexer_analyzer.py` | Breaks source code into tokens |
| `syntax_analyzer.py` | Validates program structure and executes code |
| `semantics_analyzer.py` | Handles variable operations and type checking |
| `typecaster.py` | Manages type conversions (NUMBR, NUMBAR, YARN, etc.) |

## Usage Guide

### Loading a LOLCODE File

1. Click the Browse button in the top-left
2. Select a `.lol` file from your system
3. The code will appear in the text editor

### Writing LOLCODE

You can directly type or paste LOLCODE programs in the text editor. Example:

```lolcode
HAI 1.2
    VISIBLE "Hello, World!"
KTHXBYE
```

### Executing Code

1. Write or load your LOLCODE program
2. Click the Execute button (purple button, bottom-right)
3. View results:
   - Lexemes panel shows all tokens
   - Symbol Table displays variables
   - Console shows program output

### Interactive Input

When a program requires input (using `GIMMEH`), the console will:
1. Display the input prompt
2. Allow you to type your response
3. Press Enter to submit

### Clearing Everything

Click the Clear bu tton (red button, bottom-left) to reset all panels.

## About LOLCODE

LOLCODE is an esoteric programming language inspired by lolcat memes. This interpreter supports:

- Variable declarations (`I HAS A`)
- Input/Output (`GIMMEH`, `VISIBLE`)
- Arithmetic operations (`SUM OF`, `DIFF OF`, etc.)
- Conditionals (`O RLY?`, `YA RLY`, `NO WAI`)
- Loops (`IM IN YR`, `IM OUTTA YR`)
- Functions (`HOW IZ I`, `I IZ`, `FOUND YR`)
- Type casting (`MAEK`, `IS NOW A`)

