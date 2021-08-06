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
        if '__ReadingListItem__' in dct:
            return  ReadingListItem(**{key : value for key, value in dct.items() if key != '__ReadingListItem__'})
        else:
            return dct

    class CollectionEncoder(json.JSONEncoder):
        def default(self, dct):
            if isinstance(dct, ReadingListItem):
                res = { '__ReadingListItem__' : True }
                for key, value in dct.__dict__.items():
                    res[key] = value
                return res
            else:
                return super().default(dct)


    def cmd_new_list(self):
        self.Metis.reload()
        self.Secretary.reload()

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