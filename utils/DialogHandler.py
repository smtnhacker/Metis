import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

import json

from utils.EntriesListHandler import EntriesListHandler
from utils.metis import MetisClass, ReadingListItem

class DialogHandler:
    """Handles the creation and management of dialog boxes."""

    def __init__(self, encoder_class, decoder_function):
        self.encoder = encoder_class
        self.decoder = decoder_function
    
    def ask_confirmation(func):
        def wrapper(*args, **kwargs):
            proceed = messagebox.askyesno(message='Unsaved progress will be lost. Do you want to continue?', icon='warning', title='New List')
            if not proceed:
                return
            return func(*args, **kwargs)
        return wrapper

    @ask_confirmation
    def cmd_load_list(self):
        "Loads a valid json file and returns the filepath and the decoded data"

        filepath = askopenfilename(
            filetypes=[('Metis Files', '*.mts'), ('All Files', '*.*')]
        )

        if not filepath:
            return None

        with open(filepath, 'r') as data_file:
            data = data_file.read()
            try:
                save_file = json.loads(data, object_hook=self.decoder)
            except Exception as e:
                messagebox.showerror(title='Error', message='Cannot read file.')
                print(e)
                return None
        
        res = {'filepath' : filepath, 'save_file' : save_file} 
        return res
        
    def cmd_save_list(self, data):
        "Creates a json file of the reading list and returns the filepath"
        filepath = asksaveasfilename(
            defaultextension='mts',
            filetypes=[('Metis Files', '*.mts'), ('All Files', '*.*')],
        )
        if not filepath:
            return
        
        filepath = self.save_file(data, filepath)
        
        return filepath
    
    def save_file(self, data, filepath):
        with open(filepath, 'w') as output_file:
            try:
                attempt_save = json.dumps(data, indent=4, cls=self.encoder)
            except Exception as e:
                print(e)
                return ''
            else:
                json.dump(data, output_file, indent=4, cls=self.encoder)
                return filepath
