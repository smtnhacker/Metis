import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class ListEntry:
    """An interactive Frame that represents a reading list item."""

    COLOR_AVAILABLE = "#e4ffbd"
    COLOR_UNAVAILABLE = "#ffbdbd"

    def __init__(self, window, toggler, master, frame, edit_reloader, gui_reload, item_delete, item):
        self.frame = frame
        self.item = item
        self.available = item.available
        self.toggler = toggler
        self.window = window
        self.master = master
        self.edit_reloader = edit_reloader
        self.gui_reload = gui_reload
        self.item_delete = item_delete
    
        # --- Create the GUI --- #

        def on_click(event):
            # Remove the toggling for now
            # self.toggler(self.item)
            # self.toggle()

            modal = EditDialog(self.frame, self.item)

            # Check if delete action should be performed
            if modal.delete:
                self.delete()
                return

            if not self.edit_reloader(self.item, modal.data):
                messagebox.showerror(message='Book entry already exists')
            else:
                self.label.config(text=self.item.format_book())
                if self.available != self.item.available:
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
    
    def delete(self):
        self.frame.destroy()
        self.gui_reload()
        self.item_delete(self.item)

class EntriesListHandler:
    """Handles the interaction between the GUI list and the actual data list"""

    def __init__(self, window, master, collection, toggler, binding, reloader, edit_reloader, deleter):
        self.item_list = dict()
        self.frame_list = dict()
        self.window = window
        self.collection = collection
        self.toggler = toggler
        self.master = master
        self.recursive_binding = binding
        self.reload_canvas = reloader
        self.edit_reloader = edit_reloader
        self.item_delete = deleter

    def load(self):
        for item in self.collection:
            self.insert(item)
    
    def unload(self):
        for item in self.frame_list.values():
            item.destroy()
        self.item_list = dict()
        self.frame_list = dict()

        self.gui_reload()

    def gui_reload(self):
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
        self.frame_list[item.get_uid()] = tk.Frame(self.master)
        self.item_list[item.get_uid()] = ListEntry(
            window=self.window, 
            toggler=self.toggler, 
            master=self.master, 
            frame=self.frame_list[item.get_uid()], 
            edit_reloader=self.edit_reloader, 
            gui_reload=self.gui_reload, 
            item_delete=self.item_delete, 
            item=item
        )

        self.window.update()

        # some shz on scrollbar
        self.recursive_binding(self.frame_list[item.get_uid()])
        self.reload_canvas()
    
    def toggle(self, item_uid):
        self.item_list[item_uid].toggle()

class AddDialog:
    """Provides an interface for handling the modal in creating a new book item."""

    def __init__(self, root, should_wait=True):
        self.data = None

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
        self.txt_summary.grid(row=4, column=1)
        
        self.frm_btn = tk.Frame(self.modal)
        self.frm_btn.pack(padx=20, pady=5)
        
        self.btn_submit = tk.Button(master=self.frm_btn, text='Submit', command=self.pre_submit)
        self.btn_submit.grid(row=0, column=0, padx=10)

        self.btn_cancel = tk.Button(master=self.frm_btn, text='Cancel', command=self.dismiss)
        self.btn_cancel.grid(row=0, column=1, padx=10)

        if should_wait:
            self.modal.wait_window()
    
    def pre_submit(self):
        "Pre-checks the information inputted before packing them in a dictionary for processing."

        # Check if there is a title
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showerror(message='You must have a title!')
            return
        
        subtitle = self.ent_subtitle.get().strip()
        author = self.ent_author.get().strip()
        date = self.ent_date.get().strip()
        summary = self.txt_summary.get("1.0", tk.END)

        data = {
            'title': title,
            'subtitle': subtitle,
            'author': author if author else 'Anonymous',
            'date': date if date else 'n.d.',
            'summary': summary,
        }

        self.submit(data)
    
    def dismiss(self):
        self.modal.grab_release()
        self.modal.destroy()
    
    def submit(self, data : dict):
        self.data = data
        self.dismiss()

class EditDialog(AddDialog):
    """Provides an interface for handling the modal of editing a list entry"""

    def __init__(self, root, item):
        super().__init__(root, should_wait=False)

        self.modal.title('Edit Entry')
        self.item = item

        # Populate the entries
        self.ent_title.insert(0, self.item.title)
        self.ent_subtitle.insert(0, self.item.subtitle)
        self.ent_author.insert(0, self.item.author)
        self.ent_date.insert(0, self.item.date)
        self.txt_summary.insert('1.0', self.item.summary[:-2])

        # Add the Availability
        self.available = tk.BooleanVar(value=self.item.available)
        self.chk_available = ttk.Checkbutton(self.frm_entries, text='Available', variable=self.available)
        self.chk_available.grid(row=5, column=1, sticky='e')

        # Add the Delete Btn
        self.delete = False

        def cmd_delete():
            self.delete = True
            self.dismiss()

        self.btn_delete = tk.Button(master=self.frm_entries, text='Delete Entry', command=cmd_delete)
        self.btn_delete.grid(row=5, column=0, padx=5, pady=5)

        self.data = {
            'title': self.item.title,
            'subtitle': self.item.subtitle,
            'author': self.item.author,
            'date': self.item.date,
            'summary': self.item.summary[:-2],
            'available': self.item.available,
        }

        self.modal.wait_window()
    
    def pre_submit(self):
        "Pre-checks the information inputted before packing them in a dictionary for processing."

        # Check if there is a title
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showerror(message='You must have a title!')
            return
        
        subtitle = self.ent_subtitle.get().strip()
        author = self.ent_author.get().strip()
        date = self.ent_date.get().strip()
        summary = self.txt_summary.get("1.0", tk.END)

        data = {
            'title': title,
            'subtitle': subtitle,
            'author': author,
            'date': date,
            'summary': summary,
            'available': self.available.get()
        }

        self.submit(data)