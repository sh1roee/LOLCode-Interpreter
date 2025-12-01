import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from lexer_analyzer import tokenize
from syntax_analyzer import SyntaxAnalyzer

# color scheme
BG = "#0B1220"
PANEL = "#172232"
INNER = "#0F1A26"
ACCENT_PURPLE = "#9B63FF"
CLEAR_RED = "#880808"
TEXT = "#D6E6FF"

ctk.set_appearance_mode("dark") # modes : "dark", "light"

# main gui class
class LOLCodeInterpreterGUI:  
    def __init__(self): # default 
        self.root = ctk.CTk()
        self.root.title("LOCODE Interpreter")
        self.root.configure(fg_color=BG)
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        self.current_file = None
        self.waiting_for_input = False
        self.input_prompt_start = None  # Track where input prompt starts
        self.input_value = None
        self.create_gui()
        self._configure_grid_weights()  # enable full resizing

    # create gui layout
    def create_gui(self):
        # title
        title = ctk.CTkLabel(self.root, text="LOLCODE Interpreter",
                             font=("Arial", 22, "bold"), text_color=ACCENT_PURPLE)
        title.pack(pady=(12, 6))
        
        # Create main paned window for vertical split
        self.main_paned = tk.PanedWindow(self.root, orient=tk.VERTICAL, bg=BG, 
                                        sashwidth=6, sashrelief=tk.RAISED, 
                                        sashpad=2, bd=0)
        self.main_paned.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        
        # Top frame for editor and analysis panels
        self.top_frame = ctk.CTkFrame(self.main_paned, fg_color=BG, corner_radius=0)
        
        # Bottom frame for console (resizable)
        self.console_container = ctk.CTkFrame(self.main_paned, fg_color=PANEL, corner_radius=14)
        
        # Add frames to paned window
        self.main_paned.add(self.top_frame, minsize=300)
        self.main_paned.add(self.console_container, minsize=100)
        
        # Configure the paned window to give more space to top initially
        self.root.after(100, lambda: self.main_paned.sash_place(0, 0, 500))
        
        self._create_top_panels()
        self._create_console_panel()

    def _create_top_panels(self):
        """Create the top section with editor, lexemes, and symbol table"""
        # Use grid layout for the top frame
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=5)
        self.top_frame.grid_columnconfigure(1, weight=3)
        self.top_frame.grid_columnconfigure(2, weight=3)

        # left editor panel
        left_panel = ctk.CTkFrame(self.top_frame, fg_color=PANEL, corner_radius=16)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)

        file_row = ctk.CTkFrame(left_panel, fg_color=PANEL)
        file_row.pack(fill="x", padx=12, pady=(10, 6))

        self.filename_label = ctk.CTkLabel(file_row, text="(None)", font=("Arial", 12, "bold"), text_color=TEXT)
        self.filename_label.pack(side="left")

        browse_btn = ctk.CTkButton(file_row, text="📁", width=36, height=28, fg_color="#2A3350", 
                                   hover=False, command=self.browse_file)
        browse_btn.pack(side="right")

        # text editor frame
        editor_frame = ctk.CTkFrame(left_panel, fg_color=INNER, corner_radius=12)
        editor_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # text editor label
        editor_label_frame = ctk.CTkFrame(editor_frame, fg_color=INNER)
        editor_label_frame.pack(fill="x", padx=6, pady=(8, 4))
        ctk.CTkLabel(editor_label_frame, text="Text Editor", font=("Arial", 13, "bold"),
                     text_color=TEXT).pack(side="left", anchor="w")

        # line numbers + text editor container
        editor_container = ctk.CTkFrame(editor_frame, fg_color=INNER)
        editor_container.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # line numbers gutter
        gutter_bg = "#08121a"
        self.line_numbers = tk.Text(editor_container, width=4, padx=4, pady=8, takefocus=0,
                                    border=0, background=gutter_bg, foreground="#6B7B8C",
                                    font=("Courier New", 12), state="disabled", cursor="arrow",
                                    spacing1=0, spacing2=0, spacing3=0)
        self.line_numbers.pack(side="left", fill="y")

        # text editor textbox
        self.text_editor = ctk.CTkTextbox(editor_container, wrap="none", font=("Courier New", 12),
                                          fg_color="#091218", text_color=TEXT)
        self.text_editor.pack(side="left", fill="both", expand=True)

        # bind events to sync scrolling and update line numbers
        self.text_editor.bind("<KeyRelease>", lambda e: self.update_line_numbers())
        self.text_editor.bind("<ButtonRelease-1>", lambda e: self.update_line_numbers())
        self.text_editor.bind("<MouseWheel>", lambda e: self.sync_scroll())

        # mid lexemes panel
        lex_panel = ctk.CTkFrame(self.top_frame, fg_color=PANEL, corner_radius=16)
        lex_panel.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        lex_title_row = ctk.CTkFrame(lex_panel, fg_color=PANEL)
        lex_title_row.pack(fill="x", padx=12, pady=(10, 6))
        ctk.CTkLabel(lex_title_row, text="LEXEMES", font=("Arial", 14, "bold"),
                     text_color=TEXT).pack(side="left")

        lex_inner = ctk.CTkFrame(lex_panel, fg_color=INNER, corner_radius=12)
        lex_inner.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        headers = ctk.CTkFrame(lex_inner, fg_color=INNER)
        headers.pack(fill="x", padx=8, pady=(6, 4))
        ctk.CTkLabel(headers, text="Lexeme", font=("Arial", 11, "bold"),
                     text_color=TEXT).pack(side="left", padx=(4, 12))
        ctk.CTkLabel(headers, text="Classification", font=("Arial", 11, "bold"),
                     text_color=TEXT).pack(side="left")

        self.lexemes_textbox = ctk.CTkTextbox(lex_inner, font=("Courier New", 10),
                                              fg_color="#091218", text_color=TEXT)
        self.lexemes_textbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # right symbol table panel
        sym_panel = ctk.CTkFrame(self.top_frame, fg_color=PANEL, corner_radius=16)
        sym_panel.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=8)

        sym_title_row = ctk.CTkFrame(sym_panel, fg_color=PANEL)
        sym_title_row.pack(fill="x", padx=12, pady=(10, 6))
        ctk.CTkLabel(sym_title_row, text="SYMBOL TABLE", font=("Arial", 14, "bold"),
                     text_color=TEXT).pack(side="left")

        sym_inner = ctk.CTkFrame(sym_panel, fg_color=INNER, corner_radius=12)
        sym_inner.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        sym_headers = ctk.CTkFrame(sym_inner, fg_color=INNER)
        sym_headers.pack(fill="x", padx=8, pady=(6, 4))
        ctk.CTkLabel(sym_headers, text="Identifier", font=("Arial", 11, "bold"),
                     text_color=TEXT).pack(side="left", padx=(4, 12))
        ctk.CTkLabel(sym_headers, text="Value", font=("Arial", 11, "bold"),
                     text_color=TEXT).pack(side="left")

        self.symbol_textbox = ctk.CTkTextbox(sym_inner, font=("Courier New", 10),
                                             fg_color="#091218", text_color=TEXT)
        self.symbol_textbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # controls row
        controls_frame = ctk.CTkFrame(self.top_frame, fg_color=BG, corner_radius=0)
        controls_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=0, pady=(0, 6))

        ctk.CTkButton(controls_frame, text="🗑️ Clear", width=110, fg_color=CLEAR_RED,
                      hover_color="#9E5B4B", command=self.clear_all).pack(side="left", padx=(2, 6))
        ctk.CTkButton(controls_frame, text="Execute", width=140, fg_color=ACCENT_PURPLE,
                      hover_color=ACCENT_PURPLE, command=self.execute_code).pack(side="right", padx=(6, 2))

    def _create_console_panel(self):
        """Create the resizable console panel"""
        # console output area (now editable for input)
        self.console_textbox = ctk.CTkTextbox(self.console_container, wrap="word",
                                              font=("Courier New", 12), fg_color=INNER, text_color=TEXT)
        self.console_textbox.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Bind Enter key for input handling
        self.console_textbox.bind("<Return>", self._handle_console_input)
        self.console_textbox.bind("<Key>", self._handle_console_key)

    # configure grid weights for resizing
    def _configure_grid_weights(self):
        # Since we're using pack layout now, this method is simplified
        pass

    # file browsing function
    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select LOL Code File",
                                              filetypes=(("LOL files", "*.lol"), ("Text files", "*.txt"),
                                                         ("All files", "*.*")))
        if filename:
            self.current_file = filename
            self.filename_label.configure(text=os.path.basename(filename))
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", content)
                self.update_line_numbers()
                
                # Clear symbol table and lexemes when new file is loaded
                self.symbol_textbox.delete("1.0", "end")
                self.lexemes_textbox.delete("1.0", "end")
                
                self.log_to_console(f"File loaded: {os.path.basename(filename)}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    # execute code function
    def execute_code(self):
        self.console_textbox.delete("1.0", "end")
        code = self.text_editor.get("1.0", "end-1c")
        if not code.strip():
            messagebox.showwarning("Warning", "No code to execute!")
            return

        self.log_to_console("Running Lexical Analysis...\n")
        try:
            tokens = tokenize(code)
            self.display_lexemes(tokens)
            self.log_to_console(f"Found {len(tokens)} tokens\n\n")
        except Exception as e:
            self.log_to_console(f"Lexer error: {e}\n")
            return

        self.log_to_console("Running Syntax Analysis & Execution...\n")
        try:
            parser_obj = SyntaxAnalyzer(tokens, log_function=self.log_to_console, input_function=self.request_input)
            symbol_table = parser_obj.parse_program()

            self.display_symbol_table(symbol_table)
        except Exception as e:
            self.log_to_console(f"\nSyntax/Runtime error: {e}\n")

    # display lexemes in textbox
    def display_lexemes(self, tokens):
        self.lexemes_textbox.delete("1.0", "end")
        for token in tokens:
            self.lexemes_textbox.insert("end", f"{token.value:<25} {token.type}\n")

    # display symbol table in textbox
    def display_symbol_table(self, variables):
        self.symbol_textbox.delete("1.0", "end")
        if not variables:
            return
        for identifier, info in variables.items():
            val = info.get("value", "NOOB")
            t = info.get("type", "")
            self.symbol_textbox.insert("end", f"{identifier:<18} {val} ({t})\n")

    # display console output
    def display_console(self, text):
        self.console_textbox.delete("1.0", "end")
        self.console_textbox.insert("1.0", text)

    # log messages to console
    def log_to_console(self, msg):
        self.console_textbox.insert("end", msg)
        self.console_textbox.see("end")
        self.root.update_idletasks()

    # request input from user via console
    def request_input(self, prompt):
        """
        Request input from user directly in console
        Returns the input value when user presses Enter
        """
        self.log_to_console(prompt)
        self.input_prompt_start = self.console_textbox.index("end-1c")
        self.waiting_for_input = True
        self.input_value = None
        
        # Focus on console and position cursor at end
        self.console_textbox.focus()
        self.console_textbox.mark_set("insert", "end")
        
        # Wait for input to be submitted
        while self.waiting_for_input:
            self.root.update()
            self.root.after(10)  # Small delay to prevent high CPU usage
        
        return self.input_value

    # handle console input when Enter is pressed
    def _handle_console_input(self, event):
        if self.waiting_for_input:
            # Get the current line content after the prompt
            current_pos = self.console_textbox.index("insert")
            
            # Find where user input starts (after the prompt)
            if self.input_prompt_start:
                # Get text from prompt end to current cursor position
                input_text = self.console_textbox.get(self.input_prompt_start, current_pos)
            else:
                # Fallback: get current line
                line_start = self.console_textbox.index("insert linestart")
                input_text = self.console_textbox.get(line_start, current_pos)
            
            # Clean the input text
            self.input_value = input_text.strip()
            self.waiting_for_input = False
            
            # Add newline and prevent default Enter behavior
            self.console_textbox.insert("insert", "\n")
            return "break"  # Prevent default Enter handling
        
        return None

    # handle key presses in console
    def _handle_console_key(self, event):
        if self.waiting_for_input:
            # Allow normal typing when waiting for input
            return None
        else:
            # When not waiting for input, make console read-only except for scrolling
            if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Prior', 'Next', 'Home', 'End']:
                return None  # Allow navigation
            else:
                return "break"  # Block other keys when not in input mode

    # clear all fields
    def clear_all(self):
        self.text_editor.delete("1.0", "end")
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.configure(state="disabled")
        self.lexemes_textbox.delete("1.0", "end")
        self.symbol_textbox.delete("1.0", "end")
        self.console_textbox.delete("1.0", "end")
        self.filename_label.configure(text="(None)")
        self.current_file = None
        self.log_to_console("✓ All fields cleared\n")

    # update line numbers to match editor content
    def update_line_numbers(self):
        try:
            content = self.text_editor.get("1.0", "end-1c")
            line_count = content.count('\n') + 1 if content else 1
            line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
            
            self.line_numbers.configure(state="normal")
            self.line_numbers.delete("1.0", "end")
            self.line_numbers.insert("1.0", line_numbers_string)
            self.line_numbers.configure(state="disabled")
        except Exception:
            pass

    # sync scroll position between line numbers and editor
    def sync_scroll(self):
        try:
            # get the editor's first visible line
            self.line_numbers.yview_moveto(self.text_editor.yview()[0])
        except Exception:
            pass

    # run main loop
    def run(self):
        self.root.mainloop()

# entry point
if __name__ == "__main__":
    app = LOLCodeInterpreterGUI()
    app.run()
