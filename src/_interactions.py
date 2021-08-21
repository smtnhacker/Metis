"""
Interactions

Contains the interactions and logic-related
methods and variables for the App class
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import json
import configparser

# import local modules
from utils.metis import *
from utils.EntriesListHandler import *
from utils.FileDialogHandler import *
from utils.DetailDialog import *
from utils.GenreHandler import *
from utils.SaveFile import *

# --------------------------------------------------- #
# ------------- HANDLE THE INTERACTIONS ------------- #
# --------------------------------------------------- #

def initialize_interactions(self):

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
        binding=self.recursive_binding, 
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

    self.genres = GenrePacker(
        master=self.frm_genres, 
        genres=self.Metis.filter, 
        suggestions=self.Metis.available_genres, # Should serve to show the current genres in the App
        on_edit=self.onGenreEdit,
    )

    # ----- Set up name filtering ----- #

    self.var_search_text = tk.StringVar()
    self.var_search_text.trace('w', self.onSearchKeyPress)
    self.ent_search.config(textvariable=self.var_search_text)

# -------------------------------------------------- #
# --------------- EVENTS METHODS ------------------- #
# -------------------------------------------------- #

def onGenreEdit(self):
    "Whenever the GenrePacker updates the genres, the App must also be updated."

    self.Metis.reload_available()
    self.Secretary.reload()
    self.unread_ratio_reload()

def onSearchKeyPress(self, *args):
    text = self.ent_search.get()
    self.Metis.search_filter = text
    self.Metis.reload_available()
    self.Secretary.reload()
    self.unread_ratio_reload()

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