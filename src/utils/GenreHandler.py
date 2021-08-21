"""
Genre Handlers

Contains methods for handling genres.

Note: Code-splitted from EntriesListHandler
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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

        self.frame = ttk.Frame(master=master, width=200)
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

        self.rows = [ttk.Frame(master=self.frame)]
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
            frame = ttk.Frame(master=self.rows[-1])
            frame.pack(side=tk.LEFT)
            genre = GenreGUI(master=frame, value=value, on_delete=self._delete_item)
            self.frame.update()

            if self.rows[-1].winfo_reqwidth() < self.frame.winfo_width() - 10 or len(self.rows[-1].winfo_children()) == 1:
                break

            frame.destroy()
            self.frame.update()
            self.rows.append(ttk.Frame(master=self.frame))
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
            btn_new_genre = GenrePacker.AddBtn(master=self.rows[-1], text='+', on_submit=btn_click, suggestions=self.suggestions, current_genres=self.genres)
            btn_new_genre.pack(side=tk.LEFT)
            self.frame.update()

            if self.rows[-1].winfo_reqwidth() < self.frame.winfo_width() - 10 or len(self.rows[-1].winfo_children()) == 1:
                break

            btn_new_genre.destroy()
            self.frame.update()
            self.rows.append(ttk.Frame(master=self.frame))
            self.rows[-1].pack(fill=tk.X)
        
    def _delete_item(self, item):
        "Deletes a GenreGUI (passed to and called by GenreGUI's)"
        
        item.master.destroy()
        self.genres.remove(item.value)
        del item
        if self.on_edit:
            self.on_edit()
    
    class AddBtn(ttk.Button):
        def __init__(self, master, text, on_submit, suggestions=set(), current_genres=set()):
            super().__init__(master=master, text=text, cursor='hand2')
            self.data = ''
            self.on_submit = on_submit
            self.suggestions = suggestions
            self.current_genres = current_genres

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

            self.modal.columnconfigure(1, weight=1)

            # Insert the label
            self.label = ttk.Label(master=self.modal, text='Genre: ')
            self.label.grid(row=0, column=0)

            # Insert the entry box
            self.entry = ttk.Entry(master=self.modal, width=50)
            self.entry.grid(row=0, column=1, sticky='ew')
            self.entry.focus()

            # Insert the submit button
            self.btn_submit = ttk.Button(master=self.modal, text='Submit', command=self.submit, cursor='hand2')
            self.btn_submit.grid(row=0, column=2, padx=5)

            # Insert Suggestions

            self.temp_suggestions = sorted(filter(lambda x : x not in self.current_genres, self.suggestions))
            def on_key_press(*args, **kwargs):
                text = self.entry.get()
                self.temp_suggestions = sorted(filter(lambda x : text in x and x not in self.current_genres, self.suggestions))
                self.suggestionsVar.set(self.temp_suggestions)
                self.modal.update()
            
            def on_d_press(event):
                index = self.lst_suggestions.curselection()[0]
                value = self.temp_suggestions[index]
                self.entry.delete(0, tk.END)
                self.entry.insert(0, value)
                self.submit()

            self.suggestionsVar = tk.StringVar(value=self.temp_suggestions)
            self.lst_suggestions = tk.Listbox(master=self.modal, listvariable=self.suggestionsVar, height=3)
            self.lst_suggestions.grid(row=1, column=1, sticky='ew', pady=7)

            # Set-up suggestions
            var_text = tk.StringVar()
            var_text.trace('w', on_key_press)
            self.entry.config(textvariable=var_text)
            self.lst_suggestions.bind('<Double-1>', on_d_press)

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

        self.btn_delete = ttk.Button(master=self.frame, text=' x ', command=self.delete, cursor='hand2')
        self.btn_delete.pack(side=tk.LEFT, padx=2, fill=tk.Y)
    
    def delete(self):
        "Deletes the widget."

        self.frame.destroy()
        self.on_delete(self)
