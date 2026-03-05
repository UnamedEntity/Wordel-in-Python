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
        self.root.title("Wordel")
        # let the window size itself to content and prevent resizing
        self.root.resizable(False, False)
        # store game state
        self.current_row = current_row
        self.score = score

        # load the master dictionary of all 5-letter words from every CSV
        self.full_words = self.load_all_words()

        # pick a target word and also keep the list for that initial letter
        self.target_word, self.words = self.generate_target_word()

        # build the interface
        self.setup_ui()

    # only let user input one letter per box and only allow letters, not numbers or symbols
    def validate_letter(self, proposed):
        if proposed == "":
            return True
        if len(proposed) > 1:
            return False
        return proposed.isalpha()

    def setup_ui(self):
        # Create a main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))

        # Create a label for the title
        title_label = ttk.Label(main_frame, text="Wordel", font=("Arial", 24))
        title_label.grid(row=0, column=0, columnspan=5, pady=(0, 20))

        # Create a grid of entry fields for the wordle game
        self.entries = []
        # restrict input to one letter pass %P as the argument for the function validate letter
        vcmd = (self.root.register(self.validate_letter), '%P')
        for i in range(6):
            row_entries = []
            for j in range(5):
                # create entries that support readonly background and validate input
                entry = Entry(
                    main_frame,
                    width=3,
                    readonlybackground='white',
                    validate='key',
                    validatecommand=vcmd
                )
                entry.grid(row=i+1, column=j, padx=1, pady=1)
                row_entries.append(entry)
            self.entries.append(row_entries)

        #Score label 
        self.score_label = ttk.Label(main_frame, text="Score: " + str(self.score), font=("Arial", 12))
        self.score_label.grid(row=9, column=0, columnspan=5, pady=(5, 0))

        # Reset button to start a new game
        reset_button = ttk.Button(main_frame, text="Reset Game", command=self.reset_game)
        reset_button.grid(row=10, column=0, columnspan=5, pady=(10, 0))

        # Create a button to submit the guess.
        submit_button = ttk.Button(main_frame, text="Submit Guess", command=self.submit_guess)
        submit_button.grid(row=7, column=0, columnspan=5, pady=(20, 0))

        # Label for status messages (warnings, success, invalid word, etc.)
        self.status_label = ttk.Label(main_frame, text="", font=("Arial", 12))
        self.status_label.grid(row=8, column=0, columnspan=5, pady=(5, 0))

        # set focus to first cell at the start of the game
        self.entries[0][0].focus_set()

    def reset_game(self):
        # Reset the game state and clear the interface for a new game.
        self.current_row = 0
        self.target_word, self.words = self.generate_target_word()
        self.score = 0

        # Update the score label and clear the status label.
        self.score_label.config(text=f"Score: {self.score}")
        # clear the status label if it exists
        if hasattr(self, 'status_label'):
            self.status_label.config(text="")

        for row in self.entries:
            # reset each entry to normal state, clear the text, and set background to white
            for entry in row:
                entry.config(state='normal', background='white', readonlybackground='white')
                entry.delete(0, END)
        #set cursor to first cell of the first row
        self.entries[0][0].focus_set()

    def submit_guess(self):
        # Collect the guess from entry field and test it against the target word.
        letters = [entry.get().strip() for entry in self.entries[self.current_row]]

        # check if each box has exactly one character
        if any(len(l) != 1 for l in letters):
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
            self.status_label.config(text="You've guessed the word!")
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            color = 'green'
            self.reset_game()
        else:
            # Update the background color based on the guess.
            for i in range(len(self.target_word)):
                # choose a color
                if guess[i] == self.target_word[i]:
                    color = 'green'
                elif guess[i] in self.target_word:
                    color = 'yellow'
                else:
                    color = 'red'
                # set both normal and readonly backgrounds 
                self.entries[self.current_row][i].config(background=color, readonlybackground=color)
            # make the row read-only to prevent editing 
            for entry in self.entries[self.current_row]:
                entry.config(state='readonly')
            self.current_row += 1
            if self.current_row >= 6:
                # print the answer and end the game if the user has used all their guesses
                self.status_label.config(text=f"The word was: {self.target_word}")
            else:
                # set cursor to next row's first cell
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

        