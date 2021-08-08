import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

import configparser

from utils.metis import MetisClass, ReadingListItem
from utils.EntriesListHandler import *
from utils.DialogHandler import *

class App:
    """A class that handles the overall operation of the Metis program."""

    TITLE = 'Metis'
    CONFIG_PATH = 'config.ini'

    def __init__(self):

        self.filepath = ''

        # ----- Initialize the Window ----- #

        self.window = tk.Tk()
        self.window.title(App.TITLE)
        self.window.minsize(width=920, height=400)
        self.window.rowconfigure(0, minsize=100, weight=0)
        self.window.rowconfigure(1, minsize=300, weight=1)
        self.window.columnconfigure(0, minsize=500, weight=1)

        # ------ Initialize Metis ----- #

        self.Metis = MetisClass()

        # ----------------------------------------------- #
        # ------------- GUI INITIALIZATION -------------- #
        # ----------------------------------------------- #

        # ----- Set-up the Request GUI ----- #

        self.frm_main = tk.Frame(self.window)
        self.frm_main.grid(row=0, column=0)

        self.btn_request_book = tk.Button(
            master=self.frm_main,
            text="Click to request for a book",
            width=25,
            command=self.request_book
        )
        self.btn_request_book.grid(row=0, column=0, padx=10, pady=10)

        self.ent_book_given = tk.Entry(master=self.frm_main,)
        self.ent_book_given.bind("<Key>", lambda e : "break") # To make the Entry read-only
        self.ent_book_given.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky='ew')

        # ----- Create a Scrollable Canvas ----- #

        self.frm_list = tk.Frame(master=self.window)
        self.frm_list.grid(row=1, column=0, padx=20, pady=20, sticky='nsew')
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

        def on_mouse_wheel(event):
            if self.scrollable:
                self.canvas_list.yview_scroll(-1 * int((event.delta / 120)), 'units')

        def recursive_binding(w):
            "Recursion to bind a widget and all its children to be scrollable"

            w.bind('<MouseWheel>', on_mouse_wheel)
            for child in w.winfo_children():
                recursive_binding(child)
        
        self.canvas_list.bind('<MouseWheel>', on_mouse_wheel)
        self.frm_container.bind('<MouseWheel>', on_mouse_wheel)

        # ----- Create the File Handling Buttons ----- #

        self.btn_new_list = tk.Button(master=self.frm_main, text="New List", width=25)
        self.btn_new_list.grid(row=1, column=0, padx=10, pady=5)

        self.btn_load_list = tk.Button(master=self.frm_main, text="Load List", width=25)
        self.btn_load_list.grid(row=1, column=1, padx=10, pady=5)

        self.btn_save_list = tk.Button(master=self.frm_main, text="Save List", width=25)
        self.btn_save_list.grid(row=1, column=2, padx=10, pady=5)

        # ----- Create the Add Book Buttons ----- #

        self.btn_add_book = tk.Button(master=self.frm_main, text="Add Book", width=25)
        self.btn_add_book.grid(row=1, column=3, padx=10, pady=5)
        self.btn_add_book.config(command=self.CallCreateDialog)

        # --------------------------------------------------- #
        # ------------- HANDLE THE INTERACTIONS ------------- #
        # --------------------------------------------------- #

        # ----- Set-up the Reading List Backend ----- #

        self.Secretary = EntriesListHandler(
            window=self.window,
            toggler=self.Metis.toggle, 
            master=self.frm_container, 
            binding=recursive_binding, 
            reloader=self.reload_canvas,
            collection=self.Metis.collection,
        )

        # ----- Set up File Handling ----- #

        self.Dialogs = DialogHandler(
            encoder_class=ReadingListItem.CollectionEncoder,
            decoder_function=ReadingListItem.decode_collection
        )

        self.btn_new_list.config(command=self.cmd_new_list)
        self.btn_save_list.config(command=self.cmd_save_list)
        self.btn_load_list.config(command=self.cmd_load_list)

        # ----- Load the config file ----- #

        self.loadApp()

    # -------------------------------------------------- #
    # --------------- WIDGET METHODS ------------------- #
    # -------------------------------------------------- #

    def request_book(self):
            "Requests a title (string) from Metis"

            requested_title = self.Metis.request_book()
            self.ent_book_given.delete(0, tk.END)
            self.ent_book_given.insert(0, requested_title)

            # Show in the GUI that the chosen book is not unavailable
            if requested_title != 'No book available':
                self.Secretary.toggle(requested_title)
    
    def CallCreateDialog(self):
        "Creates a dialog box for adding a new book entry"

        modal = AddDialog(self.window)

        # Verify if there is data
        if not modal.data:
            return

        # Verify if the book already exists
        new_item = self.Metis.insert_item(modal.data)
        if not new_item:
            messagebox.showerror(message='Book already exists.')
        else:
            self.Secretary.insert(new_item)
    
    @DialogHandler.ask_confirmation
    def cmd_new_list(self):

        self.filepath = ''
        self.window.title(App.TITLE)

        self.Metis.reload()
        self.Secretary.reload()
        self.reload_config_path()
    
    def cmd_save_list(self):
        self.filepath = self.Dialogs.cmd_save_list(self.Metis.collection)
        self.reload_config_path()

    def cmd_load_list(self):
        res = self.Dialogs.cmd_load_list()

        if not res:
            return

        self.filepath = res['filepath']
        self.load_file_path()
        self.reload_config_path()

    # ------------------------------------------- #
    # ---------- GUI HANDLER METHODS ------------ #
    # ------------------------------------------- #
    
    def check_scrollbar_visibility(self):
        "Hides / Unhides the scrollbar when necessary"

        minHeight = self.frm_container.winfo_reqheight()

        if self.canvas_list.winfo_height() >= minHeight:
            self.scrollbar.grid_remove()
            self.scrollable = False
        else:
            self.scrollbar.grid(row=0, column=1, sticky='nsew')
            self.scrollable = True

    def reload_canvas(self):
        "Re-calibrates the canvas to update the scrollbar"

        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.canvas_list.configure(scrollregion=self.canvas_list.bbox('all'))
        self.canvas_list.config(yscrollcommand=self.scrollbar.set)
        self.check_scrollbar_visibility()
        
    def loadApp(self):
        "Sets up the windows and the App configurations."

        # Load the config file
        try:
            config = configparser.ConfigParser()
            config.read(App.CONFIG_PATH)
            self.filepath = config['recent_file']['path']
        except:
            config = configparser.ConfigParser()
            config['recent_file'] = { 'path' : '' }
            with open(App.CONFIG_PATH, 'w') as config_file:
                config.write(config_file)
            print('Successfully created config file!')
        else:
            print(f'Successfully loaded config file!\nFile Path: {self.filepath}')
        
        self.load_file_path()
    
    def load_file_path(self):
        "Configures the App and loads the filepath"

        if self.filepath:
            with open(self.filepath, 'r') as data_file:
                data = data_file.read()
                try:
                    collection = json.loads(data, object_hook=self.Dialogs.decoder)
                except ValueError as e:
                    messagebox.showerror(title='Error', message='Invalid config file! The recent_file path cannot be read.')
                    print(e)
                    return None
                else:
                    self.window.title(f'{App.TITLE} - {self.filepath}')
                    try:
                        current_collection = collection[:]
                    except TypeError:
                        current_collection = collection['collection']
                    self.Metis.reload(current_collection)
                    self.Secretary.reload()

        else:
            self.window.title(App.TITLE)
            self.Metis.reload()
            self.Secretary.reload()
    
    def reload_config_path(self):
        config = configparser.ConfigParser()
        config.read(App.CONFIG_PATH)
        config['recent_file']['path'] = self.filepath
        with open(App.CONFIG_PATH, 'w') as config_file:
            config.write(config_file)
    
    def startApp(self):
        self.window.mainloop()

if __name__ == '__main__':
    app = App()
    app.startApp()