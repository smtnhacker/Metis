# Metis [![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

![GitHub last commit](https://img.shields.io/github/last-commit/smtnhacker/metis?style=flat-square)

A simple python project that creates reading lists and suggests books to read.

## Demo

![Demo Gif](https://github.com/smtnhacker/Metis/blob/master/Screenshots/sample_usage.gif)

**Main Window**

![Metis](https://github.com/smtnhacker/Metis/blob/master/Screenshots/1.PNG) 

**Creating a new book**

![Creating a new book](https://github.com/smtnhacker/Metis/blob/master/Screenshots/2.PNG)

## About the Project

### Motivating Problem

At its core, this project is just a practice on software development (using Python). However, a good software should ideally be built solving a particular problem. In this case, the problem I wanted to solve was:

> People can often get stuck on deciding what book to read. Futhermore, people can also have mood for certain genres or authors at times, so when choosing a book, they should be given the freedom to filter out books that are in their mood right now.

### How I worked on this project

This was my first time working with GUI on Python; hence, I opted to tinker around with the library first in order to get a feel on what I can do with it. Once I understood what I can (reasonably) do, I started working on making a barely functional prototype. At this early stage, I prioritized speed over maintainability. Once I had a feel on how the code structure will look like, I started refactoring to make the project more maintanable and to make further developments easier and quicker. 

With regards to business logic vs UI/UX, I typically focused more on the business logic first, ensuring that the project is feasible and that there are no obvious bugs. Once I feel that a feature is working sufficiently, I start improving the UI/UX.

### How to navigate this project

The bulk of the logic is contained in the utility classes in the `utils` folder, where the main class is in the `metis.py` file. The `_gui.py` file concerns itself with building the GUI while the `_interactions.py` connects the GUI with the utility classes through event handlers. The `main.py` mainly concerns itself with setting up configurations and fail-safes so that the app can still run even with corrupted data files (though, the data might not be saved). 

### Why this project structure

I separated the GUI with the utility classes since the underlying logic should not influence much how the user interacts with the app. Furthermore, I separated the logic into various utility classes since their functions are generally mutually exclusive. This grouping into features helped adding and modifying features easier and less buggier.

### Possible improvements

One notable point of improvement is with the GUI library; I used TKinter, which led to the non-modern looking design. I chose this since it was my first time with Python GUI applications, but it may not be a good choice for the long term. The way I passed event handlers might also be a bit messy. I should use a system that avoids _drilling_ parameters.

## Installation

There's nothing to install. Just make sure that you have Python 3.7.0 or later versions in your system!

## Usage

Make sure you are in the `src` folder and run the following:

```bash
python main.py
```

The rest of the application should be pretty straightforward (if they are not, please raise an issue or contact me!) 

#### Notes

For a book entry to appear in the list, it must satisfy **all** filter criteria (genre and search field). For a book to satisfy the genre criteria, it must have **at least** one genre that appears in the list.

## Support

If there are any concerns or problems, please don't hesistate to raise an issue!

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

Theme: [Sun Valley TTk Theme by rdbende](https://github.com/rdbende/Sun-Valley-ttk-theme)

## License
[MIT](https://choosealicense.com/licenses/mit/)
