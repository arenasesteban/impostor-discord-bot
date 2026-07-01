import random

WORDS = [
    "pizza",
    "playa",
    "perro",
    "hospital",
    "avión",
    "colegio",
    "montaña",
    "cine",
    "fútbol",
    "celular",
    "supermercado",
    "doctor",
    "restaurante",
    "bicicleta",
    "computador",
]


class WordError(Exception):
    """Base class for word-related errors."""


def get_random_word() -> str:
    if not WORDS:
        raise WordError("No words available to select from.") 
    
    return random.choice(WORDS)