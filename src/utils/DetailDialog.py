"""
Detail Dialogs

Contains dialog boxes classes for maintaining ReadingListItem details.

Note: Code-splitted from EntriesListHandler.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from utils.GenreHandler import *

class AddDialog:
    """Provides an interface for handling the modal in creating a new book item."""

    def __init__(self, root, should_wait=True, attempt_submit=None, suggestions=list()):
        self.item = None
        self.attempt_submit = attempt_submit
        self.should_close = False
        self.suggestions = suggestions

        self.modal = tk.Toplevel(root)
        self.modal.title('Add a new book')
        self.modal.minsize(600, 550)
        self.modal.resizable(True, False)

        self.modal.protocol("WM_DELETE_WINDOW", self.dismiss)
        self.modal.transient(root)
        self.modal.wait_visibility()
        self.modal.grab_set()

        # ----- Add the details ----- #
        self.frm_entries = ttk.LabelFrame(self.modal, text='Details')
        self.frm_entries.pack(padx=20, pady=10, fill=tk.X)

        self.frm_entries.columnconfigure(0, minsize=50, weight=0)
        self.frm_entries.columnconfigure(1, minsize=450, weight=1)

        self.lbl_title = ttk.Label(master=self.frm_entries, text='Title')
        self.lbl_title.grid(row=0, column=0, padx=10, sticky='e')
        self.ent_title = ttk.Entry(master=self.frm_entries)
        self.ent_title.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        self.ent_title.focus()

        self.lbl_subtitle = ttk.Label(master=self.frm_entries, text='Subtitle')
        self.lbl_subtitle.grid(row=1, column=0, padx=10, sticky='e')
        self.ent_subtitle = ttk.Entry(master=self.frm_entries)
        self.ent_subtitle.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        self.lbl_author = ttk.Label(master=self.frm_entries, text='Author')
        self.lbl_author.grid(row=2, column=0, padx=10, sticky='e')
        self.ent_author = ttk.Entry(master=self.frm_entries)
        self.ent_author.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        self.lbl_date = ttk.Label(master=self.frm_entries, text='Date')
        self.lbl_date.grid(row=3, column=0, padx=10, sticky='e')
        self.ent_date = ttk.Entry(master=self.frm_entries)
        self.ent_date.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        self.lbl_summary = ttk.Label(master=self.frm_entries, text='Summary')
        self.lbl_summary.grid(row=4, column=0, padx=10, sticky='e')
        self.txt_summary = tk.Text(master=self.frm_entries, width=40, height=7)
        self.txt_summary.grid(row=4, column=1, padx=10, pady=3, sticky='ew')

        self.lbl_genres = ttk.Label(master=self.frm_entries, text='Genres')
        self.lbl_genres.grid(row=5, column=0, padx=10, sticky='e')
        self.frm_genres = ttk.Frame(master=self.frm_entries)
        self.frm_genres.grid(row=5, column=1, padx=10, pady=(5, 15), sticky='nsew')
        self.genres = GenrePacker(master=self.frm_genres, suggestions=self.suggestions)

        # ----- Add the misc ----- #

        self.frm_misc = ttk.Frame(self.modal)
        self.frm_misc.pack(padx=30, pady=0, fill=tk.X, expand=True)

        # ----- Add the Btns ----- #

        self.frm_btn = ttk.Frame(self.modal)
        self.frm_btn.pack(padx=20)
        
        self.btn_submit = ttk.Button(master=self.frm_btn, text='Submit', style='Accent.TButton', command=self.pre_submit, cursor='hand2')
        self.btn_submit.grid(row=0, column=0, padx=10, pady=(10, 20))

        self.btn_cancel = ttk.Button(master=self.frm_btn, text='Cancel', command=self.dismiss, cursor='hand2')
        self.btn_cancel.grid(row=0, column=1, padx=10, pady=(10, 20))

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

    def __init__(self, root, item, attempt_submit, suggestions):
        super().__init__(root=root, should_wait=False, attempt_submit=attempt_submit, suggestions=suggestions)

        self.modal.title('Edit Entry')
        self.item = item

        # Populate the entries
        self.ent_title.insert(0, self.item.title)
        self.ent_subtitle.insert(0, self.item.subtitle)
        self.ent_author.insert(0, self.item.author)
        self.ent_date.insert(0, self.item.date)
        self.txt_summary.insert('1.0', self.item.summary[:-2])
        self.genres.load(item.genre if item.genre != None else set())

        # Add the Misc widgets
        self.frm_misc.columnconfigure(0, weight=1)
        self.frm_misc.columnconfigure(1, weight=2)

        # Add the Availability
        self.available = tk.BooleanVar(value=self.item.available)
        self.chk_available = ttk.Checkbutton(
            self.frm_misc, text='Available', style='Switch.TCheckbutton', variable=self.available, cursor='hand2'
        )
        self.chk_available.grid(row=0, column=1, sticky='e')

        # Add the Delete Btn
        self.delete = False

        def cmd_delete():
            self.delete = True
            self.dismiss()

        self.btn_delete = ttk.Button(master=self.frm_misc, text='Delete Entry', command=cmd_delete, cursor='hand2')
        self.btn_delete.grid(row=0, column=0, padx=5, pady=5, sticky='w')

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