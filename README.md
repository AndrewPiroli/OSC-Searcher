## Simple OSC searcher

A command line tool to search the OSC library for homebrew.

Downloads a list of all homebrew on OSC, does a fuzzy text search (partial ratio) on both the display name and description,
selects the better score of those two, then ranks the results and displays the top 5.

### Requirements:
 Python 3.6+ (probably, only tested on 3.9)
 requests library
 rapidfuzz library