import random

class MetisClass:
    """Provides an interface for handling the reading lists"""
    def __init__(self, collection=list()):
        self.collection = collection
        self.indices = { item.format_book() : index for index, item in enumerate(collection)}
        self.availables = set(filter(lambda x : x.available, self.collection))
    
    def request_book(self):
        "Returns a book from the available collection"
        
        if self.availables:
            chosen = random.choice(list(self.availables))
            self.toggle(chosen)
            return chosen.format_book()
        else:
            return 'No book available'
    
    def toggle(self, item):
        index = self.indices[item.format_book()]
        self.collection[index].available = not self.collection[index].available

        if self.collection[index].available:
            self.availables.add(item)
        else:
            self.availables.remove(item)
    
    def insert_item(self, data):
        new_item = ReadingListItem(**data)
        if new_item.format_book() in self.indices.keys():
            return None
        self.collection.append(new_item)
        self.availables.add(new_item)
        self.indices[new_item.format_book()] = len(self.collection) - 1
        print(f'Successfully added {new_item.format_book()}.')
        return new_item

class ReadingListItem:
    """Describes a book a to read"""

    def __init__(self, read=False, **kwargs):
        self.title = kwargs.pop('title')
        self.subtitle = kwargs.get('subtitle')
        self.author = kwargs.get('author', 'Anonymous')
        self.date = kwargs.get('date', 'n.d.')
        self.summary = kwargs.get('summary', 'TBA')
        self.genre = kwargs.get('genre')

        self.available = kwargs.get('available', True)
    
    def config(self, **kwargs):
        for attrib, value in kwargs.items():
            if attrib in self.__dict__.keys():
                self.__dict__[attrib] = value
            else:
                print(f'Attribute {attrib} does not exist.')
    
    def format_book(self):
        return f'{self.title} ({self.date}) by {self.author}'