"""
Entries Handler

Contains the classes that handles the interaction
between Metis (backend) and the GUI (frontend).

Includes:
1. class EntriesListHandler - the major handler
2. class ListEntry - handler for individual entries

Rationale: 
    To properly modularize the project, the back-end
    and front-end must be, as much as possible, independent
    from each other. The classes here serve as the 
    FRONTEND handlers that uses data from the
    back-end to create the necessary GUI.

    As much as possible, classes here MUST NOT store
    their own data, unless that data is something simple
    like a string or ReadingListItem. Instead, they should
    reference from the back-end and reload instead.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from utils.DetailDialog import *
from utils.GenreHandler import *

class ListEntry:
    """
    An interactive Frame that represents a reading list item.
    
    The ListEntry serves as the class that creates an individual
    item in the scrollable reading list, and maintains the methods
    that specifically modifies the specific item.

    Rationale: Each method must be localized as much as possible.
        ALL changes in a specific ReadingListItem must pass
        through its corresponding ListEntry. However,
        it should be noted that if there is a method that
        modifies both the GUI and Metis, Metis will be the
        independent one.

    Life Cycle:
        Whenever a new ReadingListItem is created,
        the item is passed to the EntriesListHandler. 
        There, a ListEntry is created. 

        Whenever the an item is up for the deletion,
        the ListEntry initiates its deletion by first
        destroying the GUI, the reference in the parent,
        and then calling the delete function provided by
        the back-end.
    
    Parameters:
        frame : tk.Frame
            - refers to the parent frame. This will be created by 
              the parent handler
        item : ReadingListItem
            - the entry that the ListEntry represents
        on_edit : function
            - function to call after an edit has been made. Preferably,
              this refers to Metis' edit command
        on_delete : function
            - function to call after a delete has been made. Preferable,
              this refers to Metis' delete command
        gui_reload : function
            - function that reloads the parent handler's GUI. Only
              used to correct some annoying technicalities
    """

    COLOR_AVAILABLE = "#e4ffbd"
    COLOR_UNAVAILABLE = "#ffbdbd"
    COLOR_HOVER_AVAILABLE = "#ccecff"
    COLOR_HOVER_UNAVAILABLE = "#ffdbcc"

    def __init__(self, frame, genre_suggestions, on_edit, gui_reload, on_delete, on_toggle, item):
        self.frame = frame
        self.item = item
        self.available = item.available
        self.genre_suggestions = genre_suggestions
        self.on_edit = on_edit
        self.gui_reload = gui_reload
        self.on_delete = on_delete
        self.on_toggle = on_toggle
    
        # --- Create the GUI --- #

        def on_click(event):
            """
            Current function of clicking: Edit the entry.
            """
            
            def attempt_submit(data):
                if not self.on_edit(self.item, data):
                    messagebox.showerror(message='Book entry already exists')
                else:
                    self.label.config(text=self.item.format_book())
                    if self.available != self.item.available:
                        self.toggle()
                    return self.item

            modal = EditDialog(root=self.frame, item=self.item, attempt_submit=attempt_submit, suggestions=self.genre_suggestions)

            # Check if delete action should be performed
            if modal.delete:
                self.delete()
                return

        self.frame.config(height=40, background=ListEntry.COLOR_AVAILABLE if self.available else ListEntry.COLOR_UNAVAILABLE)
        self.frame.bind("<Button-1>", on_click)
        self.frame.bind("<Enter>", self._on_enter)
        self.frame.bind("<Leave>", self._on_leave)
        self.frame.pack(fill=tk.X, padx=10, pady=5)

        self.label = tk.Label(master=self.frame, text=self.item.format_book(), background=self.frame['bg'], width=80)
        self.label.bind("<Button-1>", on_click)
        self.label.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    
    def toggle(self):
        """
        Toggles ONLY the GUI aspect of the entry.
        
        Rationale: It is possible that an item will be
            toggled through another means. As such, the
            burden of adjusting will be carried by the GUI
            and the toggle must only affect the GUI.
        """

        self.available = not self.available
        self.frame.config(bg=ListEntry.COLOR_AVAILABLE if self.available else ListEntry.COLOR_UNAVAILABLE)
        self.label.config(bg=self.frame['bg'])
    
    def item_toggle(self):
        """
        Toggles both the GUI and the backend aspect of the entry.

        Rationale: It is possible that the item will be toggled
            through GUI. This function serves to make that function
            clear-cut.
        """
        self.toggle()
        self.on_toggle(self.item)
    
    def delete(self):
        "Deletes the GUI first and calls for its item to be deleted backend afterwards."

        self.frame.destroy()
        self.gui_reload()
        self.on_delete(self.item)

    def _on_enter(self, event):
        self.label.config(text=f'Edit "{self.item.format_book()}"?')

        self.frm_btn = ttk.Frame(master=self.frame)
        self.frm_btn.pack(side=tk.RIGHT)
        self.btn_toggle = ttk.Button(master=self.frm_btn, text='TOGGLE', command=self.item_toggle, cursor='hand2')
        self.btn_toggle.grid(row=0, column=0, padx=5)
        self.btn_delete = ttk.Button(master=self.frm_btn, text='DELETE', command=self.delete, cursor='hand2')
        self.btn_delete.grid(row=0, column=1, padx=5)
    
    def _on_leave(self, event):
        self.label.config(text=self.item.format_book())
        self.frm_btn.destroy()

class EntriesListHandler:
    """
    Handles the interaction between the GUI list and the actual data list.
    
    Provides the main interface for handling interaction between the
    back-end (Metis) and the GUI, which the class itself handles.

    Rationale: In juggling the data and interaction, the idea is
        that this class will handle most of the heavier and dirtier
        burden. To implement such a framework, Metis will provide
        the methods in modifying the data (at the back-end side),
        the EntriesListHandler (or Secretary), will provide those
        methods to the specific components that will need them.
    
    Parameters:
        window : tk.Tk
            - refers to the root of the application
        master : tk.Frame
            - the parent frame of the reading list GUI
        collection
            - reference to the backend collections
        genre_suggestions
            - reference to the current genre collection
        binding : function
            - function for recursive binding to give every widget 
              a particular property
        canvas_reloader : function
            - an annoying, but necessary function to force update 
              the scrollbar
        on_edit : function
            - function to call whenever an entry is updated. 
              Preferably, on_edit refers to Metis' edit command
        on_delete : function
            - function to call whenever an entry is deleted. 
              Preferably, on_delete refers to Metis' delete command
        is_available : function
            - boolean function that takes in item and returns 
              whether the item is available or not. Preferable, is_available
              refers to Metis' is_showable method
    """

    def __init__(self, window : tk.Tk, master : ttk.Frame, collection, genre_suggestions, binding, canvas_reloader, on_edit, on_delete, on_toggle, is_available):
        self.item_list = dict()
        self.frame_list = dict()

        self.window = window
        self.master = master

        self.collection = collection
        self.genre_suggestions = genre_suggestions

        self.recursive_binding = binding
        self.reload_canvas = canvas_reloader
        self.is_available = is_available

        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle = on_toggle

    def load(self):
        """
        Loads the items that are available.

        Rationale: The data must be referenced directly from
            the backend as much as possible to avoid inconsistencies.
            As such, loading must as independent as possible, which
            means that as long as the pre-requisites are met, 
            no error must occur regarding the data. Also, self.load
            must have NO strange behavior under any circumstances
            to ensure that methods that call self.load work as expected.

        Pre-requisites:
            - self.frame_list must be empty
            - self.item_list must be empty
            - self.collection reflects the current data
            - self.is_available reflects the current filter function
        """
        
        for item in filter(self.is_available, self.collection):
            self.insert(item)
    
    def unload(self):
        """
        Deletes all the GUI aspect of the entries.
        
        Rationale: Unload basically resets the EntryListHandler
            to a fresh state. As such, no unnecessary data must
            be left after calling self.unload. This is to ensure
            that other methods that call self.unload work as expected.
        """

        for item in self.frame_list.values():
            item.destroy()
        self.item_list = dict()
        self.frame_list = dict()
        self.gui_reload()

    def gui_reload(self):
        "Some annoying GUI technicalities to force a redrawing."

        # Some GUI techninal sht
        frm_temp = ttk.Frame(self.master)
        frm_temp.pack()
        self.window.update()
        frm_temp.destroy()
        self.window.update()
        self.window.update_idletasks()
        self.reload_canvas()
    
    def reload(self):
        """
        Reloads and recreates the GUI-aspect of the entries.

        Rationale: Whenever the data is manipulated on a collective
            level, it is better for the GUI to reload instead of
            updating each one of the entries. As much as possible,
            rely on the independency of self.unload and self.load.
        """
        
        self.unload()
        self.load()

    def insert(self, item):
        "Creates and inserts a ListEntry based on the item."

        self.frame_list[item.get_uid()] = tk.Frame(self.master, cursor='hand2')
        self.item_list[item.get_uid()] = ListEntry(
            frame=self.frame_list[item.get_uid()], 
            genre_suggestions=self.genre_suggestions,
            on_edit=self.on_edit, 
            gui_reload=self.gui_reload, 
            on_delete=self.delete, 
            on_toggle=self.on_toggle,
            item=item
        )

        self.window.update()

        # some shz on scrollbar
        self.recursive_binding(self.frame_list[item.get_uid()])
        self.reload_canvas()
    
    def delete(self, item):
        """
        Deletes a specific item.

        Rationale: Whenever deleting, always delete
            the GUI first, before destroying the data
            from the backend. Also, make sure that delete
            methods are localized as much as possible to
            avoid dangling data.
        
        Pre-requisites:
            - the item must still be present at the backend
        
        Result: 
            - the GUI will be destroyed (non-reversable)
            - the item will be deleted from the backend (non-reversable)
        """

        del self.frame_list[item.get_uid()]
        del self.item_list[item.get_uid()]
        self.on_delete(item)
    
    def toggle(self, item_uid):
        "An intermediary method for toggling."

        self.item_list[item_uid].toggle()
    
