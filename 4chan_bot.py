# coding: utf-8

"""

This script is a 4chan bot
It is used to parse the website for specific keywords.

Author: Phaide | https://phaide.net/
Licence: GNU GPL v3
Repository: https://github.com/Phaide/4chan_bot/
Build: 27/01/2020

"""

# Import non built-in modules. Requires external installation.
import requests # pip install requets
import curses # pip install windows-curses (on Windows of course). Documentation: https://docs.python.org/3/howto/curses.html

# Import build-in modules
import re, webbrowser

# List of boards to parse.
boards = ["b"]
# List of terms to search for. Keep in mind that the script parses HTML, so adapt your terms accordingly.
terms = ["Facts", "Logic", "Other"]

class b_4chan:

    # 4chan boards subdomain ; boards addresses are built from this address.
    address = "http://boards.4chan.org"

    def __init__(self, boards, terms):
        self.boards = boards
        self.searchingFor = terms
        self.init_activeThreads()

    def init_activeThreads(self):
        """
        Empties the activeThreads dictionnary then recreates it.
        """
        self.activeThreads = {}
        for term in self.searchingFor:
            self.activeThreads[term] = []

    def main_parser(self):
        """
        Main function
        """
        for board in self.boards:
            self.board_parser(board)

    def r_is_in_list(self, uList, term):
        """
        Searches recursively for a term in the passed list.
        Returns True if it found it, False otherwise.
        """
        for value in uList:
            if (type(value) in (list, tuple, dict)):
                if (term in value) or self.r_is_in_list(value, term):
                    return True
            else:
                if value == term:
                    return True

    def board_parser(self, board):
        """
        Gets the HTML of the board's pages to find threads.
        """
        boardAdd = "{}/{}".format(self.address, board)
        pages = [""] + list(range(2, 10))
        for page in pages:
            r = requests.get("{}/{}".format(boardAdd, page))
            if r.status_code == 200:
                threads = re.findall(r"id=\"t([0-9]*)\"", r.text)
                for thread in threads:
                    self.thread_parser(board, thread)

    def thread_parser(self, board, thread):
        """
        Parses each thread's HTML code to find the terms.
        """
        threadAdd = "{}/{}/thread/{}".format(self.address, board, thread)
        r = requests.get(threadAdd)
        if r.status_code == 200:
            for term in self.searchingFor:
                count = r.text.lower().count(term.lower())
                if count > 0:
                    if not self.r_is_in_list(self.activeThreads[term], threadAdd):
                        self.activeThreads[term].append([count, threadAdd])

class Display:

    def __init__(self, menu):
        self.menu = menu + ["Exit"]
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def __del__(self):
        self.stdscr.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def loading_screen(self):
        """
        Prints a simple loading screen.
        """
        row = "Loading..."
        self.stdscr.clear()
        # Get screen dimensions (height and width)
        h, w = self.stdscr.getmaxyx()
        # Find the center
        x = (w // 2) - (len(row) // 2)
        y = (h // 2)
        # Print the text
        self.stdscr.addstr(y, x, row)
        # Refresh display
        self.stdscr.refresh()

    def main(self, bot):
        """
        Main loop, used to navigate through the menus and execute actions depending on user input.
        """
        for index, entry in enumerate(self.menu):
            try:
                indexName = next(v for i, v in enumerate(bot.activeThreads) if i == index)
                try:
                    self.menu[index] = [len(bot.activeThreads[indexName]), self.menu[index]]
                except NameError:
                    continue
            except:
                continue
        currentMenuRowIndex = 0
        while True:
            try:
                # Get the name of the menu entry in the "bot.activeThreads" var, used to access data in this dictionnary
                currentMenuRowName = next(v for i, v in enumerate(bot.activeThreads) if i == currentMenuRowIndex)
            except: # Catches StopIteration when selecting menu entry "Exit"
                pass
            self.print_list(self.menu, currentMenuRowIndex)
            key = self.stdscr.getch()
            if (key == curses.KEY_UP) and (currentMenuRowIndex > 0):
                currentMenuRowIndex -= 1
            elif (key == curses.KEY_DOWN) and (currentMenuRowIndex < (len(self.menu) - 1)):
                currentMenuRowIndex += 1
            elif (key == ord("u")):
                self.loading_screen()
                bot.init_activeThreads()
                bot.main_parser()
            elif (key == curses.KEY_RIGHT) and (currentMenuRowIndex == (len(self.menu) - 1)):
                break
            elif (key == curses.KEY_RIGHT) and (len(bot.activeThreads[currentMenuRowName]) > 0):
                currentThreadRowIndex = 0
                while True:
                    self.print_list(bot.activeThreads[currentMenuRowName], currentThreadRowIndex)
                    key = self.stdscr.getch()
                    if (key == curses.KEY_UP) and (currentThreadRowIndex > 0):
                        currentThreadRowIndex -= 1
                    elif (key == curses.KEY_DOWN) and (currentThreadRowIndex < (len(bot.activeThreads[currentMenuRowName]) - 1)):
                        currentThreadRowIndex += 1
                    elif (key == curses.KEY_RIGHT):
                        # Uses the webbrowser module to open a web page.
                        webbrowser.open(bot.activeThreads[currentMenuRowName][currentThreadRowIndex][1])
                    elif (key == curses.KEY_LEFT):
                        break

    def print_list(self, list, currentIndex):
        """
        Prints a list's items in the screen center.
        """
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        for index, couple in enumerate(list):
            row = "{} | {}".format(couple[0], couple[1]) if type(couple) == type([]) and (len(couple) == 2) else couple
            # The two next lines centers the menu entries, vertically and horizontally
            x = (w // 2) - (len(row) // 2)
            y = (h // 2) - (len(list) // 2) + index
            if x in range(0, w) and y in range(0, h):
                if index == currentIndex:
                    self.stdscr.addstr(y, x, row, curses.color_pair(1))
                else:
                    self.stdscr.addstr(y, x, row)
            else:
                self.stdscr.addstr(0, 0, "Too many results to display !\nIncrease the window size and/or dezoom")
        self.stdscr.refresh()

if __name__ == "__main__":
    bot = b_4chan(
        boards,
        terms
    )
    display = Display(bot.searchingFor)
    display.loading_screen()
    bot.main_parser()
    display.main(bot)
    del bot, display
