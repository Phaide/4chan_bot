# coding: utf-8

"""
This script is a 4chan bot.
It is used to parse the website for specific keywords.
Licence: GNU GPL v3
Repository: https://github.com/Phaide/4chan_bot/
Build: 28/01/2021
"""

# Import build-in modules
import re
import webbrowser
# We use multi-threading to improve performance
import multiprocessing as mp

from typing import Tuple

# Import third-party
import requests
import curses

# List of boards to parse. Example : ["b", "pol", "r9k"]
boards = ["b", "r9k"]
# List of terms to search for. Note : the script parses HTML, so adapt your terms accordingly.
# Also, terms are case-insensitive.
terms = ["Facts", "Logic", "Other"]


class FourChanBot:

    # 4chan boards subdomain ; boards addresses are built from this address.
    url = "https://boards.4chan.org"

    def __init__(self, display, boards: list, terms: list):
        self.display = display
        self.boards = boards
        self.searching_for = terms
        self.init_active_threads()
        self.active_threads = None
        self.current_board = None

    def init_active_threads(self):
        """
        Empties the activeThreads dictionary then recreates it.
        """
        self.active_threads = {}
        for term in self.searching_for:
            self.active_threads[term] = []

    def main_parser(self):
        self.init_active_threads()
        for board in self.boards:
            self.current_board = board
            self.board_parser_main()
        for term, active_thread in self.active_threads.items():
            active_thread.sort(reverse=True)
        self.display.main(self)

    def r_is_in_list(self, u_list: list, term: str) -> bool:
        """
        Searches recursively for a term in the passed list.
        Returns True if it found it, False otherwise.
        """
        for value in u_list:
            if type(value) in (list, tuple, dict):
                if term in value or self.r_is_in_list(value, term):
                    return True
            else:
                if value == term:
                    return True
        return False

    def board_parser_main(self):
        """
        Creates a multithreading pool to parse each boards pages simultaneously.
        """
        board_add = f"{self.url}/{self.current_board}"
        pages = [f"{board_add}/{i}" for i in ("", 2, 3, 4, 5, 6, 7, 8, 9, 10)]
        # Creates a multithreading pool (doesn't work for some reason)
        for page in pages:
            self.board_parser(page)
        # with mp.Pool(mp.cpu_count()) as pool:
        #    pool.map(self.board_parser, pages)

    def board_parser(self, page):
        """
        Gets the HTML of the board's pages to find threads.
        """
        try:
            r = requests.get(page)
        except requests.exceptions.ConnectionError:
            self.display.display_network_error()
            return
        if r.status_code == 200:
            threads = re.findall(r"id=\"t([0-9]*)\"", r.text)
            for thread in threads:
                self.thread_parser(self.current_board, thread)

    def thread_parser(self, board, thread):
        """
        Parses each thread's HTML code to find the terms.
        """
        thread_add = f"{self.url}/{board}/thread/{thread}"
        try:
            r = requests.get(thread_add)
        except requests.exceptions.ConnectionError:
            self.display.display_network_error()
            return
        if r.status_code == 200:
            for term in self.searching_for:
                count = r.text.lower().count(term.lower())
                if count > 0:
                    if not self.r_is_in_list(self.active_threads[term], thread_add):
                        self.active_threads[term].append([count, thread_add])


class Display:

    def __init__(self, menu):
        self.menu = menu + ["Exit"]
        self.screen = curses.initscr()
        self.screen.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def __del__(self):
        self.screen.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def display_single_line(self, row: str):
        self.screen.clear()
        x, y = self.get_center_coordinates(row)
        self.screen.addstr(y, x, row)
        self.screen.refresh()

    def loading_screen(self):
        """
        Prints a simple loading screen.
        """
        self.display_single_line("Loading...")

    def display_network_error(self):
        self.display_single_line("Network exception. Please verify your Internet connection.")
        input()  # Pause (actually stops processing)

    def main(self, bot):
        """
        Main loop, used to navigate through the menus and execute actions depending on user input.
        """
        self.add_count_to_menu(bot)
        current_menu_row_index = 0
        while True:
            try:
                # Get the name of the menu entry in the "bot.activeThreads" var, used to access data in this dictionary
                current_menu_row_name = next(v for i, v in enumerate(bot.active_threads) if i == current_menu_row_index)
            except StopIteration:  # Catches StopIteration when selecting menu entry "Exit"
                continue
            self.print_list(self.menu, current_menu_row_index)
            key = self.screen.getch()
            if key == curses.KEY_UP and current_menu_row_index > 0:
                current_menu_row_index -= 1
            elif (key == curses.KEY_DOWN) and (current_menu_row_index < (len(self.menu) - 1)):
                current_menu_row_index += 1
            elif key == ord("u"):
                self.loading_screen()
                bot.main_parser()
                self.add_count_to_menu(bot)
            elif key == curses.KEY_RIGHT and current_menu_row_index == len(self.menu) - 1:
                break
            elif key == curses.KEY_RIGHT and len(bot.active_threads[current_menu_row_name]) > 0:
                current_thread_row_index = 0
                while True:
                    self.print_list(bot.active_threads[current_menu_row_name], current_thread_row_index)
                    key = self.screen.getch()
                    if (key == curses.KEY_UP) and (current_thread_row_index > 0):
                        current_thread_row_index -= 1
                    elif key == curses.KEY_DOWN and \
                            current_thread_row_index < len(bot.active_threads[current_menu_row_name]) - 1:
                        current_thread_row_index += 1
                    elif key == curses.KEY_RIGHT:
                        # Open the thread in the default web browser.
                        webbrowser.open(bot.active_threads[current_menu_row_name][current_thread_row_index][1])
                    elif key == curses.KEY_LEFT:
                        break

    def add_count_to_menu(self, bot):
        for index, entry in enumerate(self.menu):
            try:
                index_name = next(v for i, v in enumerate(bot.active_threads) if i == index)
            except StopIteration:
                continue
            try:
                if isinstance(self.menu[index], list):
                    self.menu[index] = [len(bot.active_threads[index_name]), self.menu[index][1]]
                else:
                    self.menu[index] = [len(bot.active_threads[index_name]), self.menu[index]]
            except NameError:
                continue

    def print_list(self, p_list, current_index):
        """
        Prints a list's items in the screen center.
        """
        self.screen.clear()
        height, width = self.screen.getmaxyx()
        for index, couple in enumerate(p_list):
            if isinstance(couple, list) and len(couple) == 2:
                row = f"{couple[0]} | {couple[1]}"
            else:
                row = couple
            # The two next lines centers the menu entries, vertically and horizontally
            x = (width // 2) - (len(row) // 2)
            y = (height // 2) - (len(p_list) // 2) + index
            if x in range(0, width) and y in range(0, height):
                if index == current_index:
                    self.screen.addstr(y, x, row, curses.color_pair(1))
                else:
                    self.screen.addstr(y, x, row)
            else:
                self.screen.addstr(0, 0, "Too many results to display !\nIncrease the window size and/or dezoom")
        self.screen.refresh()

    def get_center_coordinates(self, row: str) -> Tuple[int, int]:
        # Get screen dimensions (height and width)
        height, width = self.screen.getmaxyx()
        # Find the center
        x = (width // 2) - (len(row) // 2)
        y = (height // 2)
        return x, y


def main():
    display = Display(terms)
    display.loading_screen()

    bot = FourChanBot(display, boards, terms)
    bot.main_parser()

    del bot, display


if __name__ == "__main__":
    main()
