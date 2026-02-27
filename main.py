from tkinter import *
from tkinter import ttk
# Create the main application window class with helper functions to manage the GUI components and interactions.
class WordelApp:
    def __init__(self, root):
        # Initialize the main application window and set up the user interface.
        self.root = root
        self.root.title("Wordel")
        self.root.geometry("500x600")
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
                entry = ttk.Entry(main_frame, width=3)
                entry.grid(row=i+1, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.entries.append(row_entries)