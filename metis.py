import random

class MetisClass:
    """Provides an interface for handling the reading lists"""
    def __init__(self, collection=list()):
        self.collection = collection
        self.available = list(filter(lambda x : x.available, self.collection))
    
    def request_book(self):
        "Returns a book from the available collection"

        def format_book(book):
            return f'{book.title} ({book.date}) by {book.author}'
        
        if self.available:
            return format_book(random.choice(self.available))
        else:
            return 'No book available'

class ReadingListItem:
    """Describes a book a to read"""

    def __init__(self, read=False, **kwargs):
        self.title = kwargs.pop('title')
        self.subtitle = kwargs.get('subtitle')
        self.author = kwargs.get('author', 'Anonymous')
        self.date = kwargs.get('date', 'n.d.')
        self.summary = kwargs.get('summary', 'TBA')
        self.genre = kwargs.get('genre')

        self.available = kwargs.get('read', True)
    
    def config(self, **kwargs):
        for attrib, value in kwargs.items():
            if attrib in self.__dict__:
                self.__dict__[attrib] = value
            else:
                print(f'Attribute {attrib} does not exist.')