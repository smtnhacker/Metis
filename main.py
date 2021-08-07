import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

from utils.metis import MetisClass, ReadingListItem
from utils.EntriesListHandler import *
from utils.DialogHandler import *

class App:
    """A class that handles the overall operation of the Metis program."""

    def __init__(self):

        # ----- Initialize the Window ----- #

        self.window = tk.Tk()
        self.window.title('Metis')
        self.window.minsize(width=920, height=400)
        self.window.rowconfigure(0, minsize=100, weight=0)
        self.window.rowconfigure(1, minsize=300, weight=1)
        self.window.columnconfigure(0, minsize=500, weight=1)

        # ------ Initialize Metis ----- #

        self.Metis = MetisClass()

        # ----------------------------------------------- #
        # ------------- GUI INITIALIZATION -------------- #
        # ----------------------------------------------- #

        # ----- Set-up the Request GUI ----- #

        self.frm_main = tk.Frame(self.window)
        self.frm_main.grid(row=0, column=0)

        def request_book():
            "Requests a title (string) from Metis"

            requested_title = self.Metis.request_book()
            self.ent_book_given.delete(0, tk.END)
            self.ent_book_given.insert(0, requested_title)

            # Show in the GUI that the chosen book is not unavailable
            if requested_title != 'No book available':
                self.Secretary.toggle(requested_title)

        self.btn_request_book = tk.Button(
            master=self.frm_main,
            text="Click to request for a book",
            width=25,
            command=request_book
        )
        self.btn_request_book.grid(row=0, column=0, padx=10, pady=10)

        self.ent_book_given = tk.Entry(master=self.frm_main,)
        self.ent_book_given.bind("<Key>", lambda e : "break") # To make the Entry read-only
        self.ent_book_given.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky='ew')

        # ----- Create a Scrollable Canvas ----- #

        self.frm_list = tk.Frame(master=self.window)
        self.frm_list.grid(row=1, column=0, padx=20, pady=20, sticky='nsew')
        self.frm_list.columnconfigure(0, minsize=400, weight=1)
        self.frm_list.rowconfigure(0, minsize=400, weight=1)

        # Create a canvas to draw things on
        self.canvas_list = tk.Canvas(self.frm_list)
        self.canvas_list.grid(row=0, column=0, sticky='nsew')

        # Create the scrollbar
        self.scrollbar = ttk.Scrollbar(self.frm_list, orient=tk.VERTICAL, command=self.canvas_list.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.scrollbar.grid_remove()

        # Configure the canvas
        self.SCROLLABLE = False

        def check_scrollbar_visibility():
            "Hides / Unhides the scrollbar when necessary"
            minHeight = self.frm_container.winfo_reqheight()

            if self.canvas_list.winfo_height() >= minHeight:
                self.scrollbar.grid_remove()
                self.SCROLLABLE = False
            else:
                self.scrollbar.grid(row=0, column=1, sticky='nsew')
                self.SCROLLABLE = True

        def onCanvasConfigure(event):
            self.canvas_list.configure(scrollregion = self.canvas_list.bbox('all'))
            self.canvas_list.itemconfig('frame', width=self.canvas_list.winfo_width())

        self.canvas_list.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_list.bind('<Configure>', onCanvasConfigure)

        self.frm_container = tk.Frame(self.canvas_list)
        self.canvas_list.create_window((0,0), width=self.canvas_list.winfo_reqwidth(), window=self.frm_container, anchor='nw', tags='frame')

        # Make it scrollable using the mousewheel

        def on_mouse_wheel(event):
            if self.SCROLLABLE:
                self.canvas_list.yview_scroll(-1 * int((event.delta / 120)), 'units')

        def recursive_binding(w):
            "Recursion to bind a widget and all its children to be scrollable"

            w.bind('<MouseWheel>', on_mouse_wheel)
            for child in w.winfo_children():
                recursive_binding(child)

        def reload_canvas():
            "Re-calibrates the canvas to update the scrollbar"

            self.scrollbar.grid(row=0, column=1, sticky='nsew')
            self.canvas_list.configure(scrollregion=self.canvas_list.bbox('all'))
            self.canvas_list.config(yscrollcommand=self.scrollbar.set)
            check_scrollbar_visibility()

        self.canvas_list.bind('<MouseWheel>', on_mouse_wheel)
        self.frm_container.bind('<MouseWheel>', on_mouse_wheel)

        # ----- Create the File Handling Buttons ----- #

        self.btn_new_list = tk.Button(master=self.frm_main, text="New List", width=25)
        self.btn_new_list.grid(row=1, column=0, padx=10, pady=5)

        self.btn_load_list = tk.Button(master=self.frm_main, text="Load List", width=25)
        self.btn_load_list.grid(row=1, column=1, padx=10, pady=5)

        self.btn_save_list = tk.Button(master=self.frm_main, text="Save List", width=25)
        self.btn_save_list.grid(row=1, column=2, padx=10, pady=5)

        # ----- Create the Add Book Buttons ----- #

        self.btn_add_book = tk.Button(master=self.frm_main, text="Add Book", width=25)
        self.btn_add_book.grid(row=1, column=3, padx=10, pady=5)

        # --------------------------------------------------- #
        # ------------- HANDLE THE INTERACTIONS ------------- #
        # --------------------------------------------------- #

        # ----- Set-up the Reading List Backend ----- #

        self.Secretary = EntriesListHandler(
                        window=self.window, 
                        Metis=self.Metis, 
                        master=self.frm_container, 
                        binding=recursive_binding, 
                        reloader=reload_canvas
                    )

        # ----- Set up the File Handling Dialog Boxes ----- #

        self.Dialogs = DialogHandler(
                    self.Metis, 
                    self.Secretary, 
                    new_list_btn=self.btn_new_list, 
                    save_list_btn=self.btn_save_list, 
                    load_list_btn=self.btn_load_list
                )

        # ----- Setup Add Book Modal ----- #

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

        def CallCreateDialog():
            "Creates a dialog box for adding a new book entry"

            modal = AddDialog(self.window)

            # Verify if there is data
            if not modal.data:
                return

            # Verify if the book already exists
            new_item = self.Metis.insert_item(modal.data)
            if not new_item:
                messagebox.showerror(message='Book already exists.')
            else:
                self.Secretary.insert(new_item)

        self.btn_add_book.config(command=CallCreateDialog)

        # ----- Place this portion at the end of the program ----- #
        self.window.mainloop()

if __name__ == '__main__':
    app = App()