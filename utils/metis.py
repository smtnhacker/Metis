"""
Metis

Contains the classes that handles the backend of 
the application.

Includes:
1. class MetisClass - the main backend
2. class ReadingListItem - represents an entry
3. class SaveFile - represents the current state (to be used in saving)

Rationale: 
    To reduce any inconsistencies, the application
    shall maintain a independent backend and a 
    frontend that references data directly from
    the backend, which is the MetisClass. Therefore,
    any collection and method here should be as 
    independent as possible, and re-referencing 
    should be avoided, excluding at initialization.
"""

from collections import deque
import random
import json

class ReadingListItem:
    """
    Describes a book to read.
    
    Rationale: A book has no method. It
        merely has facts. Do not place any
        instance method.

    Warning: Changes to the instance may
        result to an incompatible save file.
        Therefore, avoid editing this unless
        completely necessary!
    """

    def __init__(self, uid : int, read=False, **kwargs):
        self.title = kwargs.pop('title')
        self.subtitle = kwargs.get('subtitle')
        self.author = kwargs.get('author', 'Anonymous')
        self.date = kwargs.get('date', 'n.d.')
        self.summary = kwargs.get('summary', 'TBA')
        self.genre = set(kwargs.get('genre', []))

        self.available = kwargs.get('available', True)
        self.uid = uid

    def config(self, **kwargs):
        """
        Configures an attribute.
        
        Current attributes available:
            title : string
            subtitle : string (optional)
            author : string (optional)
            date : string (optional) 
                - preferably the year made
            summary : string
            genre : set of strings
            available : boolean
            uid : int
        """
        for attrib, value in kwargs.items():
            if attrib in self.__dict__.keys():
                self.__dict__[attrib] = value
            else:
                raise KeyError(f'Attribute {attrib} does not exist.')
    
    def format_book(self):
        return f'{self.title} ({self.date}) by {self.author}'
    
    def get_uid(self):
        return self.uid

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

class MetisClass:
    """
    Provides an interface for handling the reading lists and core functionalities.
    
    Rationale: Most, if not all, data will be handled
        exclusively by Metis. To make this possible, collections
        must not be assigned, except at initialization. Also, 
        Metis must NOT rely on any outside methods. Instead, 
        make sure that its methods can easily be used by other
        entities without messing up the backend.
    
    Instance Variables:
        collection : dict
            - a (key, value) pair of (uid, ReadingListItem). To access the
              collection of entries, use collection.values()
        filter : set
            - set of current filters used in requesting books
        recently_read_genre : collections.deque
            - stores the recently read genre. Used in improving
              the request book heuristics.
        available_genres : set
            - stores ALL of the genres that have been used
        search_filter : string
            - search_filter must be in the entry's format_book
              for it to available.
        
        Private variables
        - These can still be used by other entities, but they
          are not built for long term referencing, so reference
          them repeatedly whenever needed.
        
        availables : set
            - represents the current entries that might appear
              in a request book call. This can be replicated by
              using: set(filter(self.is_available, self.collection))
        indices : dict
            - (key, value) pairs of (formatted entry, uid) of the 
              entries. Commonly used for internal formatted entry -> uid
              conversion for Metis' use.
        next_uid : int
            - the next available uid available. This will be updated
              when a new entry is made.
    """

    def __init__(self):
        self.collection = dict()
        self.filter = set()
        self.indices = dict()
        self.availables = set()

        self.next_uid = 0

        self.available_genres = set()
        self.recently_read_genre = deque()
        self.search_filter = ''

    def reload(self, save_file : SaveFile = SaveFile()):
        """
        Loads a SaveFile.

        Rationale: In order to make sure that necessary references
            are not broken, just clear the collection and extend
            or update, instead of re-assigning.

        Warning: Do not use for any other purpose other than loading
        a state since this overhauls the current data it has.
        """
        self.collection.clear()
        self.collection.update({ int(index) : value for index, value in save_file.collection.items() }) 

        self.filter.clear()
        self.filter.update({ genre for genre in save_file.filter })

        # a private variable so assigning is permitted
        self.indices = { item.format_book().lower() : item.get_uid() for item in self.collection.values() }

        # a private variable
        self.availables = set(filter(self.is_available, self.collection.values()))
        self.available_genres.clear()
        self.available_genres.update(set(genre for item in self.collection.values() for genre in item.genre))

        self.recently_read_genre.clear()
        self.recently_read_genre.extend(save_file.recently_read)

        if save_file.collection:
            self.next_uid = max(x.get_uid() for x in self.collection.values()) + 1
    
    def reload_available(self):
        """
        Recomputes self.availables.

        This is often used after the filter is edited. Make sure
        to reload the GUI afterwards, if not yet done.
        """

        self.availables = set(filter(self.is_available, self.collection.values()))
    
    def request_book(self):
        """
        Returns a book from the available collection.
        
        In order to make the reading experience a bit more
        varied, Metis takes note of the previously read books
        and 'tries' to avoid giving them.
        """

        if not self.availables:
            return None

        chosen, population = None, list(self.availables)
        recents = [ (5*(index+1), genre) for index, genre in enumerate(self.recently_read_genre)]

        def okay(item, arr):
            "Check if there are conflicting genres"
            res = True
            for genre in item.genre:
                for index, x in enumerate(arr):
                    tries, illegal_genre = x
                    if genre == illegal_genre and tries:
                        res = False
                        arr[index] = (tries-1, illegal_genre)
            return res


        while not chosen:
            possible = random.choice(population)
            if okay(possible, recents):
                chosen = possible
        
        if chosen:
            self.toggle(chosen)

            # update the recently read genre
            temp_genre, to_add_genre = set(self.recently_read_genre), list()
            for genre in chosen.genre:
                if genre in temp_genre:
                    temp_genre.remove(genre)
                to_add_genre.append(genre)
            temp_genre = list(temp_genre)
            temp_genre.extend(to_add_genre)
            self.recently_read_genre = deque(temp_genre)

            while len(self.recently_read_genre) > 7:
                self.recently_read_genre.popleft()
        
        return chosen
        
        if self.availables:
            chosen = random.choice(list(self.availables))
            self.toggle(chosen)
            return chosen
        else:
            return None
    
    def is_available(self, item):
        """
        Tells whether an item is available for request.

        Rationale: self.availables is often changed drastically
            every filter edits. Therefore, reassigning is opted
            instead of clearing / updating. To make access to
            it easier, this method was made.

        This is often used by outside entities to generate
        a copy of the available entries by calling:
            set(filter(self.is_available, self.collection.values()))

        Parameter:
            item : ReadingListItem
                - the item to be checked
        
        Return Value : boolean
        """

        # should be available in the first place
        if not item.available:
            return False
        
        # It should also be shown in the frontend
        return self.is_showable(item)
    
    def is_showable(self, item):
        """
        Tells whether an item fits the filter criteria.

        Rationale: Being available is different from being
            showable. If it is available, it is eligible for
            request calls. If it is showable, it is possible
            that it is not available, but it should still appear
            in the frontend for whatever reason.
        
        Parameter:
            item : ReadingListItem
                - the item to be checked
        
        Return Value : boolean
        """
        
        # should be correct genre
        if self.filter and not any(genre in self.filter for genre in item.genre):
            return False
        
        # should be in search result
        if self.search_filter.lower() not in item.format_book().lower():
            return False

        return True
    
    def toggle(self, item):
        """
        Toggles the availability of the item.

        Rationality: There are three kinds of item
            toggling: frontend, backend, and both. 
            This is a backend toggle.

        This flips item.available and removes/adds
        it into self.availables.

        Parameter:
            item : ReadingListItem
                - the item to toggle
        """

        index = self.indices[item.format_book().lower()]
        self.collection[index].available = not self.collection[index].available

        if self.is_available(self.collection[index]):
            self.availables.add(item)
        else:
            self.availables.remove(item)
    
    def insert_item(self, data):
        """
        Attempts to insert a new item and tells if it is a success.

        Rationale: This should be "attempt_insert" since insertion
            is NOT guaranteed. However, this route might lead to
            redundant insertion. For performance reason, this
            method acts as both attempt and actual insertion, so
            be careful!

        Creates a new item normally and attempts to insert it into
        the collection. If its formatted title already exists as a
        key, then the method ends. If not, the item is added into
        the relevant collections and it is returned.

        Effects:
            (if success) 
            collection - a new (uid, item) pair is inserted
            availables - a new item may be inserted
            indices - a new (formatted title, uid) pair is inserted
            available_genres - new genres may be added

            (success independent)
            uid - incremented
        
        Parameter:
            data : dict
                - contains the data to be used for the instantation
                  of a new ReadingListItem. Therefore, its contents
                  must be formatted accordingly.
        
        Return Value: 
            None - if fail
            ReadingItemList - if success
        """

        uid = self.get_next_uid()
        new_item = ReadingListItem(uid=uid, toggle=self.toggle, **data)

        if new_item.format_book().lower() in self.indices.keys():
            return None

        self.collection[uid] = new_item
        if self.is_available(new_item):
            self.availables.add(new_item)
        self.indices[new_item.format_book().lower()] = uid
        for genre in new_item.genre:
            self.available_genres.add(genre)

        print(f'Successfully added {new_item.format_book()}.')

        return new_item
    
    def edit_item(self, item, new_data):
        """
        Attempts to update the item in the backend and tells if success.

        Rationale: This should be "attempt_edit" since editing
            is NOT guaranteed. However, this route might lead to
            redundant editing. For performance reason, this
            method acts as both attempt and actual editing, so
            be careful!

            Also, editing is a nasty process. To smoothen the process,
            update first the ones that uses other methods, then the
            collection that uses the previous formatted title, then
            the actual item and other collections that loosely refers
            to the item.
        
        Effects:
            (if success) 
            availables - an item may be toggled
            indices - an old pair is deleted and a new one is inserted
            available_genres - new genres may be added

            (success independent)
            uid - incremented

        Parameters:
            item : ReadingListItem
                - the item to be edited (should be the unedited version)
            new_data : dict
                - the dict of the new data. It should follow the
                  ReadingListItem's convention.
        
        Return Value : boolean
        """

        new_item = ReadingListItem(uid=item.get_uid(), **new_data)
        
        if not item.format_book() == new_item.format_book() and new_item.format_book().lower() in self.indices.keys():
            return False

        # Call other methods that rely on self.indices first
        if new_data['available'] != item.available:
            self.toggle(item)

        # deleting old index, make sure that item.format_book().lower() will not be used anymore
        index = self.indices[item.format_book().lower()]
        del self.indices[item.format_book().lower()]
        self.indices[new_item.format_book().lower()] = index

        # apply the superficial changes last
        item.config(**new_data)

        for genre in new_data['genre']:
            self.available_genres.add(genre)

        return True
    
    def delete_item(self, item):
        """
        Deletes an item from the backend.

        Rationale: This should be "attempt_delete" since deletion
            is NOT guaranteed. However, this route might lead to
            redundant deleting. For performance reason, this
            method acts as both attempt and actual deletion, so
            be careful!

            Also, deletion is a nasty process. To smoothen the process,
            call first the ones that uses other methods, then delete from 
            the collections that uses the item, then the actual item and 
            other collections that loosely refers to the item.
        
        Effects:
            (if success) 
            collection - a (uid, item) pair is deleted
            availables - an item may be removed
            indices - a (formatted title, uid) pair is deleted
        
        Parameter:
            item : ReadingListItem
                - the item to be deleted
        """

        if item.format_book().lower() not in self.indices.keys():
            raise KeyError(f'{item.format_book()} is missing. Cannot be deleted...')
            return

        index = self.indices[item.format_book().lower()]
        
        del self.collection[index] 
        del self.indices[item.format_book().lower()]
        if item.available:
            self.availables.remove(item)
        
        del item
    
    def get_next_uid(self):
        "Returns the next available uid."

        res = self.next_uid
        self.next_uid += 1
        return res