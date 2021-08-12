from collections import deque
import random
import json

class MetisClass:
    """Provides an interface for handling the reading lists and core functionalities"""

    def __init__(self, collection=dict()):
        self.collection = dict()
        self.reload(collection)
        self.next_uid = 0
        self.available_genres = set()
        self.filter = None

        self.recently_read_genre = deque()

    def reload(self, collection=dict()):
        self.collection.clear()
        self.collection.update({ int(index) : value for index, value in collection.items() }) 
        self.indices = { item.format_book() : item.get_uid() for item in self.collection.values() }
        self.availables = set(filter(self.is_available, self.collection.values()))
        self.available_genres = set(genre for item in collection.values() for genre in item.genre)

        if collection:
            self.next_uid = max(x.get_uid() for x in self.collection.values()) + 1
    
    def reload_available(self, genres):
        self.filter = genres.copy()
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
        
        print(recents)
        return chosen
        
        if self.availables:
            chosen = random.choice(list(self.availables))
            self.toggle(chosen)
            return chosen
        else:
            return None
    
    def is_available(self, item):
        # should be available in the first place
        if not item.available:
            return False
        # should be correct genre
        if self.filter and not any(genre in self.filter for genre in item.genre):
            return False
        
        return True
    
    def toggle(self, item):
        index = self.indices[item.format_book()]
        self.collection[index].available = not self.collection[index].available

        if self.is_available(self.collection[index]):
            self.availables.add(item)
        else:
            self.availables.remove(item)
    
    def insert_item(self, data):
        uid = self.get_next_uid()
        new_item = ReadingListItem(uid=uid, **data)
        if new_item.format_book() in self.indices.keys():
            return None
        self.collection[uid] = new_item
        if self.is_available(new_item):
            self.availables.add(new_item)
        self.indices[new_item.format_book()] = uid
        for genre in new_item.genre:
            self.available_genres.add(genre)
        print(f'Successfully added {new_item.format_book()}.')
        return new_item
    
    def edit_item(self, item, new_data):
        new_item = ReadingListItem(uid=item.get_uid(), **new_data)
        
        if not item.format_book() == new_item.format_book() and new_item.format_book() in self.indices.keys():
            return False
        
        index = self.indices[item.format_book()]
        del self.indices[item.format_book()]
        self.indices[new_item.format_book()] = index
        if new_data['available'] != item.available:
            self.toggle(item)
        item.config(**new_data)
        for genre in new_data['genre']:
            self.available_genres.add(genre)
        return True
    
    def delete_item(self, item):
        if item.format_book() not in self.indices.keys():
            print(f'{item.format_book()} is missing. Cannot be deleted...')
            return
        index = self.indices[item.format_book()]
        del self.collection[index] # So inefficient...
        del self.indices[item.format_book()]
        if item.available:
            self.availables.remove(item)
    
    def get_next_uid(self):
        res = self.next_uid
        self.next_uid += 1
        return res

class ReadingListItem:
    """Describes a book to read"""

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
        for attrib, value in kwargs.items():
            if attrib in self.__dict__.keys():
                self.__dict__[attrib] = value
            else:
                print(f'Attribute {attrib} does not exist.')
    
    def format_book(self):
        return f'{self.title} ({self.date}) by {self.author}'
    
    def get_uid(self):
        return self.uid

    # ------------------------------------------ #
    # --------- For JSON Conversion ------------ #
    # ------------------------------------------ #
        
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
                    if type(value) == set:
                        res[key] = list(value)
                    else:
                        res[key] = value
                return res
            else:
                return super().default(dct)