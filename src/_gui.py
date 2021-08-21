"""
GUI Module

Contains the GUI-related methods and variables
for the App Clas
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# ----------------------------------------------- #
# ------------- GUI INITIALIZATION -------------- #
# ----------------------------------------------- #

def initialize_gui(self):

    self.window.rowconfigure(0, minsize=100, weight=0)      # the main buttons
    self.window.rowconfigure(2, minsize=300, weight=1)      # the canvas
    self.window.columnconfigure(0, minsize=500, weight=1)

    # ----- Set-up the Request GUI ----- #

    self.frm_main = tk.Frame(self.window)
    self.frm_main.grid(row=0, column=0)

    self.btn_request_book = tk.Button(
        master=self.frm_main,
        text="Click to request",
        width=20,
        cursor='hand2',
        command=self.request_book
    )
    self.btn_request_book.grid(row=0, column=0, padx=10, pady=10)

    self.ent_book_given = tk.Entry(master=self.frm_main, cursor='')
    self.ent_book_given.bind("<Key>", lambda e : "break") # To make the Entry read-only
    self.ent_book_given.bind("<FocusIn>", lambda e : self.window.focus_set())
    self.ent_book_given.grid(row=0, column=1, columnspan=4, padx=10, pady=10, sticky='ew')

    # ----- Create the File Handling Buttons ----- #

    self.btn_new_list = tk.Button(master=self.frm_main, text="New List", width=20, cursor='hand2')
    self.btn_new_list.grid(row=1, column=0, padx=10, pady=5)

    self.btn_load_list = tk.Button(master=self.frm_main, text="Load List", width=20, cursor='hand2')
    self.btn_load_list.grid(row=1, column=1, padx=10, pady=5)

    self.btn_save_list = tk.Button(master=self.frm_main, text="Save List", width=20, cursor='hand2')
    self.btn_save_list.grid(row=1, column=2, padx=10, pady=5)

    self.btn_save_as_list = tk.Button(master=self.frm_main, text="Save As", width=20, cursor='hand2')
    self.btn_save_as_list.grid(row=1, column=3, padx=10, pady=5)

    # ----- Create the Add Book Buttons ----- #

    self.btn_add_book = tk.Button(master=self.frm_main, text="Add Books", width=20, cursor='hand2')
    self.btn_add_book.grid(row=1, column=4, padx=10, pady=5)
    self.btn_add_book.config(command=self.call_add_dialog)

    # ----- Create the Misc Layer ----- #

    self.frm_misc = tk.Frame(master=self.window)
    self.frm_misc.grid(row=1, column=0, padx=25, sticky='ew')
    self.frm_misc.columnconfigure(index=0, minsize=15, weight=0)
    self.frm_misc.columnconfigure(index=1, minsize=200, weight=1)

    # ----- Create the Genre Filters ----- #

    self.lbl_genres = tk.Label(master=self.frm_misc, text="Genres:")
    self.lbl_genres.grid(row=0, column=0, padx=10, pady=5)

    self.frm_genres = tk.Frame(master=self.frm_misc)
    self.frm_genres.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

    # ----- Create Name Filter ----- #

    self.lbl_search = tk.Label(master=self.frm_misc, text="Search: ")
    self.lbl_search.grid(row=1, column=0, padx=10, pady=5)

    self.ent_search = tk.Entry(master=self.frm_misc)
    self.ent_search.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
    self.ent_search.focus()

    # ----- Show the Not Read / Available Stats ----- #

    self.lbl_unread = tk.Label(master=self.frm_misc, text='')
    self.lbl_unread.grid(row=2, column=0, padx=10, pady=5)

    # ----- Create a Scrollable Canvas ----- #

    self.frm_list = tk.Frame(master=self.window)
    self.frm_list.grid(row=2, column=0, padx=20, pady=5, sticky='nsew')
    self.frm_list.columnconfigure(0, minsize=400, weight=1)
    self.frm_list.rowconfigure(0, minsize=400, weight=1)

    # Create a canvas to draw things on
    self.canvas_list = tk.Canvas(self.frm_list)
    self.canvas_list.grid(row=0, column=0, sticky='nsew')

    # Create the scrollbar
    self.scrollbar = ttk.Scrollbar(self.frm_list, orient=tk.VERTICAL, command=self.canvas_list.yview)
    self.scrollbar.grid(row=0, column=1, sticky='nsew')
    self.scrollbar.grid_remove()

    # Configure the canvas
    self.scrollable = False
    
    def onCanvasConfigure(event):
        self.canvas_list.configure(scrollregion = self.canvas_list.bbox('all'))
        self.canvas_list.itemconfig('frame', width=self.canvas_list.winfo_width())

    self.canvas_list.configure(yscrollcommand=self.scrollbar.set)
    self.canvas_list.bind('<Configure>', onCanvasConfigure)

    self.frm_container = tk.Frame(self.canvas_list)
    self.canvas_list.create_window((0,0), width=self.canvas_list.winfo_reqwidth(), window=self.frm_container, anchor='nw', tags='frame')

    # Make it scrollable using the mousewheel

    self.canvas_list.bind('<MouseWheel>', self.onCanvasMouseWheel)
    self.frm_container.bind('<MouseWheel>', self.onCanvasMouseWheel)

# -------------------------------------------------- #
# --------------- EVENTS METHODS ------------------- #
# -------------------------------------------------- #

def recursive_binding(self, w):
        "Recursion to bind a widget and all its children to be scrollable"

        w.bind('<MouseWheel>', self.onCanvasMouseWheel)
        for child in w.winfo_children():
            self.recursive_binding(child)

def onCanvasMouseWheel(self, event):
        "Enables the canvas to be scrollable using the mouse wheel."
        if self.scrollable:
            self.canvas_list.yview_scroll(-1 * int((event.delta / 120)), 'units')

# ------------------------------------------- #
# ---------- GUI HANDLER METHODS ------------ #
# ------------------------------------------- #

def check_scrollbar_visibility(self):
    """
    Hides / Unhides the scrollbar when necessary.
    
    Calculates if the required height for the
    frm_container (the tk.Frame that currently
    holds the reading list) exceeds that of the
    canvas and adjusts the scrollbar and scrollability
    accordingly. 
    """

    minHeight = self.frm_container.winfo_reqheight()

    if self.canvas_list.winfo_height() >= minHeight:
        self.scrollbar.grid_remove()
        self.scrollable = False
    else:
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.scrollable = True

def reload_canvas(self):
    """
    Re-calibrates the canvas to update the scrollbar.
    
    For some tkinter reason, the scrollbar does not re-compute
    its size automatically whenever its sister-component
    changes size. This serves as a force recomputation.
    """

    self.scrollbar.grid(row=0, column=1, sticky='nsew')
    self.canvas_list.configure(scrollregion=self.canvas_list.bbox('all'))
    self.canvas_list.config(yscrollcommand=self.scrollbar.set)
    self.check_scrollbar_visibility()

def unread_ratio_reload(self):
    """
    Updates the available/showable ration.
    
    Rationale: As this purely relies on the
        backend data, Metis reload and Secretary
        reload must occur before calling this
        method.
    """

    self.unread = len(set(filter(self.Metis.is_available, self.Metis.collection.values())))
    self.population = len(set(filter(self.Metis.is_showable, self.Metis.collection.values())))
    self.lbl_unread.config(text=f'To read: {self.unread} / {self.population}')
    