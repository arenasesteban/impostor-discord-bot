import json

import pytest

import src.impostor_bot.words.loader as words
from src.impostor_bot.words.loader import (
    load_words,
    get_words_by_category,
    get_random_word,
)
from src.impostor_bot.words.exceptions import (
    WordsFileNotFoundError,
    EmptyWordsFileError,
    CategoryNotFoundError,
    EmptyCategoryError,
)
from src.impostor_bot.constants import DEFAULT_WORD_CATEGORY


@pytest.fixture
def words_file(tmp_path, monkeypatch):
    test_file = tmp_path / "words.json"

    def _create_words_file(content):
        test_file.write_text(
            json.dumps(content, ensure_ascii=False),
            encoding="utf-8",
        )

        monkeypatch.setattr(words, "WORDS_FILE", test_file)

        return test_file

    return _create_words_file


def test_load_words_returns_dictionary(words_file):
    words_file(
        {
            "general": ["pizza", "playa", "perro"]
        }
    )

    data = load_words()

    assert isinstance(data, dict)
    assert data


def test_get_words_by_default_category_returns_list(words_file):
    words_file(
        {
            "general": ["pizza", "playa", "perro"]
        }
    )

    result = get_words_by_category()

    assert isinstance(result, list)
    assert len(result) > 0


def test_get_words_by_existing_category_returns_list(words_file):
    words_file(
        {
            "general": ["pizza", "playa"],
            "comida": ["sushi", "hamburguesa"],
        }
    )

    result = get_words_by_category("comida")

    assert isinstance(result, list)
    assert len(result) > 0
    assert result == ["sushi", "hamburguesa"]


def test_get_random_word_returns_string(words_file):
    words_file(
        {
            "general": ["pizza", "playa", "perro"]
        }
    )

    word = get_random_word()

    assert isinstance(word, str)
    assert len(word) > 0


def test_get_random_word_returns_word_from_category(words_file):
    words_file(
        {
            "general": ["pizza", "playa", "perro"]
        }
    )

    word = get_random_word(DEFAULT_WORD_CATEGORY)

    assert word in ["pizza", "playa", "perro"]


def test_category_not_found_raises_error(words_file):
    words_file(
        {
            "general": ["pizza", "playa"]
        }
    )

    with pytest.raises(CategoryNotFoundError):
        get_words_by_category("categoria_inexistente")


def test_empty_category_raises_error(words_file):
    words_file(
        {
            "general": []
        }
    )

    with pytest.raises(EmptyCategoryError):
        get_words_by_category("general")


def test_missing_words_file_raises_error(tmp_path, monkeypatch):
    missing_file = tmp_path / "missing_words.json"

    monkeypatch.setattr(words, "WORDS_FILE", missing_file)

    with pytest.raises(WordsFileNotFoundError):
        load_words()


def test_empty_words_file_raises_error(words_file):
    words_file({})

    with pytest.raises(EmptyWordsFileError):
        load_words()


def test_invalid_root_format_raises_error(tmp_path, monkeypatch):
    test_file = tmp_path / "words.json"

    test_file.write_text(
        json.dumps(["pizza", "playa"], ensure_ascii=False),
        encoding="utf-8",
    )

    monkeypatch.setattr(words, "WORDS_FILE", test_file)

    with pytest.raises(EmptyWordsFileError):
        load_words()