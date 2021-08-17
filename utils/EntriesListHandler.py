"""
Entries Handler

Contains the classes that handles the interaction
between Metis (backend) and the GUI (frontend).

Includes:
1. class EntriesListHandler - the major handler
2. class ListEntry - handler for individual entries
3. class AddDialog - handler for the add dialog box
4. class EditDialog - handler for the edit dialog box
5. class GenrePacker - handler for the genre frame
6. class GenreGUI - handler for individual genres

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

    def __init__(self, frame, on_edit, gui_reload, on_delete, on_toggle, item):
        self.frame = frame
        self.item = item
        self.available = item.available
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

            modal = EditDialog(root=self.frame, item=self.item, attempt_submit=attempt_submit)

            # Check if delete action should be performed
            if modal.delete:
                self.delete()
                return

        self.frame.config(height=25, bg=ListEntry.COLOR_AVAILABLE if self.available else ListEntry.COLOR_UNAVAILABLE)
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

        self.frm_btn = tk.Frame(master=self.frame)
        self.frm_btn.pack(side=tk.RIGHT)
        self.btn_toggle = tk.Button(master=self.frm_btn, text='TOGGLE', command=self.item_toggle)
        self.btn_toggle.grid(row=0, column=0, padx=5, pady=5)
        self.btn_delete = tk.Button(master=self.frm_btn, text='DELETE', command=self.delete)
        self.btn_delete.grid(row=0, column=1, padx=5, pady=5)
    
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
              refers to Metis' is_available method
    """

    def __init__(self, window : tk.Tk, master : tk.Frame, collection, binding, canvas_reloader, on_edit, on_delete, on_toggle, is_available):
        self.item_list = dict()
        self.frame_list = dict()

        self.window = window
        self.master = master

        self.collection = collection

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
        frm_temp = tk.Frame(self.master)
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

        self.frame_list[item.get_uid()] = tk.Frame(self.master)
        self.item_list[item.get_uid()] = ListEntry(
            frame=self.frame_list[item.get_uid()], 
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
    
class AddDialog:
    """Provides an interface for handling the modal in creating a new book item."""

    def __init__(self, root, should_wait=True, attempt_submit=None):
        self.item = None
        self.attempt_submit = attempt_submit
        self.should_close = False

        self.modal = tk.Toplevel(root)
        self.modal.title('Add a new book')
        self.modal.minsize(500, 330)
        self.modal.resizable(False, False)

        self.modal.protocol("WM_DELETE_WINDOW", self.dismiss)
        self.modal.transient(root)
        self.modal.wait_visibility()
        self.modal.grab_set()

        # --- Set-up the modal --- #
        self.frm_entries = tk.Frame(self.modal)
        self.frm_entries.pack(padx=20, pady=10)

        self.lbl_title = tk.Label(master=self.frm_entries, text='Title: ')
        self.lbl_title.grid(row=0, column=0)
        self.ent_title = tk.Entry(master=self.frm_entries)
        self.ent_title.grid(row=0, column=1, sticky='ew')
        self.ent_title.focus()

        self.lbl_subtitle = tk.Label(master=self.frm_entries, text='Subtitle: ')
        self.lbl_subtitle.grid(row=1, column=0)
        self.ent_subtitle = tk.Entry(master=self.frm_entries)
        self.ent_subtitle.grid(row=1, column=1, sticky='ew')

        self.lbl_author = tk.Label(master=self.frm_entries, text='Author')
        self.lbl_author.grid(row=2, column=0)
        self.ent_author = tk.Entry(master=self.frm_entries)
        self.ent_author.grid(row=2, column=1, sticky='ew')

        self.lbl_date = tk.Label(master=self.frm_entries, text='Date: ')
        self.lbl_date.grid(row=3, column=0)
        self.ent_date = tk.Entry(master=self.frm_entries)
        self.ent_date.grid(row=3, column=1, sticky='ew')

        self.lbl_summary = tk.Label(master=self.frm_entries, text='Summary: ')
        self.lbl_summary.grid(row=4, column=0)
        self.txt_summary = tk.Text(master=self.frm_entries, width=40, height=7)
        self.txt_summary.grid(row=4, column=1, sticky='ew')

        self.lbl_genres = tk.Label(master=self.frm_entries, text='Genres: ')
        self.lbl_genres.grid(row=5, column=0)
        self.frm_genres = tk.Frame(master=self.frm_entries)
        self.frm_genres.grid(row=5, column=1, pady=5, sticky='nsew')
        self.genres = GenrePacker(master=self.frm_genres)
        
        self.frm_btn = tk.Frame(self.modal)
        self.frm_btn.pack(padx=20, pady=5)
        
        self.btn_submit = tk.Button(master=self.frm_btn, text='Submit', command=self.pre_submit)
        self.btn_submit.grid(row=0, column=0, padx=10)

        self.btn_cancel = tk.Button(master=self.frm_btn, text='Cancel', command=self.dismiss)
        self.btn_cancel.grid(row=0, column=1, padx=10)

        if should_wait:
            self.modal.wait_window()
    
    def pre_submit(self):
        """
        Pre-checks the information inputted before packing them in a dictionary for processing.
        
        When the submission is a success, the data will merely be
        stored at self.data. Access the data manually after the modal is
        destroyed.
        """

        # Check if there is a title

        def _format(value):
            return ' '.join(value.split())

        title = _format(self.ent_title.get())
        if not title:
            messagebox.showerror(message='You must have a title!')
            return
        
        subtitle = self.ent_subtitle.get().strip()
        author = self.ent_author.get().strip()
        date = self.ent_date.get().strip()
        summary = self.txt_summary.get("1.0", tk.END)
        genre = self.genres.genres

        data = {
            'title': title,
            'subtitle': subtitle,
            'author': author if author else 'Anonymous',
            'date': date if date else 'n.d.',
            'summary': summary,
            'genre': genre
        }

        new_item = self.attempt_submit(data)
        if new_item:
            self.submit(new_item)
    
    def dismiss(self):
        self.modal.grab_release()
        self.modal.destroy()
    
    def submit(self, new_item):
        self.item = new_item
        self.dismiss()

class EditDialog(AddDialog):
    """
    Provides an interface for handling the modal of editing a list entry.
    
    Inherits from AddDialog due to similar functions. Adds the
    option of editing the availability, deleting, and making some
    of the entries empty (as opposed to having a default value).
    """

    def __init__(self, root, item, attempt_submit):
        super().__init__(root=root, should_wait=False, attempt_submit=attempt_submit)

        self.modal.title('Edit Entry')
        self.item = item

        # Populate the entries
        self.ent_title.insert(0, self.item.title)
        self.ent_subtitle.insert(0, self.item.subtitle)
        self.ent_author.insert(0, self.item.author)
        self.ent_date.insert(0, self.item.date)
        self.txt_summary.insert('1.0', self.item.summary[:-2])
        self.genres.load(item.genre if item.genre != None else set())

        # Add the Availability
        self.available = tk.BooleanVar(value=self.item.available)
        self.chk_available = ttk.Checkbutton(self.frm_entries, text='Available', variable=self.available)
        self.chk_available.grid(row=6, column=1, sticky='e')

        # Add the Delete Btn
        self.delete = False

        def cmd_delete():
            self.delete = True
            self.dismiss()

        self.btn_delete = tk.Button(master=self.frm_entries, text='Delete Entry', command=cmd_delete)
        self.btn_delete.grid(row=6, column=0, padx=5, pady=5)

        self.data = {
            'title': self.item.title,
            'subtitle': self.item.subtitle,
            'author': self.item.author,
            'date': self.item.date,
            'summary': self.item.summary[:-2],
            'available': self.item.available,
            'genre': self.item.genre.copy() if self.item.genre != None else set()
        }

        self.modal.wait_window()
    
    def pre_submit(self):
        """
        Pre-checks the information inputted before packing them in a dictionary for processing.
        
        When the submission is a success, the data will merely be
        stored at self.data. Access the data manually after the modal is
        destroyed.
        """

        # Check if there is a title
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showerror(message='You must have a title!')
            return
        
        subtitle = self.ent_subtitle.get().strip()
        author = self.ent_author.get().strip()
        date = self.ent_date.get().strip()
        summary = self.txt_summary.get("1.0", tk.END)
        genres = self.genres.genres

        data = {
            'title': title,
            'subtitle': subtitle,
            'author': author,
            'date': date,
            'summary': summary,
            'available': self.available.get(),
            'genre': genres
        }

        new_item = self.attempt_submit(data)
        if new_item:
            self.submit(new_item)

class GenreGUI:
    """
    A widget that represents a genre.
    
    Individually, GenreGUI are not connected in any way to
    the backend. These are just used to visualize genres but
    data must be handled by the parent handler.
    
    Parameters: 
        master : tkinter widget
            - the master of the GUI. Preferably, the master must
              be empty to avoid geometry manager problems.
        value 
            - the "genre" the widget represents.
        on_delete : function
            - the function to call after destroying the widget.
    """

    def __init__(self, master, value, on_delete):
        self.master = master
        self.value = value
        self.bg = '#e3eeff'
        self.on_delete = on_delete

        self.frame = tk.Frame(master=master, bg=self.bg)
        self.frame.pack(padx=2, pady=2)

        self.label = tk.Label(master=self.frame, text=value, bg=self.bg)
        self.label.pack(side=tk.LEFT, padx=4)

        self.btn_delete = tk.Button(master=self.frame, text=' x ', font=('Helvetica', 4, 'bold'), command=self.delete)
        self.btn_delete.pack(side=tk.LEFT, padx=2, fill=tk.Y)
    
    def delete(self):
        "Deletes the widget."

        self.frame.destroy()
        self.on_delete(self)

class GenrePacker:
    """
    A dynamically-resizing widget that shows the genres.

    Rationale: Tkinter has no native widget that packs widgets
        side-by-side until the maximum width is attained, after
        which a new row is created wherein the new contents will
        be packed starting there. This widget serves as that,
        with the added specific functionalities of handling
        genre data. It should be noted that a GenrePacker's use
        is flexible, so it should not be directly related to
        Metis specifically and must be a general-purpose widget.
    
    Parameters: 
        master : tk widget
            - the widget wherein the main frame of the GenrePacker
              will be packed. To avoid geometry manager problems, the
              master should be a Frame that is made specifically to
              contain the GenrePacker ONLY. It should be noted that
              the GenrePacker's width will adjust to the master.
        genres (optional) : set
            - a reference to the VALUES of the genre to be shown. 
              This means that it should NOT be a set of GenreGUI since
              GenrePacker will handle the creation of those.
        suggestions (under construction)
            - a collection of suggested values that will show when
              creating a new genre.
        on_edit (optional) : function
            - a function that will be called after a genre is created
              or deleted.
    """

    def __init__(self, master, genres=set(), suggestions=None, on_edit=None):
        self.master = master
        self.suggestions = suggestions
        self.on_edit = on_edit

        self.frame = tk.Frame(master=master, width=200)
        self.frame.pack(fill=tk.BOTH)

        self.rows = list()        
        self.genres = genres

        self.reload()

    # ----------------------------- #
    # ------ Public Methods ------- #
    # ----------------------------- #
    
    def load(self, genres):
        """
        Loads a new set of genres.

        It should be noted that once load is called, the
        previously referenced genres will remain UNMODIFIED.
        This is because, as per rationale, the widget will
        only work with data referenced from the backend. Hence,
        this will essentially cut off connection from the 
        previous set of genres and instead associate itself with
        the loaded genres. 
        """

        self.genres = genres
        self.reload()
    
    def reload(self):
        "Reloads the GUI aspect of the widget."

        for frm in self.rows:
            frm.destroy()
            self.frame.update()

        self.rows = [tk.Frame(master=self.frame)]
        self.rows[0].pack(fill=tk.X)

        for value in self.genres:
            self._insert_to_row(value)
        
        self._insert_add_btn()
        self.frame.update()
    
    def add_genre(self, value):
        """
        Adds a new genre to both the backend, and the widget.

        It should be noted that value should only be the value
        of the new genre. It must NOT be GenreGUI. 

        Pre-requisites:
            - value must NOT be in the referenced genres
        
        Result (if successful): 
            - a new GenreGUI will be created (within GenrePacker)
            - value will be added to the backend
        """

        if value in self.genres:
            messagebox.showerror(message='Genre already exists.')
            return
        self.genres.add(value)
        self._insert_to_row(value)
    
    # ------------------------------ #
    # ------ Private Methods ------- #
    # ------------------------------ #

    def _insert_to_row(self, value):
        "Dynamically adds and resizes the contents of the widget."

        while True:
            frame = tk.Frame(master=self.rows[-1])
            frame.pack(side=tk.LEFT)
            genre = GenreGUI(master=frame, value=value, on_delete=self._delete_item)
            self.frame.update()

            if self.rows[-1].winfo_reqwidth() < self.frame.winfo_width() - 10 or len(self.rows[-1].winfo_children()) == 1:
                break

            frame.destroy()
            self.frame.update()
            self.rows.append(tk.Frame(master=self.frame))
            self.rows[-1].pack(fill=tk.X)
    
    def _insert_add_btn(self):
        "Ensures that the Add Btn stays at the end of the list."

        def btn_click(value):
            self.add_genre(value)
            btn_new_genre.destroy()
            self._insert_add_btn()

            if self.on_edit:
                self.on_edit()

        while True:
            btn_new_genre = GenrePacker.AddBtn(master=self.rows[-1], text='+', on_submit=btn_click, suggestions=self.suggestions)
            btn_new_genre.pack(side=tk.LEFT)
            self.frame.update()

            if self.rows[-1].winfo_reqwidth() < self.frame.winfo_width() - 10 or len(self.rows[-1].winfo_children()) == 1:
                break

            btn_new_genre.destroy()
            self.frame.update()
            self.rows.append(tk.Frame(master=self.frame))
            self.rows[-1].pack(fill=tk.X)
        
    def _delete_item(self, item):
        "Deletes a GenreGUI (passed to and called by GenreGUI's)"
        
        item.master.destroy()
        self.genres.remove(item.value)
        del item
        if self.on_edit:
            self.on_edit()
    
    class AddBtn(tk.Button):
        def __init__(self, master, text, on_submit, suggestions):
            super().__init__(master=master, text=text)
            self.data = ''
            self.on_submit = on_submit
            self.suggestions = suggestions

            self.config(command=self.call_dialog)
        
        def call_dialog(self):
            self.modal = tk.Toplevel(self)
            self.modal.title('New Genre')
            self.modal.minsize(530, 40)
            self.modal.resizable(True, False)

            self.modal.protocol("WM_DELETE_WINDOW", self.dismiss)
            self.modal.transient(self)
            self.modal.wait_visibility()
            self.modal.grab_set()

            self.label = tk.Label(master=self.modal, text='Genre: ')
            self.label.pack(side=tk.LEFT)
            self.entry = tk.Entry(master=self.modal, width=50)
            self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entry.focus()
            self.btn_submit = tk.Button(master=self.modal, text='Submit', command=self.submit)
            self.btn_submit.pack(side=tk.RIGHT, padx=5)

            self.modal.wait_window()
        
        def dismiss(self):
            self.modal.grab_release()
            self.modal.destroy()
        
        def submit(self):
            if self.entry.get().split():
                self.data = self._get_data(self.entry.get())
                self.on_submit(self.data)
            self.dismiss()
        
        def _get_data(self, value):
            return ' '.join(x.capitalize() for x in value.split())
