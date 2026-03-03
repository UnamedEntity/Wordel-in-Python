from tkinter import *
from tkinter import ttk
import random
import csv
import os

# Create the main application window class with helper functions to manage the GUI.
class WordelApp:
    def __init__(self, root, current_row, target_word,score):
        # Initialize the main application window and set up the user interface.
        self.root = root
        self.root.title("Wordel")
        # let the window size itself to content and prevent resizing
        self.root.resizable(False, False)
        # store game state
        self.current_row = current_row
        self.target_word = target_word
        self.score = score

        # build the interface
        self.setup_ui()

    def setup_ui(self):
        # Create a main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))

        # Create a label for the title
        title_label = ttk.Label(main_frame, text="Wordel", font=("Arial", 24))
        title_label.grid(row=0, column=0, columnspan=5, pady=(0, 20))

        # Create a grid of entry fields for the wordle game
        self.entries = []
        for i in range(6):
            row_entries = []
            for j in range(5):
                # create entries that support readonly background
                entry = Entry(main_frame, width=3, readonlybackground='white')
                entry.grid(row=i+1, column=j, padx=1, pady=1)
                row_entries.append(entry)
            self.entries.append(row_entries)

        # Status label for feedback
        self.status_label = ttk.Label(main_frame, text="", font=("Arial", 12))
        self.status_label.grid(row=8, column=0, columnspan=5, pady=(10, 0))

        #Score label 
        self.score_label = ttk.Label(main_frame, text=str(self.score), font=("Arial", 12))
        self.score_label.grid(row=9, column=0, columnspan=5, pady=(5, 0))

        # Reset button to start a new game
        reset_button = ttk.Button(main_frame, text="Reset Game", command=self.reset_game)
        reset_button.grid(row=10, column=0, columnspan=5, pady=(10, 0))

        # Create a button to submit the guess.
        submit_button = ttk.Button(main_frame, text="Submit Guess", command=self.submit_guess)
        submit_button.grid(row=7, column=0, columnspan=5, pady=(20, 0))

        # set focus to first cell at the start of the game
        self.entries[0][0].focus_set()

    def reset_game(self):
        # Reset the game state and clear the interface for a new game.
        self.current_row = 0
        self.target_word = generate_target_word()  
        self.score = 0

        # Update the score label and clear the status label.
        self.score_label.config(text=f"Score: {self.score}")
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
        guess = ''.join(l.upper() for l in letters)

        # clear 
        self.status_label.config(text="")

        #checks if the word in the dictonary
        if guess not in self.words:
            self.status_label.config(text="Not a valid word. Try again.")
            
        elif guess == self.target_word:
            #increase score and update status and score labels
            self.status_label.config(text="You've guessed the word!")
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
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

    def generate_target_word(self):
        # find a random letter in the alphabet and open the corresponding word list to select a random target word.
        random_number = random.randint(0, 25)
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        # build path to the CSV directory; this handles cases where the working directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.normpath(os.path.join(base_dir, '..', 'Word lists in csv')),
            os.path.normpath(os.path.join(base_dir, '..', 'Word-lists-in-csv', 'Word lists in csv'))
        ]
        csv_dir = None
        for c in candidates:
            if os.path.isdir(c):
                csv_dir = c
                break
        if csv_dir is None:
            raise FileNotFoundError(f"Could not locate word list directory. Tried: {candidates}")

        csv_path = os.path.join(csv_dir, f"{alphabet[random_number]}word.csv")

        if not os.path.isfile(csv_path):
            # give a helpful message rather than crashing with FileNotFoundError
            raise FileNotFoundError(f"Word list not found: {csv_path}")

        with open(csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            words = [row[0] for row in reader]
        self.words = words
        # generate a random word from the list and return it as the target word for the game.
        return random.choice(words)


# Create the main application window and start the application.
if __name__ == "__main__":
    root = Tk()
    current_row = 0 
    target_word = WordelApp.generate_target_word()  
    score = 0
    app = WordelApp(root,current_row,target_word,score)
    root.mainloop()

        