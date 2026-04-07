# Christian Edwards
# A simple Wordle game implemented in Python using Tkinter Library for the GUI.
# Date: 2026-03-23


from tkinter import *
from tkinter import ttk
import random
import csv
import os

# Create the main application window class with helper functions to manage the GUI.
class WordelApp:
    def __init__(self, root, current_row, score=0):
        # Initialize the main application window and set up the user interface.
        self.root = root
        self.root.title("Wordle")
        # let the window size itself to content and prevent resizing
        self.root.resizable(False, False)
        # store game state
        self.current_row = current_row
        self.score = score
        #timer 
        self.seconds = 0
        self.timer_job = None

        # load the master dictionary of all 5-letter words from every CSV
        self.full_words = self.load_all_words()

        # pick a target word and also keep the list for that initial letter
        self.target_word, self.words = self.generate_target_word()

        # build the interface
        self.setup_ui()

    def update_timer(self):
        minutes = self.seconds // 60
        secs = self.seconds % 60
        self.timer.config(text=f"Timer: {minutes:02d}:{secs:02d}")

        self.seconds += 1
        self.timer_job = self.root.after(1000, self.update_timer)

    def validate_letter(self, proposed):
        if proposed == "":
            return True
        if len(proposed) > 1:
            return False
        # Convert to uppercase for better display
        if proposed.isalpha():
            # Schedule the conversion after validation
            self.root.after(1, lambda: self.convert_to_uppercase())
            return True
        return False

    def convert_to_uppercase(self):
        #Convert the current entry's text to uppercase
        try:
            current_focus = self.root.focus_get()
            if isinstance(current_focus, Entry):
                current_text = current_focus.get()
                if current_text and current_text.isalpha():
                    current_focus.delete(0, END)
                    current_focus.insert(0, current_text.upper())
        except:
            pass  # Ignore if focus is not on an entry

    def setup_ui(self):
        # Create a main frame with better styling
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))

        # Create a label for the title with better styling
        title_label = ttk.Label(main_frame, text="Wordle", font=("Helvetica", 36, "bold"), foreground="#2E3440")
        title_label.grid(row=0, column=0, columnspan=5, pady=(0, 30))

        # Create a grid of entry fields for the wordle game with improved styling
        self.entries = []
        # restrict input to one letter pass %P as the argument for the function validate letter
        vcmd = (self.root.register(self.validate_letter), '%P')
        for i in range(6):
            row_entries = []
            for j in range(5):
                # create entries with enhanced styling
                entry = Entry(
                    main_frame,
                    width=4,
                    font=("Helvetica", 24, "bold"),
                    justify='center',
                    relief='solid',
                    borderwidth=2,
                    readonlybackground='#FFFFFF',
                    background='#FFFFFF',
                    highlightbackground='#D3D3D3',
                    highlightcolor='#4A90E2',
                    highlightthickness=1,
                    validate='key',
                    validatecommand=vcmd
                )
                entry.grid(row=i+1, column=j, padx=3, pady=3, ipadx=5, ipady=5)
                row_entries.append(entry)
            self.entries.append(row_entries)

        # Make all rows after the current row readonly initially
        for i in range(self.current_row + 1, 6):
            for entry in self.entries[i]:
                entry.config(state='readonly')

        # Score label with better styling
        self.score_label = ttk.Label(main_frame, text="Score: " + str(self.score), font=("Helvetica", 16), foreground="#2E3440")
        self.score_label.grid(row=10, column=0, columnspan=5, pady=(20, 0))

        # Reset button 
        reset_button = ttk.Button(main_frame, text="Play Again", command=self.reset_game, style="Accent.TButton")
        reset_button.grid(row=9, column=0, columnspan=5, pady=(15, 0))

        # Timer with better 
        self.timer = ttk.Label(main_frame, text="Timer: 00:00", font=("Helvetica", 16), foreground="#2E3440")
        self.timer.grid(row=11, column=0, columnspan=5, pady=(10, 0))

        # increment timer every second using after method, and format the time as minutes and seconds
        self.update_timer()

        # Submit button 
        submit_button = ttk.Button(main_frame, text="Submit Guess", command=self.submit_guess, style="Accent.TButton")
        submit_button.grid(row=7, column=0, columnspan=5, pady=(15, 0))

        # status messagesg
        self.status_label = ttk.Label(main_frame, text="", font=("Helvetica", 14), foreground="#E74C3C")
        self.status_label.grid(row=8, column=0, columnspan=5, pady=(5, 0))

        # Configure button style
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Helvetica", 12, "bold"), padding=6)

        # Set window background color
        self.root.configure(bg='#F8F9FA')

        # Bind Enter key to submit guess
        self.root.bind('<Return>', lambda e: self.submit_guess())
        
        # Bind arrow keys and backspace for navigation
        self.root.bind('<Left>', lambda e: self.move_cursor(-1, 0))
        self.root.bind('<Right>', lambda e: self.move_cursor(1, 0))
        self.root.bind('<Up>', lambda e: self.move_cursor(0, -1))
        self.root.bind('<Down>', lambda e: self.move_cursor(0, 1))
        self.root.bind('<BackSpace>', lambda e: self.handle_backspace())

        # set focus to first cell at the start of the game
        self.entries[0][0].focus_set()

    def move_cursor(self, dx, dy):
        # move between cells using arrow keys, but only if the next cell is not readonly
        try:
            current_focus = self.root.focus_get()
            if isinstance(current_focus, Entry):
                for row_idx, row in enumerate(self.entries):
                    for col_idx, entry in enumerate(row):
                        if entry == current_focus:
                            new_row = row_idx + dy
                            new_col = col_idx + dx
                            if 0 <= new_row < len(self.entries) and 0 <= new_col < len(row):
                                if self.entries[new_row][new_col]['state'] != 'readonly':
                                    self.entries[new_row][new_col].focus_set()
                            return
        except:
            pass

    def handle_backspace(self):
        # handle backspace key for clearing current cell and moving left
        try:
            current_focus = self.root.focus_get()
            if isinstance(current_focus, Entry):
                current_text = current_focus.get()
                if current_text:  # If there's text, clear it
                    current_focus.delete(0, END)
                else:  # If empty, move to previous cell
                    self.move_cursor(-1, 0)
        except:
            pass

    def reset_game(self):
        # stop previous timer loop
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)

        self.current_row = 0
        self.target_word, self.words = self.generate_target_word()
        self.score = 0

        self.score_label.config(text=f"Score: {self.score}")

        # Reset all entry colors and states
        for row in self.entries:
            for entry in row:
                entry.config(
                    background='#FFFFFF',
                    readonlybackground='#FFFFFF',
                    state='normal',
                    highlightthickness=1
                )
                entry.delete(0, END)  # Clear the text

        # Make all rows after the first one readonly again
        for i in range(1, 6):
            for entry in self.entries[i]:
                entry.config(state='readonly')

        # reset timer 
        self.seconds = 0
        self.timer.config(text="Timer: 00:00")
        self.update_timer()

        # Clear status message
        self.status_label.config(text="", foreground="#E74C3C")

        # Set focus to first cell
        self.entries[0][0].focus_set()

    def submit_guess(self):
        # Collect the guess from entry field and test it against the target word.
        letters = [entry.get().strip() for entry in self.entries[self.current_row]]

        # check if each box has exactly one character and is not empty
        if any(len(l) != 1 or l == '' for l in letters):
            self.status_label.config(text="Please type one letter in each box.")
            return
        
        # formats guess by turning array input into a string 
        guess = ''.join(l.lower() for l in letters)

        # clear 
        self.status_label.config(text="")

        # checks against full dictionary instead of only the letter-specific list
        if guess not in self.full_words:
            self.status_label.config(text="Not a valid word. Try again.")

        elif guess == self.target_word:
            #increase score and update status and score labels
            self.status_label.config(text="You've guessed the word!", foreground="#27AE60")
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            # Animate the winning row with a delay
            self.animate_row_colors(self.current_row, guess, is_win=True)
            self.root.after(1500, self.reset_game)  # Delay reset to show the win
            if self.timer_job:
                self.root.after_cancel(self.timer_job)
        else:
            # Update the background color based on the guess with animation
            self.animate_row_colors(self.current_row, guess, is_win=False)
            # make the row read-only to prevent editing 
            for entry in self.entries[self.current_row]:
                entry.config(state='readonly')
            self.current_row += 1
            if self.current_row >= 6:
                # print the answer and end the game if the user has used all their guesses
                self.status_label.config(text=f"The word was: {self.target_word}", foreground="#E74C3C")
                if self.timer_job:
                    self.root.after_cancel(self.timer_job)
            else:
                # set cursor to next row's first cell
                self.entries[self.current_row][0].focus_set()

    def animate_row_colors(self, row, guess, is_win=False):
        """Animate the color reveal for a row of letters"""
        colors = []
        for i in range(len(self.target_word)):
            if guess[i] == self.target_word[i]:
                colors.append('#27AE60')  # green for correct position
            elif guess[i] in self.target_word:
                colors.append('#F39C12')  # orange for correct letter wrong position
            else:
                colors.append('#BDC3C7')  # gray for incorrect letter
        
        # animate each letter with a delay
        for i, color in enumerate(colors):
            self.root.after(i * 200, lambda idx=i, col=color: self.reveal_letter(row, idx, col))
        
        # make row readonly after animation completes
        self.root.after(len(colors) * 200 + 100, lambda: self.make_row_readonly(row, is_win))

    def reveal_letter(self, row, col, color):
        # Reveal a single letter with color and animation effect
        entry = self.entries[row][col]
        entry.config(highlightthickness=3, highlightcolor=color)
        self.root.after(100, lambda: entry.config(
            background=color, 
            readonlybackground=color,
            highlightthickness=1,
            highlightcolor='#4A90E2'
        ))

    def make_row_readonly(self, row, is_win):
        # Make a row readonly after animation
        for entry in self.entries[row]:
            entry.config(state='readonly')
        
        if not is_win:
            self.current_row += 1
            if self.current_row >= 6:
                # Game over - show the answer
                self.status_label.config(text=f"The word was: {self.target_word}", foreground="#E74C3C")
                if self.timer_job:
                    self.root.after_cancel(self.timer_job)
            else:
                # Enable the next row for editing
                for entry in self.entries[self.current_row]:
                    entry.config(state='normal')
                # Move to next row
                self.entries[self.current_row][0].focus_set()
    # dose not need class as an argument
    @staticmethod
    def _get_csv_dir():
        # Return the directory path that contains the word list CSV files.
        # The word lists directory can sit next to this script or one level up.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            # look for a folder named exactly as it appears in the repository
            os.path.normpath(os.path.join(base_dir, 'Word lists in csv')),
        ]
        for c in candidates:
            if os.path.isdir(c):
                return c
    
    # autmotically has class as an argument so i can save the list of 5 letter words inside the class to use accross all methods
    def load_words_for_letter(self, letter):
        # Return all normalized 5-letter words from the CSV for the given initial letter.
        csv_dir = self._get_csv_dir()
        csv_path = os.path.join(csv_dir, f"{letter.upper()}word.csv")
        words = []
        if os.path.isfile(csv_path):
            with open(csv_path, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    w = row[0].strip().lower()
                    if len(w) == 5:
                        words.append(w)
        return words
    # loads all the words from letters A-Z, neededs to be class method since it call load words for letter method
    def load_all_words(self):
        #Aggregate 5-letter words from all letter files into one list.
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        all_words = []
        for ch in alphabet:
            all_words.extend(self.load_words_for_letter(ch))
        return all_words
    # uses the two previous methods to get a random letter and then a random word
    def generate_target_word(self):
        #Choose a random target word from one randomly selected letter bucket.
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        letter = random.choice(alphabet)
        words = self.load_words_for_letter(letter)
        return random.choice(words), words


# Create the main application window and start the application.
if __name__ == "__main__":
    root = Tk()
    current_row = 0 
    score = 0
    app = WordelApp(root, current_row, score)
    root.mainloop()

        