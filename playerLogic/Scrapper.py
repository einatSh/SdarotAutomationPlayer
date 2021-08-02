import playerLogic.PlayerException as PErr
import requests
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def to_sec(time_array):
    """
        convert the given string array to time in seconds
    :param time_array: array of string representing the remaining time for the video [s, m, h] or [s, m]
    :return: time converted to seconds
    """
    res = 0
    for i in range(0, len(time_array)):
        res = res + int(time_array[i]) * (pow(60, len(time_array) - 1 - i))
    return res


class Scrapper:

    def __init__(self, chromedriver_path: str):
        self.__chrome_path = chromedriver_path
        self.__url = "https://sdarot."
        self.__url_ending = ["tv", "dev", "world", "work", "casa", "pro"]
        self.__driver = None
        self.__series_found = None
        self.__last_season = False

    def reset(self) -> None:
        """
            reset class variables
        :return: None
        """
        self.__driver = None
        self.__series_found = None
        self.__last_season = False

    def search_series(self, series_name: str) -> [str] or None:
        """
            searches for a series with the given name in the site sdarot, saves matches found and returns a list
            of matching series names from the site
        :param series_name: given series name to search
        :return: a list of strings for matching series names if found, else None
        """
        self.init_chrome_headless()
        search_bar = self.__driver.find_element_by_id("liveSearch")
        search_bar.send_keys(series_name.rstrip())

        try:
            self.__series_found = WebDriverWait(self.__driver, 3) \
                .until(EC.presence_of_element_located((By.CLASS_NAME, "typeahead.dropdown-menu"))) \
                .find_elements_by_css_selector("li")
            res = []
            for i in self.__series_found:
                res.append(i.text)
            return res
        except TimeoutException:
            return None

    def connect(self) -> bool:
        """
            checks if any of the sites for sdarot works, and if the current site is reachable
        :return: True if a working site was found, else False
        """
        if self.__url == "https://sdarot.":
            for url_end in self.__url_ending:
                curr_url = self.__url + url_end
                if requests.head(curr_url).status_code == 200:
                    self.__url = curr_url
                    return True
            return False
        else:
            return requests.head(self.__url).status_code == 200

    def init_chrome(self, url: str) -> None:
        """
            initializes chrome settings for the player
        :param url: url to open with chrome
        :return: None
        """
        if self.__driver is not None:
            self.__driver.quit()
            self.__driver = None
        self.__driver = webdriver.Chrome(executable_path=self.__chrome_path)
        self.__driver.maximize_window()
        self.__driver.get(url)

    def init_chrome_headless(self) -> None:
        """
            initializes headless chrome settings for the background player
        :return: None
        """
        if self.__driver is not None:
            self.__driver.quit()
            self.__driver = None
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.__driver = webdriver.Chrome(executable_path=self.__chrome_path, options=option)
        self.__driver.get(self.__url)

    def check_valid_season(self, se: int) -> bool:
        """
            check if the given season is available in the site
        :param se: season to check
        :return: True if it's available, else False
        """
        seasons = self.__driver.find_element_by_id("season").find_elements_by_tag_name("li")
        return 1 <= se <= len(seasons)

    def check_valid_episode(self, ep: int, se: int) -> bool:
        """
            check if the given episode is available for the given season
        :param ep: given episode to check
        :param se: season containing the episode
        :return: True if the episode exists, else False
        """
        seasons = self.__driver.find_element_by_id("season").find_elements_by_tag_name("li")
        seasons[se-1].click()
        episodes = WebDriverWait(self.__driver, 20) \
                .until(EC.presence_of_element_located((By.ID, "episode"))) \
                .find_elements_by_css_selector("li")
        return 1 <= ep <= len(episodes)

    def goto(self, series_num: int or None, url: str or None) -> None:
        """
            navigate chrome background driver to the given url or to the chosen series from the available list
        :param series_num: number of series from the list or None
        :param url: url to direct to, or None
        :return: None
        """
        if series_num is not None:
            self.__series_found[series_num].click()
            self.__series_found = None
        elif url:
            self.__driver.get(url)

    def play(self, se: int or None, ep: int or None) -> None:
        """
            play all seasons and all episodes. If season or episode chosen, will start playing from chosen place
        :param se: season to start playing from, or None to play all seasons and all episodes
        :param ep: episode to start from, or None to play all episodes
        :return: None
        """
        try:
            self.init_chrome(self.__driver.current_url)

            seasons = self.__driver.find_element_by_id("season").find_elements_by_css_selector("li")
            if se:
                seasons = seasons[se-1:]

            last = int(seasons[len(seasons)-1].text)
            for season in seasons:
                curr_se = int(season.text)
                if curr_se == last:
                    self.__last_season = True
                if curr_se == se:
                    self.play_season(season, ep)
                else:
                    self.play_season(season, None)
        except WebDriverException:
            self.reset()
            raise PErr.ChromeExited

    def play_season(self, se, ep: int or None) -> None:
        """
            play given season. if episode is given, will play from given episode.
        :param se: season to play
        :param ep: starting episode to play from, or None to play all episodes.
        :return: None
        """
        se.click()
        try:
            episodes = WebDriverWait(self.__driver, 10) \
                .until(EC.presence_of_element_located((By.ID, "episode"))) \
                .find_elements_by_css_selector("li")

            if ep:
                episodes = episodes[ep-1:]

            last = int(episodes[len(episodes)-1].text)
            for episode in episodes:
                curr_ep = int(episode.text)
                self.play_episode(episode)
                if self.__last_season and curr_ep == last:
                    self.__driver.quit()
                    self.reset()
                    raise PErr.EndOfSeries
        except TimeoutException:
            self.play_season(se, ep)

    def play_episode(self, ep) -> None:
        """
            load and play given episode.
        :param ep: episode to play.
        :return: None
        """
        ep.click()
        self.__driver.execute_script("window.scrollTo(0, 1436)")    # scroll to video location
        try:
            # wait for loading to finish and play the video
            WebDriverWait(self.__driver, 35).until(EC.element_to_be_clickable((By.ID, "proceed"))).click()
            self.play_video()
        except TimeoutException:
            self.play_episode(ep)

    def play_video(self) -> None:
        """
            play current video.
        :return: None
        """
        try:
            # if a popup window shows up - close it
            popup = self.__driver.find_element_by_id("continue")
            if popup.is_displayed():
                self.__driver.find_element_by_id("continue").find_element_by_class_name("btn.btn-blue").click()

            # play video
            WebDriverWait(self.__driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "vjs-big-play-button"))).click()

            # enter full screen mode
            element = self.__driver.find_element_by_class_name("vjs-fullscreen-control.vjs-control.vjs-button")
            self.__driver.execute_script("arguments[0].click();", element)

            # element = self.__driver.find_element_by_css('div[class*="vjs-fullscreen-control.vjs-control.vjs-button"]')
            # webdriver.ActionChains(self.__driver).move_to_element(element).click(element).perform()
            time.sleep(2)

            while self.playing():
                time.sleep(1)

            # exit full screen
            element = self.__driver.find_element_by_class_name("vjs-fullscreen-control.vjs-control.vjs-button")
            self.__driver.execute_script("arguments[0].click();", element)
        except TimeoutException:
            pass

    def playing(self) -> bool:
        """
            check if the video is still playing
        :return: True if the remaining time of the video is bigger then 30 seconds, else False
        """
        try:
            element = self.__driver.find_element_by_class_name("vjs-remaining-time-display")
            t = element.get_attribute('innerText').split(":")
            remaining_time = to_sec(t)
            return remaining_time > 30
        except ElementNotVisibleException:
            return True
