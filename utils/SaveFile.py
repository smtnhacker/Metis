"""
Save File

Contains class for saving the reading list.

Note: Code-splitted from metis.py
"""

from collections import deque
import json

from utils.ReadingListItem import *

class SaveFile:
    "Handles the data to be used in saving / loading."

    def __init__(self, **kwargs):
        self.collection = kwargs.pop('collection', dict())
        self.recently_read = kwargs.pop('recently_read', deque())
        self.filter = kwargs.pop('filter', set())

    # ------------------------------------------ #
    # --------- For JSON Conversion ------------ #
    # ------------------------------------------ #
        
    @staticmethod
    def decode_collection(dct):
        "A custom decoder for decoding the specific a SaveFile"

        if '__SaveFile__' in dct:
            return SaveFile(**{key : value for key, value in dct.items() if key != '__SaveFile__'})
        if '__ReadingListItem__' in dct:
            return  ReadingListItem(**{key : value for key, value in dct.items() if key != '__ReadingListItem__'})
        else:
            return dct

    class CollectionEncoder(json.JSONEncoder):
        "Extends the JSONEncoder to include encoding SaveFiles"

        def default(self, dct):
            if isinstance(dct, SaveFile):
                res = { '__SaveFile__' : True }
                for key, value in dct.__dict__.items():
                    if type(value) in {set, deque}:
                        res[key] = list(value)
                    else:
                        res[key] = value
                return res
            elif isinstance(dct, ReadingListItem):
                res = { '__ReadingListItem__' : True }
                for key, value in dct.__dict__.items():
                    if type(value) == set:
                        res[key] = list(value)
                    else:
                        res[key] = value
                return res
            else:
                return super().default(dct)
