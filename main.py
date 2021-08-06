import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

from utils.metis import MetisClass, ReadingListItem
from utils.EntriesListHandler import *
from utils.DialogHandler import *

# ----- Initialize the Window ----- #

window = tk.Tk()
window.title('Metis')
window.minsize(width=920, height=400)
window.rowconfigure(0, minsize=100, weight=0)
window.rowconfigure(1, minsize=300, weight=1)
window.columnconfigure(0, minsize=500, weight=1)

# ------ Initialize Metis ----- #
Metis = MetisClass()

# ------------- GUI INITIALIZATION -------------- #
# ----- Set-up the Request GUI ----- #
frm_main = tk.Frame(window)
frm_main.grid(row=0, column=0)

def request_book():
    requested_title = Metis.request_book()
    ent_book_given.delete(0, tk.END)
    ent_book_given.insert(0, requested_title)

    # Show in the GUI that the chosen book is not unavailable
    if requested_title != 'No book available':
        Secretary.toggle(requested_title)

btn_request_book = tk.Button(
    master=frm_main,
    text="Click to request for a book",
    width=25,
    command=request_book
)
btn_request_book.grid(row=0, column=0, padx=10, pady=10)

ent_book_given = tk.Entry(master=frm_main,)
ent_book_given.bind("<Key>", lambda e : "break") # To make the Entry read-only
ent_book_given.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky='ew')

# ----- Create a Scrollable Canvas ----- #
frm_list = tk.Frame(master=window)
frm_list.grid(row=1, column=0, padx=20, pady=20, sticky='nsew')
frm_list.columnconfigure(0, minsize=400, weight=1)
frm_list.rowconfigure(0, minsize=400, weight=1)

# Create a canvas to draw things on
canvas_list = tk.Canvas(frm_list)
canvas_list.grid(row=0, column=0, sticky='nsew')

# Create the scrollbar
scrollbar = ttk.Scrollbar(frm_list, orient=tk.VERTICAL, command=canvas_list.yview)
scrollbar.grid(row=0, column=1, sticky='nsew')
scrollbar.grid_remove()

# Configure the canvas
SCROLLABLE = False

def check_scrollbar_visibility():
    global SCROLLABLE
    minHeight = frm_container.winfo_reqheight()
    if canvas_list.winfo_height() >= minHeight:
        scrollbar.grid_remove()
        SCROLLABLE = False
    else:
        scrollbar.grid(row=0, column=1, sticky='nsew')
        SCROLLABLE = True

def onCanvasConfigure(event):
    canvas_list.configure(scrollregion = canvas_list.bbox('all'))
    canvas_list.itemconfig('frame', width=canvas_list.winfo_width())

canvas_list.configure(yscrollcommand=scrollbar.set)
canvas_list.bind('<Configure>', onCanvasConfigure)

frm_container = tk.Frame(canvas_list)
canvas_list.create_window((0,0), width=canvas_list.winfo_reqwidth(), window=frm_container, anchor='nw', tags='frame')

# Make it scrollable using the mousewheel

def on_mouse_wheel(event):
    if SCROLLABLE:
        canvas_list.yview_scroll(-1 * int((event.delta / 120)), 'units')

def recursive_binding(w):
    w.bind('<MouseWheel>', on_mouse_wheel)
    for child in w.winfo_children():
        recursive_binding(child)

def reload_canvas():
    scrollbar.grid(row=0, column=1, sticky='nsew')
    canvas_list.configure(scrollregion=canvas_list.bbox('all'))
    canvas_list.config(yscrollcommand=scrollbar.set)
    check_scrollbar_visibility()

canvas_list.bind('<MouseWheel>', on_mouse_wheel)
frm_container.bind('<MouseWheel>', on_mouse_wheel)

# ----- Set-up the Reading List ----- #

Secretary = EntriesListHandler(window, Metis, frm_container, recursive_binding, reload_canvas)

# ----- Get the data file ----- #


btn_new_list = tk.Button(master=frm_main, text="New List", width=25)
btn_new_list.grid(row=1, column=0, padx=10, pady=5)

btn_load_list = tk.Button(master=frm_main, text="Load List", width=25)
btn_load_list.grid(row=1, column=1, padx=10, pady=5)

btn_save_list = tk.Button(master=frm_main, text="Save List", width=25)
btn_save_list.grid(row=1, column=2, padx=10, pady=5)

Dialogs = DialogHandler(Metis, Secretary, 
                        new_list_btn=btn_new_list, 
                        save_list_btn=btn_save_list, 
                        load_list_btn=btn_load_list)

# ----- Add Book Modal ----- #
btn_add_book = tk.Button(master=frm_main, text="Add Book", width=25)
btn_add_book.grid(row=1, column=3, padx=10, pady=5)

class AddDialog:
    """Provides an interface for handling the modal in creating a new book item."""
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
            "Pre-checks the information inputted before packing them in a dictionary for processing."

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
                'author': author if author else 'Anonymous',
                'date': date if date else 'n.d.',
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
    new_item = Metis.insert_item(modal.data)
    if not new_item:
        messagebox.showerror(message='Book already exists.')
    else:
        Secretary.insert(new_item)

btn_add_book.config(command=CallCreateDialog)

# Place this portion at the end of the program
window.mainloop()