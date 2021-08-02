class PlayerException(Exception):
    """
        Base class for all player errors
    """
    def __init__(self, err_msg: str):
        super().__init__(err_msg)


class EndOfSeries(PlayerException):
    """
        raised when the last episode of the last season of the series has ended
    """
    def __init__(self):
        super().__init__("Last episode of series ended - nothing else to play here")


class ChromeExited(PlayerException):
    """
        raised when chromedriver is unexpectedly exited
    """
    def __init__(self):
        super().__init__("Chrome player has unexpectedly exited")
