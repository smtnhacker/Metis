import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
import time, json

from metis import MetisClass, ReadingListItem

# ----- Initialize the Window ----- #

window = tk.Tk()
window.title('Metis')
window.minsize(width=920, height=400)
window.rowconfigure(0, minsize=100, weight=0)
window.rowconfigure(1, minsize=300, weight=1)
window.columnconfigure(0, minsize=500, weight=1)

# ------ Initialize Metis ----- #
current_collection = []
Metis = MetisClass(current_collection)

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

# ----- Get the data file ----- #

def decode_collection(dct):
    if '__ReadingListItem__' in dct:
        return  ReadingListItem(**{key : value for key, value in dct.items() if key != '__ReadingListItem__'})
    else:
        return dct

class CollectionEncoder(json.JSONEncoder):
    def default(self, dct):
        if isinstance(dct, ReadingListItem):
            res = { '__ReadingListItem__' : True }
            for key, value in dct.__dict__.items():
                res[key] = value
            return res
        else:
            return super().default(dct)

def cmd_new_list():
    global current_collection, Metis
    current_collection = []
    Metis = MetisClass(current_collection)
    Secretary.reload()

def cmd_load_list():
    filepath = askopenfilename(
        filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')]
    )
    if not filepath:
        return None
    with open(filepath, 'r') as data_file:
        data = data_file.read()
        try:
            collection = json.loads(data, object_hook=decode_collection)
        except ValueError as e:
            messagebox.showerror(title='Error', message='Invalid file.')
            print(e.message)
            return None
    
    global current_collection, Metis
    try:
        current_collection = collection[:]
    except TypeError:
        current_collection = collection['collection']
    Metis = MetisClass(current_collection)
    Secretary.reload()

def cmd_save_list():
    filepath = asksaveasfilename(
        defaultextension='json',
        filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')],
    )
    if not filepath:
        return
    with open(filepath, 'w') as output_file:
        json.dump(current_collection, output_file, indent=4, cls=CollectionEncoder)

btn_new_list = tk.Button(master=frm_main, text="New List", width=25, command=cmd_new_list)
btn_new_list.grid(row=1, column=0, padx=10, pady=5)

btn_load_list = tk.Button(master=frm_main, text="Load List", width=25, command=cmd_load_list)
btn_load_list.grid(row=1, column=1, padx=10, pady=5)

btn_save_list = tk.Button(master=frm_main, text="Save List", width=25, command=cmd_save_list)
btn_save_list.grid(row=1, column=2, padx=10, pady=5)

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
        messagebox.showinfo(message='Book successfully added!')

btn_add_book.config(command=CallCreateDialog)

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
    global SCROLLABLE
    if SCROLLABLE:
        canvas_list.yview_scroll(-1 * int((event.delta / 120)), 'units')

def recursive_binding(w):
    w.bind('<MouseWheel>', on_mouse_wheel)
    for child in w.winfo_children():
        recursive_binding(child)

def reload_canvas():
    global scrollbar
    global canvas_list
    scrollbar.grid(row=0, column=1, sticky='nsew')
    canvas_list.configure(scrollregion = canvas_list.bbox('all'))
    canvas_list.config(yscrollcommand=scrollbar.set)
    check_scrollbar_visibility()

canvas_list.bind('<MouseWheel>', on_mouse_wheel)
frm_container.bind('<MouseWheel>', on_mouse_wheel)

# ----- Set-up the Reading List GUI ----- #

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

class EntriesListHandler:
    def __init__(self):
        self.item_list = dict()
        self.frame_list = dict()

    def load(self):
        for item in Metis.collection:
            self.insert(item)
    
    def unload(self):
        for item in self.frame_list.values():
            item.destroy()
        self.item_list = dict()
        self.frame_list = dict()
    
    def reload(self):
        self.unload()
        self.load()
        reload_canvas()
    
    def insert(self, item):
        self.frame_list[item.format_book()] = tk.Frame(frm_container)
        self.item_list[item.format_book()] = ListEntry(self.frame_list[item.format_book()], item)

        window.update()

        # some shz on scrollbar
        recursive_binding(self.frame_list[item.format_book()])
        reload_canvas()
    
    def toggle(self, item_name):
        self.item_list[item_name].toggle()

Secretary = EntriesListHandler()

# Place this portion at the end of the program
window.mainloop()