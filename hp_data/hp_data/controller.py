class DataController:
    """The controller that decides what data is passed to the frontend"""
    def __init__(self, post):
        self._post = post

        self._parse_fields()

    def _parse_fields():
        """Will parse any selectors out of the fields"""
