class PlayerException(Exception):
    """
        Base class for all player errors
    """
    def __init__(self, err_msg: str):
        super().__init__(err_msg)
    pass


class EndOfSeries(PlayerException):
    """
        raised when the last episode of the last season of the series has ended
    """
    def __init__(self):
        super().__init__("Last episode of series ended - nothing else to play here")
    pass
