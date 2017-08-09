# Freecycle Scraper
Python utility which queries one or many [Freecycle](https://www.freecycle.org/) listings to identify and retrive which ones are new since the last run of the utility.

Outputs to the default HTML handling program as defined by the operating system e.g. Google Chrome. New listings are highlighted in green, old listings highlighted in red.

## Usage
    python freecycleScraper.py [freecycle URL 1] [freecycle URL 2] [...]

For example, for the Cheltenham and Southampton offers pages, I would use the following command:

    python freecycleScraper.py https://groups.freecycle.org/group/CheltenhamUK/posts/offer https://groups.freecycle.org/group/SouthamptonUK/posts/offer