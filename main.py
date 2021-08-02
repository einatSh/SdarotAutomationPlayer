from presentation.Controller import Controller

"""
    This repo is using chromedriver for windows - documentation: https://chromedriver.chromium.org/
    After downloading chromedriver, change the path in the var chromedriver_path to the new path
"""

if __name__ == '__main__':
    chromedriver_path = "resource/chromedriver.exe"
    bot = Controller(chromedriver_path)
    bot.start()
