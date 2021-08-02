from playerLogic.Scrapper import Scrapper
from enum import Enum
import re
import playerLogic.PlayerException as PErr


def print_err(err_msg: str):
    print(Colors.r.value + err_msg + Colors.end.value)


def check_valid_url(url: str) -> bool:
    """
        check if a given url is from site sdarot
    :param url: url string to check
    :return: True if the url is valid, else False
    """
    if not re.search("^https://sdarot.*/watch/.*$", url):
        return False
    return True


def get_int_input(min_val: int or None, max_val: int or None) -> int:
    """
        get input as integer within the given range [min_val, max_val]
    :param min_val: minimum value of input acceptable
    :param max_val: maximum value of input acceptable
    :return: integer input
    """
    while True:
        try:
            res = int(input())
            if not min_val or not max_val or min_val <= res <= max_val:
                return res
            else:
                print_err("Please enter a valid choice (number between " + str(min_val) + " and " + str(max_val))
        except ValueError:
            print_err("The British define number as - 'A single issue of a magazine'...\n"
                      "Since this is not England, that's not what we mean here "
                      "so stop being an idiot and pick a god damn number!")


class Colors(Enum):
    end = "\033[0m"
    r = "\033[1;31m"
    g = "\033[1:32m"
    y = "\033[1:33m"
    b = "\033[1;34m"
    p = "\033[1:35m"
    c = "\033[1:36m"


class Controller:

    def __init__(self, path: str):
        self.__s_enlarge = True
        self.__s_window = True
        self.__s_progress = False
        self.__driver_path = path
        self.__player = Scrapper(path)

    def play_options(self) -> None:
        """
            show all play options for the chosen series and play series accordingly
        :return: None
        """
        print(Colors.p.value + "Choose play option:\n"
                               "1." + Colors.end.value + " Play all\n" +
              Colors.p.value + "2." + Colors.end.value + " Choose season\n" +
              Colors.p.value + "3." + Colors.end.value + " Choose season and episode\n")
        option = get_int_input(1, 3)

        try:
            if option == 1:
                # play all seasons and all episodes
                self.__player.play(1, 1)
            else:
                # get season input and check if it's available for the given series
                print(Colors.p.value + "Type season number: " + Colors.end.value)
                se = get_int_input(1, None)
                while not self.__player.check_valid_season(se):
                    print_err("You either made a mistake there or this season is not yet available here :(")
                    se = get_int_input(1, None)
                if option == 3:
                    # get episode input and check if it's available for the given series
                    print(Colors.p.value + "Type episode number: " + Colors.end.value)
                    ep = get_int_input(1, None)
                    while not self.__player.check_valid_episode(ep, se):
                        print_err("You probably made a mistake there or this episode is not yet available here :(")
                        ep = get_int_input(1, None)
                    # play from given season and given episode
                    self.__player.play(se, ep)
                # play from given season
                self.__player.play(se, None)
        except PErr.EndOfSeries:
            print(Colors.b.value + "Series ended - returning to main options menu" + Colors.end.value)
            self.start()

    def search_by_name(self) -> None:
        """
            search for a series by full/partial name.
        :return: None
        """
        # get name input and search for matches
        name = input(Colors.p.value + "Enter series name:\n" + Colors.end.value)
        series = self.__player.search_series(name)

        if series is None:
            # no results found for the given name
            print_err(series["data"])
            self.__player.reset()
            choice = input(Colors.g.value + "Type s to search for another series (any other choice will return to main "
                                            "options menu):\n" + Colors.end.value)
            if choice.lower() == "s":
                self.search_by_name()
            else:
                return
        else:
            # results found for the given name
            print(Colors.g.value + "Found " + str(len(series["data"]) - 1) + " matches:" + Colors.end.value)
            for i in range(0, len(series["data"]) - 1):
                print(Colors.g.value + str(i + 1) + Colors.end.value + "\n" + series["data"][i])
            print(Colors.p.value + "Choose series (number): " + Colors.end.value)
            choice = get_int_input(1, len(series["data"]))
            # present play options for the chosen series
            self.__player.goto(series_num=choice - 1, url=None)
            self.play_options()

    def search_by_url(self) -> None:
        """
            search for a series by a given url
        :return: None
        """
        url = input(Colors.p.value + "Please enter URL:\n" + Colors.end.value)
        # check if the given url is valid
        if not check_valid_url(url):
            print_err("Incorrect url - check yourself!")
            self.search_by_url()
        else:
            # present play options for the chosen series
            self.__player.goto(series_num=None, url=url)
            self.play_options()

    def change_settings(self):
        print_err("NOT YET IMPLEMENTED")
        pass

    def start(self) -> None:
        if not self.__player.connect():
            print_err("The website is down... again -_- ...try later")
            exit()
        options = {1: self.search_by_name, 2: self.search_by_url, 3: exit}
        while True:
            print(Colors.c.value + "Welcome to my useless sdarot automatic player!" + Colors.end.value)
            print(Colors.p.value + "Please choose your poison:\n" +
                  "1." + Colors.end.value + " Search for series by name.\n" +
                  Colors.p.value + "2." + Colors.end.value + " Search for series by URL.\n" +
                  Colors.p.value + "3." + Colors.end.value + " Exit")

            choice = get_int_input(1, 3)
            options[choice]()

    def set_enlarge(self, val: bool) -> None:
        if val != self.__s_enlarge:
            self.__s_enlarge = val

    def set_progress(self, val: bool) -> None:
        if val != self.__s_progress:
            self.__s_progress = val

    def get_settings(self) -> {str: bool}:
        return {"enlarge": self.__s_enlarge, "window": self.__s_window, "save": self.__s_progress}
