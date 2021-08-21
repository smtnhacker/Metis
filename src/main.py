# # -------------------------------- #
#        Metis - Reading Guide
#        By Something_Hacker
# # -------------------------------- #
#
# Rationale:
#   When one has an ever growing reading list, 
#   it is not surprising to find oneself in a
#   state of choice paralysis. As such, it
#   might be useful to leave the dilemma of
#   choosing to something cold and calculating,
#   AKA, a program.
# 
# Description:
#   Metis is a simple program that lets the user
#   create, edit, and save reading lists. Upon
#   the user's request, Metis will provide a book.
#   To improve the reading experience, the genre
#   of the provided book will vary as much as possible.
#
# # -------------------------------------------------- # #

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import json
import configparser

# import local modules
from utils.metis import MetisClass

# import App extension modules
import _gui
import _interactions

class App:
    """A class that handles the overall operation of the Metis program."""

    TITLE = 'Metis'
    CONFIG_PATH = 'config.ini'

    def __init__(self):
        """
        Initializes the App.
        """
        
        # load imported methods
        self.loadModule(_gui)
        self.loadModule(_interactions)

        self.filepath = ''
        self.changed = False    # False at start and after reloading config (save as, load, new) and save
                                # Not yet used, too hassle to implement smh

        # ------ Initialize the App ----- #

        self.Metis = MetisClass()
        self.initialize_gui()
        self.initialize_interactions()

        # ----- Load the config file ----- #

        self.loadApp()
    
    def loadModule(self, module):
        """
        Loads methods from an external module.

        Rationale: The GUI and interactions have been
            separated from the main App to make them more
            independent and easier to edit. However, since
            they are part of one App, they access each other.
            Hence, they must still be part of the App class.
        """

        for name, func in module.__dict__.items():
            if callable(func):
                setattr(self.__class__, name, func)

    def loadApp(self):
        """
        Sets up the windows and the App configurations.

        Rationale: At the beginning of the App, the configurations
            must be loaded. This includes loading the previously
            used reading list to provide ease of experience for the
            user. 

            It might be possible that the config file is corrupted,
            and if such occurs, the App MUST still load, albeit empty
            and the config file should be fixed.
        """

        # Load the config file

        config = configparser.ConfigParser()
        try:
            config.read(App.CONFIG_PATH)
            filepath = config['recent_file']['path']
        
        # In the case that the config file is corrupted,
        # correct the file

        except Exception as e:
            config['recent_file'] = { 'path' : '' }
            filepath = ''
            with open(App.CONFIG_PATH, 'w') as config_file:
                config.write(config_file)
            print('Successfully created config file!')

        # Try to load the filepath

        did_load = self.load_file_path(filepath)
        
        if did_load:
            self.filepath = filepath
            self.reload_config_path()
            print(f'Successfully loaded config file!\nFile Path: {self.filepath}')

        # If the filepath is corrupted, just start from scratch

        else:
            # Pseudo self.reload_config_path()
            # This must work in parallel with the actual
            config['recent_file'] = { 'path' : '' }
            with open(App.CONFIG_PATH, 'w') as config_file:
                config.write(config_file)
            print('Deleted recent_file path from config')
            self.changed = False
    
    def attempt_load(self, filepath : str):
        """
        Attempts to load the filepath.

        Rationale: Loading files may lead to an error.
            In such cases, something must still be loaded
            (it might be an empty file or the current file).
            Thus, try first to load the file.
        
        Parameter:
            1. filepath : str
                - the filepath of the file to be loaded
        
        Return Value:
            filepath : str
                - if the filepath is valid, then it is returned
            self.filepath : str
                - if the provided filepath is not valid, the 
                  current filepath is returned
        """

        did_load = self.load_file_path(filepath)
        if did_load:
            return filepath
        return self.filepath
    
    def load_file_path(self, filepath):
        """
        Loads the filepath and returns if the attempt was a success.
        
        Rationale: This is the actual "loading" in the entire loading
            process. To know whether the loading was a success, this
            must be able to cover all the possible outcomes.
        
        Current outcomes (SUCCESS?):
            - Loaded successfuly (TRUE)
            - Invalid filepath (FALSE)
            - Corrupted file (FALSE)
            - Empty filepath (TRUE)
        
        Parameter:
            1. filepath : str
                - the filepath to be loaded
        
        Return Value:
            1. Success? : boolean
                - tells whether an error occured or not.
        """

        if filepath:
            try:
                with open(filepath, 'r') as data_file:
                    data = data_file.read()
                    try:
                        save_file = json.loads(data, object_hook=self.Dialogs.decoder)
                        test_load = MetisClass()
                        test_load.reload(save_file)
                    except Exception as e:
                        messagebox.showerror(title='Error', message='File cannot be read.')
                        print(e)
                        return False
                    else:
                        self.Metis.reload(save_file)
            except FileNotFoundError:
                messagebox.showerror(title='Error', message='Invalid config filepath')
                return False

        else:
            self.Metis.reload()

        self.Secretary.reload()
        self.genres.reload()
        self.unread_ratio_reload()

        return True
    
    def reload_config_path(self):
        """
        Updates the config and the window.

        Rationale: Whenever the App changes filepath (whether
            by loading, saving, or creating a new list), the 
            window and the configurations must be updated to
            ensure an smooth user experience the next time they
            open the App.
        
        Pre-requisite:
            The App MUST have a self.filepath that reflects
            the current contents.
        """

        if self.filepath:
            self.window.title(f'{App.TITLE} - {self.filepath}')
        else:
            self.window.title(App.TITLE)

        config = configparser.ConfigParser()
        config.read(App.CONFIG_PATH)
        config['recent_file']['path'] = self.filepath
        with open(App.CONFIG_PATH, 'w') as config_file:
            config.write(config_file)
        self.changed = False
    
    def startApp(self):
        self.window.mainloop()

if __name__ == '__main__':
    app = App()
    app.startApp()