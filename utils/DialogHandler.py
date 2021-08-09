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
            filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')]
        )
        if not filepath:
            return None
        with open(filepath, 'r') as data_file:
            data = data_file.read()
            try:
                collection = json.loads(data, object_hook=self.decoder)
            except Exception as e:
                messagebox.showerror(title='Error', message='Invalid file.')
                print(e)
                return None
        
        # Create a Reading List Collection (list)
        try:
            current_collection = collection[:]
        except TypeError:
            current_collection = collection['collection']
        
        res = {'filepath' : filepath, 'collection' : current_collection} 
        return res
        
    def cmd_save_list(self, data):
        "Creates a json file of the reading list and returns the filepath"
        filepath = asksaveasfilename(
            defaultextension='json',
            filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')],
        )
        if not filepath:
            return
        with open(filepath, 'w') as output_file:
            json.dump(data, output_file, indent=4, cls=self.encoder)
        
        return filepath
