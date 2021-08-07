import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

import json

from utils.EntriesListHandler import EntriesListHandler
from utils.metis import MetisClass, ReadingListItem

class DialogHandler:
    """Handles the creation and management of dialog boxes."""

    def __init__(self, Metis : MetisClass, Secretary : EntriesListHandler, **kwargs):
        self.Metis = Metis
        self.Secretary = Secretary
        
        # Setup the New List Button
        self.new_list_btn = kwargs.get('new_list_btn')
        if self.new_list_btn:
            self.new_list_btn.config(command=self.cmd_new_list)
        
        # Setup the Save List Button
        self.save_list_btn = kwargs.get('save_list_btn')
        if self.save_list_btn:
            self.save_list_btn.config(command=self.cmd_save_list)
        
        #Setup the Load List Button
        self.load_list_btn = kwargs.get('load_list_btn')
        if self.load_list_btn:
            self.load_list_btn.config(command=self.cmd_load_list)
            
    @staticmethod
    def decode_collection(dct):
        "A custom decoder for decoding Reading List specific data"

        if '__ReadingListItem__' in dct:
            return  ReadingListItem(**{key : value for key, value in dct.items() if key != '__ReadingListItem__'})
        else:
            return dct

    class CollectionEncoder(json.JSONEncoder):
        "Extends the JSONEncoder to include encoding Reading Lists"

        def default(self, dct):
            if isinstance(dct, ReadingListItem):
                res = { '__ReadingListItem__' : True }
                for key, value in dct.__dict__.items():
                    res[key] = value
                return res
            else:
                return super().default(dct)

    def ask_confirmation(func):
        def wrapper(self):
            proceed = messagebox.askyesno(message='Unsaved progress will be lost. Do you want to continue?', icon='warning', title='New List')
            if not proceed:
                return
            func(self)
        return wrapper

    @ask_confirmation
    def cmd_new_list(self):
        self.Metis.reload()
        self.Secretary.reload()

    @ask_confirmation
    def cmd_load_list(self):
        filepath = askopenfilename(
            filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')]
        )
        if not filepath:
            return None
        with open(filepath, 'r') as data_file:
            data = data_file.read()
            try:
                collection = json.loads(data, object_hook=self.decode_collection)
            except ValueError as e:
                messagebox.showerror(title='Error', message='Invalid file.')
                print(e)
                return None
        
        # Create a Reading List Collection (list)
        try:
            current_collection = collection[:]
        except TypeError:
            current_collection = collection['collection']

        self.Metis.reload(current_collection)
        self.Secretary.reload()

    def cmd_save_list(self):
        filepath = asksaveasfilename(
            defaultextension='json',
            filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')],
        )
        if not filepath:
            return
        with open(filepath, 'w') as output_file:
            json.dump(self.Metis.collection, output_file, indent=4, cls=self.CollectionEncoder)

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
