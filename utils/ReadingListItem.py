"""
Reading List Item

Contains the class for Reading List Item

Note: Code-split from metis.py
"""

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
