import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WORDS_FILE = BASE_DIR / "data" / "words.json"
DEFAULT_CATEGORY = "general"

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


def load_words() -> dict[str, list[str]]:
    if not WORDS_FILE.exists():
        raise WordsFileNotFoundError(
            f"Words file not found: {WORDS_FILE}"
        )

    with open(WORDS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict) or not data:
        raise EmptyWordsFileError(
            f"Words file is empty or not in the expected format."
        )

    return data


def get_words_by_category(category: str = DEFAULT_CATEGORY) -> list[str]:
    words_data = load_words()

    if category not in words_data:
        raise CategoryNotFoundError(
            f"Category '{category}' not found in the words file."
        )

    words = words_data[category]

    if not isinstance(words, list) or not words:
        raise EmptyCategoryError(
            f"Category '{category}' exists but contains no words."
        )

    return words


def get_random_word(category: str = DEFAULT_CATEGORY) -> str:
    words = get_words_by_category(category)
    return random.choice(words)