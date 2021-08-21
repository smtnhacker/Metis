# # -------------------------------- #
#        Metis - Reading Guide
#        By Something_Hacker
# # -------------------------------- #
#
# Rationale:
#   When one has an ever growing reading list, 
#   it is not surprising to find oneself in a
#   state of choice paralysis. As such, it
#   might be useful to leave the dilemma of
#   choosing to something cold and calculating,
#   AKA, a program.
# 
# Description:
#   Metis is a simple program that lets the user
#   create, edit, and save reading lists. Upon
#   the user's request, Metis will provide a book.
#   To improve the reading experience, the genre
#   of the provided book will vary as much as possible.
#
# # -------------------------------------------------- # #

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

import json
import configparser

from utils.metis import *
from utils.EntriesListHandler import *
from utils.FileDialogHandler import *
from utils.DetailDialog import *
from utils.GenreHandler import *
from utils.SaveFile import *

class App:
    """A class that handles the overall operation of the Metis program."""

    TITLE = 'Metis'
    CONFIG_PATH = 'config.ini'

    def __init__(self):

        self.filepath = ''
        self.changed = False    # False at start and after reloading config (save as, load, new) and save
                                # Not yet used, too hassle to implement smh

        # ----- Initialize the Window ----- #

        self.window = tk.Tk()
        self.window.title(App.TITLE)
        self.window.minsize(width=960, height=400)
        self.window.rowconfigure(0, minsize=100, weight=0)      # the main buttons
        self.window.rowconfigure(2, minsize=300, weight=1)      # the canvas
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

        def onCanvasMouseWheel(event):
            "Enables the canvas to be scrollable using the mouse wheel."
            if self.scrollable:
                self.canvas_list.yview_scroll(-1 * int((event.delta / 120)), 'units')

        def recursive_binding(w):
            "Recursion to bind a widget and all its children to be scrollable"

            w.bind('<MouseWheel>', onCanvasMouseWheel)
            for child in w.winfo_children():
                recursive_binding(child)
        
        self.canvas_list.bind('<MouseWheel>', onCanvasMouseWheel)
        self.frm_container.bind('<MouseWheel>', onCanvasMouseWheel)

        # --------------------------------------------------- #
        # ------------- HANDLE THE INTERACTIONS ------------- #
        # --------------------------------------------------- #

        # ----- Set-up the Reading List Backend ----- #

        def _on_toggle(item):
            self.Metis.toggle(item)
            self.unread_ratio_reload()
        
        def _on_delete(item):
            self.Metis.delete_item(item)
            self.unread_ratio_reload()
        
        def _on_edit(item, data):
            res = self.Metis.edit_item(item, data)
            self.unread_ratio_reload()
            return res

        self.Secretary = EntriesListHandler(
            window=self.window,
            master=self.frm_container, 
            binding=recursive_binding, 
            canvas_reloader=self.reload_canvas,
            collection=self.Metis.collection.values(),
            genre_suggestions=self.Metis.available_genres,
            on_edit=_on_edit,
            on_delete=_on_delete,
            on_toggle=_on_toggle, 
            is_available=self.Metis.is_showable,
        )

        # ----- Set up File Handling ----- #

        self.Dialogs = FileDialogHandler(
            encoder_class=SaveFile.CollectionEncoder,
            decoder_function=SaveFile.decode_collection
        )

        self.btn_new_list.config(command=self.cmd_new_list)
        self.btn_save_list.config(command=self.cmd_save_list)
        self.btn_load_list.config(command=self.cmd_load_list)
        self.btn_save_as_list.config(command=self.cmd_save_as_list)

        # ----- Set up genre filtering ----- #

        def onGenreEdit():
            "Whenever the GenrePacker updates the genres, the App must also be updated."

            self.Metis.reload_available()
            self.Secretary.reload()
            self.unread_ratio_reload()

        self.genres = GenrePacker(
            master=self.frm_genres, 
            genres=self.Metis.filter, 
            suggestions=self.Metis.available_genres, # Should serve to show the current genres in the App
            on_edit=onGenreEdit,
        )

        # ----- Set up name filtering ----- #

        def onSearchKeyPress(*args):
            text = self.ent_search.get()
            self.Metis.search_filter = text
            self.Metis.reload_available()
            self.Secretary.reload()
            self.unread_ratio_reload()

        self.var_search_text = tk.StringVar()
        self.var_search_text.trace('w', onSearchKeyPress)
        self.ent_search.config(textvariable=self.var_search_text)

        # ----- Load the config file ----- #

        self.loadApp()

    # -------------------------------------------------- #
    # --------------- WIDGET METHODS ------------------- #
    # -------------------------------------------------- #

    def request_book(self):
        """
        Requests a book item from Metis and displays it.
        
        Rationale: To reduce complexity from Metis, the requested
            item must be the ReadingItemList and the App should
            handle the processing.
        
        Result (if success):
            1. The entry text will be updated.
            2. The item will be toggled (both in GUI and in Metis).
        """

        requested_item = self.Metis.request_book()
        requested_title = requested_item.format_book() if requested_item else 'No book available'
        self.ent_book_given.delete(0, tk.END)
        self.ent_book_given.insert(0, requested_title)

        # Show in the GUI that the chosen book is not unavailable
        if requested_title != 'No book available':
            self.Secretary.toggle(requested_item.get_uid())
    
    def call_add_dialog(self):
        """
        Creates a dialog box for adding a new book entry
        
        Rationale: When creating a new book, three steps
            are currently taken:
            1. Get data from the dialog
            2. Insert data to Metis
            3. Update others.
            This function should serve as the integrating
            function to simplify the function of each independent
            components.
        """

        def attempt_submit(data):
            new_item = self.Metis.insert_item(data)
            if not new_item:
                messagebox.showerror(message='Book already exists.')
            else:
                if self.Metis.is_available(new_item):
                    self.Secretary.insert(new_item)
                self.unread_ratio_reload()
                return new_item

        modal = AddDialog(root=self.window, attempt_submit=attempt_submit, suggestions=self.Metis.available_genres)

        # Verify if the dialogs should end
        if not modal.item:
            return
        
        # call again to add another book
        self.call_add_dialog()
    
    @FileDialogHandler.ask_confirmation
    def cmd_new_list(self):
        """
        Creates a new list by erasing all previously added data.

        Rationale: Creating a new list is the same as loading an
            empty file. To make things uniform, this must be 
            similar to that of loading.
        
        Result:
            1. The contents will be empty.
            2. The self.filepath will be empty('')
            3. The config will be reset.
        """

        self.filepath = self.attempt_load('')
        self.reload_config_path()
    
    def get_state_data(self):
        """
        Returns a SaveFile to use for saving.

        Rationale: To provide a uniform way of obtaining the
            data needed for saving. All save functions must
            use this function when obtaining data.

        Currently, a Save File has the following components:
        1. collection : dict 
            - a (key, value) pair of ReadingListItem.uid : ReadingListItem
              that is used primarily by Metis.
        2. recently_read : Collections.deque
            - a deque of string values that represents the recenlty read genres
        3. filter : set
            - a set of the filters currently applied
        
        Return Value:
            SaveFile - stores the current state of Metis
        """
        
        save_collection = self.Metis.collection
        save_recently_read = self.Metis.recently_read_genre
        save_filter = self.Metis.filter
        data = {
            'collection' : save_collection,
            'recently_read' : save_recently_read,
            'filter' : save_filter,
        }
        return SaveFile(**data)

    def cmd_save_list(self):
        """
        Saves if a save file already exists, if not, creates a new save file.

        Rationale: Users should not be burdened with overwriting the same
            file when saving. If a save file already exists, this function
            must purely get the current data and dump in to the save file.
            But if no save file exists, it must be exactly the same with
            that of save as.
        """

        if not self.filepath:
            self.cmd_save_as_list()
        else:
            data = self.get_state_data()
            self.Dialogs.save_file(data=data, filepath=self.filepath)
            self.changed = False
    
    def cmd_save_as_list(self):
        """
        Creates a new save file (if saved).

        Rationale: When saving, there are 4 major steps:
            1. Getting the state data
            2. Creating a save file
            3. Dumping the data
            4. Updating the App config
            This step serves as the integrating function
            to keep each of the steps as independent as possible.

            It should be noted that there are parallels between
            saving and loading, specifically step 4. Saving should
            effectively reproduce the same result as that of loading,
            without having to actually load for performance reasons.
        
        It should be noted that if no save file is created,
        there must NOT be any changes. Reasons for failure includes:
            - user canceling the action
            - unable to dump data
        If there are failure, the current state must NOT be affected
        in any way.

        Result (if success):
            1. The self.filepath will be updated.
            2. The config will be updated.
        """
        
        data = self.get_state_data()
        save_filepath = self.Dialogs.cmd_save_list(data=data)

        if not save_filepath:
            return

        self.filepath = save_filepath
        self.reload_config_path()

    def cmd_load_list(self):
        """
        Loads a save file through a dialog.

        Rationale: Loading in this manner occurs in 3 steps:
            1. Getting filepath from dialog
            2. Attempting to load filepath
            3. Updating the App config
            This step serves as the integrating function
            to keep each of the steps as independent as possible.

        It should be noted that for this step, the failure of
        not acquiring any filepath should NOT result to any
        changes within the App.

        Result (if success):
            1. The data will be loaded.
            2. The self.filepath will be updated.
            3. The config will be updated.
        """

        res = self.Dialogs.cmd_load_list()

        if not res:
            return

        self.filepath = self.attempt_load(res['filepath'])
        self.reload_config_path()

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
        
    def loadApp(self):
        """
        Sets up the windows and the App configurations.

        Rationale: At the beginning of the App, the configurations
            must be loaded. This includes loading the previously
            used reading list to provide ease of experience for the
            user. 

            It might be possible that the config file is corrupted,
            and if such occurs, the App MUST still load, albeit empty
            and the config file should be fixed.
        """

        # Load the config file

        config = configparser.ConfigParser()
        try:
            config.read(App.CONFIG_PATH)
            filepath = config['recent_file']['path']
        
        # In the case that the config file is corrupted,
        # correct the file

        except Exception as e:
            config['recent_file'] = { 'path' : '' }
            filepath = ''
            with open(App.CONFIG_PATH, 'w') as config_file:
                config.write(config_file)
            print('Successfully created config file!')

        # Try to load the filepath

        did_load = self.load_file_path(filepath)
        
        if did_load:
            self.filepath = filepath
            self.reload_config_path()
            print(f'Successfully loaded config file!\nFile Path: {self.filepath}')

        # If the filepath is corrupted, just start from scratch

        else:
            # Pseudo self.reload_config_path()
            # This must work in parallel with the actual
            config['recent_file'] = { 'path' : '' }
            with open(App.CONFIG_PATH, 'w') as config_file:
                config.write(config_file)
            print('Deleted recent_file path from config')
            self.changed = False
    
    def attempt_load(self, filepath : str):
        """
        Attempts to load the filepath.

        Rationale: Loading files may lead to an error.
            In such cases, something must still be loaded
            (it might be an empty file or the current file).
            Thus, try first to load the file.
        
        Parameter:
            1. filepath : str
                - the filepath of the file to be loaded
        
        Return Value:
            filepath : str
                - if the filepath is valid, then it is returned
            self.filepath : str
                - if the provided filepath is not valid, the 
                  current filepath is returned
        """

        did_load = self.load_file_path(filepath)
        if did_load:
            return filepath
        return self.filepath
    
    def load_file_path(self, filepath):
        """
        Loads the filepath and returns if the attempt was a success.
        
        Rationale: This is the actual "loading" in the entire loading
            process. To know whether the loading was a success, this
            must be able to cover all the possible outcomes.
        
        Current outcomes (SUCCESS?):
            - Loaded successfuly (TRUE)
            - Invalid filepath (FALSE)
            - Corrupted file (FALSE)
            - Empty filepath (TRUE)
        
        Parameter:
            1. filepath : str
                - the filepath to be loaded
        
        Return Value:
            1. Success? : boolean
                - tells whether an error occured or not.
        """

        if filepath:
            try:
                with open(filepath, 'r') as data_file:
                    data = data_file.read()
                    try:
                        save_file = json.loads(data, object_hook=self.Dialogs.decoder)
                        test_load = MetisClass()
                        test_load.reload(save_file)
                    except Exception as e:
                        messagebox.showerror(title='Error', message='File cannot be read.')
                        print(e)
                        return False
                    else:
                        self.Metis.reload(save_file)
            except FileNotFoundError:
                messagebox.showerror(title='Error', message='Invalid config filepath')
                return False

        else:
            self.Metis.reload()

        self.Secretary.reload()
        self.genres.reload()
        self.unread_ratio_reload()

        return True
    
    def reload_config_path(self):
        """
        Updates the config and the window.

        Rationale: Whenever the App changes filepath (whether
            by loading, saving, or creating a new list), the 
            window and the configurations must be updated to
            ensure an smooth user experience the next time they
            open the App.
        
        Pre-requisite:
            The App MUST have a self.filepath that reflects
            the current contents.
        """

        if self.filepath:
            self.window.title(f'{App.TITLE} - {self.filepath}')
        else:
            self.window.title(App.TITLE)

        config = configparser.ConfigParser()
        config.read(App.CONFIG_PATH)
        config['recent_file']['path'] = self.filepath
        with open(App.CONFIG_PATH, 'w') as config_file:
            config.write(config_file)
        self.changed = False
    
    def startApp(self):
        self.window.mainloop()

if __name__ == '__main__':
    app = App()
    app.startApp()