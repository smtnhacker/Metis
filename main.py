import tkinter as tk
from tkinter import messagebox

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

# ----- Set-up the Request GUI ----- #
frm_main = tk.Frame(window)
frm_main.grid(row=0, column=0)

def request_book():
    requested_title = Metis.request_book()
    ent_book_given.delete(0, tk.END)
    ent_book_given.insert(0, requested_title)

    # Show in the GUI that the chosen book is not unavailable
    if requested_title != 'No book available':
        item_list[requested_title].toggle()

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

# ----- Add Book Modal ----- #
btn_add_book = tk.Button(
    master=frm_main,
    text="Add Book",
    width=25,
)
btn_add_book.grid(row=1, column=0, padx=10, pady=5)

class AddDialog:
    def __init__(self, root : tk.Tk):
        self.data = None

        modal = tk.Toplevel(root)
        modal.title('Add a new book')
        modal.minsize(500, 330)
        modal.resizable(False, False)

        modal.protocol("WM_DELETE_WINDOW", lambda : self.dismiss(modal))
        modal.transient(root)
        modal.wait_visibility()
        modal.grab_set()

        # --- Set-up the modal --- #
        frm_entries = tk.Frame(modal)
        frm_entries.pack(padx=20, pady=10)

        lbl_title = tk.Label(master=frm_entries, text='Title: ')
        lbl_title.grid(row=0, column=0)
        ent_title = tk.Entry(master=frm_entries)
        ent_title.grid(row=0, column=1, sticky='ew')
        ent_title.focus()

        lbl_subtitle = tk.Label(master=frm_entries, text='Subtitle: ')
        lbl_subtitle.grid(row=1, column=0)
        ent_subtitle = tk.Entry(master=frm_entries)
        ent_subtitle.grid(row=1, column=1, sticky='ew')

        lbl_author = tk.Label(master=frm_entries, text='Author')
        lbl_author.grid(row=2, column=0)
        ent_author = tk.Entry(master=frm_entries)
        ent_author.grid(row=2, column=1, sticky='ew')

        lbl_date = tk.Label(master=frm_entries, text='Date: ')
        lbl_date.grid(row=3, column=0)
        ent_date = tk.Entry(master=frm_entries)
        ent_date.grid(row=3, column=1, sticky='ew')

        lbl_summary = tk.Label(master=frm_entries, text='Summary: ')
        lbl_summary.grid(row=4, column=0)
        txt_summary = tk.Text(master=frm_entries, width=40, height=7)
        txt_summary.grid(row=4, column=1)
        
        frm_btn = tk.Frame(modal)
        frm_btn.pack(padx=20, pady=5)

        def pre_submit():

            # Check if there is a title
            title = ent_title.get()
            if not title:
                messagebox.showerror(message='You must have a title!')
                return
            
            subtitle = ent_subtitle.get()
            author = ent_author.get()
            date = ent_date.get()
            summary = txt_summary.get("1.0", tk.END)

            data = {
                'title': title,
                'subtitle': subtitle,
                'author': author,
                'date': date,
                'summary': summary,
            }

            self.submit(modal, data)
        
        btn_submit = tk.Button(master=frm_btn, text='Submit', command=pre_submit)
        btn_submit.grid(row=0, column=0, padx=10)

        btn_cancel = tk.Button(master=frm_btn, text='Cancel', command=lambda : self.dismiss(modal))
        btn_cancel.grid(row=0, column=1, padx=10)

        modal.wait_window()
    
    def dismiss(self, modal):
        modal.grab_release()
        modal.destroy()
    
    def submit(self, modal, data : dict):
        self.data = data
        self.dismiss(modal)

def CallCreateDialog():
    modal = AddDialog(window)

    # Verify if there is data
    if not modal.data:
        return

    # Verify if the book already exists
    if not Metis.insert_item(modal.data):
        messagebox.showerror(message='Book already exists.')
    else:
        print(modal.data)
        messagebox.showinfo(message='Book successfully added!')

btn_add_book.config(command=CallCreateDialog)

# ----- Set-up the Reading List GUI ----- #
frm_list = tk.Frame(master=window)
frm_list.grid(row=1, column=0, sticky='ew')

class ListEntry:
    """An interactive Frame that represents a reading list item."""

    COLOR_AVAILABLE = "#e4ffbd"
    COLOR_UNAVAILABLE = "#ffbdbd"

    def __init__(self, frame : tk.Frame, item : ReadingListItem):
        self.frame = frame
        self.item = item
        self.available = item.available
    
        # --- Create the GUI --- #

        def on_click(event):
            Metis.toggle(self.item)
            self.toggle()

        self.frame.config(height=25, bg=ListEntry.COLOR_AVAILABLE if self.available else ListEntry.COLOR_UNAVAILABLE)
        self.frame.bind("<Button-1>", on_click)
        self.frame.pack(fill=tk.X, padx=10, pady=5)

        self.label = tk.Label(master=self.frame, text=self.item.format_book(), background=self.frame['bg'])
        self.label.bind("<Button-1>", on_click)
        self.label.pack(padx=5, pady=5)
    
    def toggle(self):
        self.available = not self.available
        self.frame.config(bg=ListEntry.COLOR_AVAILABLE if self.available else ListEntry.COLOR_UNAVAILABLE)
        self.label.config(background=self.frame['bg'])

item_list = { item.format_book() : ListEntry(tk.Frame(frm_list), item) for item in Metis.collection}

# Place this portion at the end of the program
window.mainloop()