import tkinter as tk

from metis import MetisClass, ReadingListItem

# For initial testing while JSON
# is not yet implemented

dummy_values = [
    ('The ONE Thing', 'Gary Keller et al', '2013'),
    ('Atomic Habits', 'James Clear', '2018'),
    ('Blink', 'Malcolm Gladwell', '2007'),
    ('Extreme Ownership', 'Jocko Willink', '2015'),
    ('The Power of Habit', 'Charles Dughigg', '2014')
]
dummy_collection = [ReadingListItem(title=x[0], author=x[1], date=x[2]) for x in dummy_values]

# ----- Initialize the Window ----- #

window = tk.Tk()
window.title('Metis')
window.minsize(width=800, height=400)
window.rowconfigure(0, minsize=100, weight=0)
window.rowconfigure(1, minsize=300, weight=1)
window.columnconfigure(0, minsize=500, weight=1)

# ------ Initialize Metis ----- #
Metis = MetisClass(dummy_collection)

# ----- Request for a book ----- #
def request_book():
    requested_title = Metis.request_book()
    ent_book_given.delete(0, tk.END)
    ent_book_given.insert(0, requested_title)

# ----- Set-up the GUI ----- #
frm_main = tk.Frame(window)
frm_main.grid(row=0, column=0)

btn_request_book = tk.Button(
    master=frm_main,
    text="Click to request for a book",
    width=25,
    command=request_book
)
btn_request_book.grid(row=0, column=0, padx=10, pady=10)

ent_book_given = tk.Entry(
    master=frm_main,
    width=60
)
ent_book_given.bind("<Key>", lambda e : "break") # To make the Entry read-only
ent_book_given.grid(row=0, column=1, padx=10, pady=10)

frm_list = tk.Frame(master=window)
frm_list.grid(row=1, column=0, sticky='ew')

# ----- Populate the List ----- #
class ListEntry:
    def __init__(self, frame : tk.Frame, item : ReadingListItem):
        self.frame = frame
        self.item = item
        self.available = item.available
    
        # --- Create the GUI --- #
        CLR_AVAILABLE = "#e4ffbd"
        CLR_UNAVAILABLE = "#ffbdbd"

        def on_click(event):
            Metis.toggle(item)
            self.available = not self.available
            self.frame.config(bg=CLR_AVAILABLE if self.available else CLR_UNAVAILABLE)
            self.label.config(background=self.frame['bg'])

        self.frame.config(height=25, bg=CLR_AVAILABLE if self.available else CLR_UNAVAILABLE)
        self.frame.bind("<Button-1>", on_click)
        self.frame.pack(fill=tk.X, padx=10, pady=5)

        self.label = tk.Label(master=self.frame, text=self.item.format_book(), background=self.frame['bg'])
        self.label.bind("<Button-1>", on_click)
        self.label.pack(padx=5, pady=5)

gui_list = [ListEntry(tk.Frame(frm_list), item) for item in Metis.collection]
print(gui_list)

# Place this portion at the end of the program
window.mainloop()