from tkinter import *
from tkinter import ttk
# Create the main application window class with helper functions to manage the GUI components and interactions.
class WordelApp:
    def __init__(self, root, current_row, target_word):
        # Initialize the main application window and set up the user interface.
        self.root = root
        self.root.title("Wordel")
        self.root.geometry("500x600")

        # store game state
        self.current_row = current_row
        self.target_word = target_word

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
                entry = ttk.Entry(main_frame, width=30)
                entry.grid(row=i+1, column=j, padx=20, pady=20)
                row_entries.append(entry)
            self.entries.append(row_entries)
        # Create a button to submit the guess. use lambda to defer execution.
        submit_button = ttk.Button(main_frame, text="Submit Guess", command=self.submit_guess)
        submit_button.grid(row=7, column=0, columnspan=5, pady=(20, 0))

    def submit_guess(self):
        # Collect the guess from entry field and test it against the target word.
        guess = ''.join(entry.get() for entry in self.entries[self.current_row])

        # make sure entry length matches target length
        if len(guess) != len(self.target_word):
            print(f"Please enter a {len(self.target_word)}-letter word.")
            return

        if guess == self.target_word:
            print("Congratulations! You've guessed the word!")
        else:
            # Update the background color based on the guess.
            for i in range(len(self.target_word)):
                if guess[i] == self.target_word[i]:
                    self.entries[self.current_row][i].config(background='green')
                elif guess[i] in self.target_word:
                    self.entries[self.current_row][i].config(background='yellow')
                else:
                    self.entries[self.current_row][i].config(background='red')
            # Increment the current row for the next guess and check if the game is over.
            self.current_row += 1
            if self.current_row >= 6:
                print("Game Over! The correct word was:", self.target_word)



# Create the main application window and start the application.
if __name__ == "__main__":
    root = Tk()
    current_row = 0
    target_word = "APPLE"  
    app = WordelApp(root,current_row,target_word)
    root.mainloop()

        