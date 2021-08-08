import tkinter as tk

class ListEntry:
    """An interactive Frame that represents a reading list item."""

    COLOR_AVAILABLE = "#e4ffbd"
    COLOR_UNAVAILABLE = "#ffbdbd"

    def __init__(self, window, toggler, master, frame, item):
        self.frame = frame
        self.item = item
        self.available = item.available
        self.toggler = toggler
        self.window = window
        self.master = master
    
        # --- Create the GUI --- #

        def on_click(event):
            self.toggler(self.item)
            self.toggle()

        self.frame.config(height=25, bg=ListEntry.COLOR_AVAILABLE if self.available else ListEntry.COLOR_UNAVAILABLE)
        self.frame.bind("<Button-1>", on_click)
        self.frame.pack(fill=tk.X, padx=10, pady=5)

        self.label = tk.Label(master=self.frame, text=self.item.format_book(), background=self.frame['bg'])
        self.label.bind("<Button-1>", on_click)
        self.label.pack(padx=5, pady=5)
    
    def toggle(self):
        self.available = not self.available
        self.frame.config(bg=ListEntry.COLOR_AVAILABLE if self.available else ListEntry.COLOR_UNAVAILABLE)
        self.label.config(background=self.frame['bg'])

class EntriesListHandler:
    """Handles the interaction between the GUI list and the actual data list"""

    def __init__(self, window, master, collection, toggler, binding, reloader):
        self.item_list = dict()
        self.frame_list = dict()
        self.window = window
        self.collection = collection
        self.toggler = toggler
        self.master = master
        self.recursive_binding = binding
        self.reload_canvas = reloader

    def load(self):
        for item in self.collection:
            self.insert(item)
    
    def unload(self):
        for item in self.frame_list.values():
            item.destroy()
        self.item_list = dict()
        self.frame_list = dict()

        # Some GUI techninal sht
        frm_temp = tk.Frame(self.master)
        frm_temp.pack()
        self.window.update()
        frm_temp.destroy()
        self.window.update()
        self.window.update_idletasks()
        self.reload_canvas()
    
    def reload(self):
        self.unload()
        self.load()
    
    def insert(self, item):
        self.frame_list[item.format_book()] = tk.Frame(self.master)
        self.item_list[item.format_book()] = ListEntry(
            window=self.window, 
            toggler=self.toggler, 
            master=self.master, 
            frame=self.frame_list[item.format_book()], 
            item=item
        )

        self.window.update()

        # some shz on scrollbar
        self.recursive_binding(self.frame_list[item.format_book()])
        self.reload_canvas()
    
    def toggle(self, item_name):
        self.item_list[item_name].toggle()