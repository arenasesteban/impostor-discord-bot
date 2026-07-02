class WordError(Exception):
    """Base class for word-related errors."""


class WordsFileNotFoundError(WordError):
    """Raised when file is not found."""


class EmptyWordsFileError(WordError):
    """Raised when file is empty or contains invalid data."""


class CategoryNotFoundError(WordError):
    """Raised when the specified category doesn't exist."""


class EmptyCategoryError(WordError):
    """Raised when the specified category exists but is empty."""