# Secret Words

This document describes how **Impostor Discord Bot** loads, organizes, and uses secret words during a game.

Words are stored in an external JSON file to keep them separate from the bot's source code.

---

## Words File

Game words are stored in:

```text
data/words.json
```

This file is located outside `src/` because it belongs to the project's configurable data.

---

## Expected Format

The file must use valid JSON format.

The expected structure is an object where each key represents a category, and each category contains a list of words.

```json
{
  "general": [
    "pizza",
    "beach",
    "dog"
  ],
  "food": [
    "burger",
    "sushi",
    "empanada"
  ],
  "places": [
    "school",
    "cinema",
    "supermarket"
  ]
}
```

---

## Default Category

Currently, the bot uses the category:

```text
general
```

This category is used when the host starts a game with:

```text
/impostor start
```

For now, the category cannot be selected from Discord. The bot gets a word from the default configured category.

---

## File Rules

| Rule                              | Description                                              |
| --------------------------------- | -------------------------------------------------------- |
| The file must exist               | The bot expects to find `data/words.json`.               |
| The file must be valid JSON       | A formatting error prevents the words from being loaded. |
| The default category must exist   | The `general` category is currently expected.            |
| Each category must contain a list | Words must be stored inside a JSON list.                 |
| Lists must not be empty           | An empty category does not allow the game to start.      |
| Words must be text                | Each word must be written as a string.                   |

---

## Usage During a Game

When this command is executed:

```text
/impostor start
```

the bot performs the following process:

1. loads `data/words.json`;
2. looks for the default category;
3. gets the list of available words;
4. selects a random word;
5. sends that word to regular players by direct message;
6. selects one impostor, who does not receive the secret word.

The secret word is never shown in the public channel.

---

## Selection Example

If the file contains:

```json
{
  "general": [
    "pizza",
    "beach",
    "dog"
  ]
}
```

the bot may randomly select a word such as:

```text
pizza
```

Regular players receive that word by direct message.

The impostor receives a message indicating that they are the impostor, but does not know the secret word.

---

## Editing the File

To add new words, edit `data/words.json` and add items to the corresponding category.

```json
{
  "general": [
    "pizza",
    "beach",
    "dog",
    "library",
    "mountain"
  ]
}
```

After modifying the file, save the changes and restart the bot if it is already running.

---

## Additional Categories

The file can contain more than one category.

```json
{
  "general": [
    "pizza",
    "beach",
    "dog"
  ],
  "objects": [
    "pencil",
    "backpack",
    "clock"
  ]
}
```

As long as the bot does not have an option to choose a category from Discord, it will continue using the default category.

---

## Handled Errors

| Case                        | Expected Result                                               |
| --------------------------- | ------------------------------------------------------------- |
| The file does not exist     | The bot reports that the words file was not found.            |
| The file is empty           | The bot reports that there is no valid data.                  |
| The JSON format is invalid  | The bot cannot load the words.                                |
| The category does not exist | The bot reports that the requested category is not available. |
| The category is empty       | The bot reports that there are no available words.            |

If one of these errors occurs, the game should not start.

---

## Recommendations

To keep the file organized:

* use short words that are easy to relate to;
* avoid overly specific words;
* avoid concepts that are too difficult for the group;
* check that the JSON does not have punctuation errors;
* keep enough words in the `general` category;
* group words by category if the bot is expanded later.

---

## Complete Example

```json
{
  "general": [
    "pizza",
    "beach",
    "dog",
    "hospital",
    "airplane",
    "school",
    "mountain",
    "cinema"
  ],
  "food": [
    "burger",
    "sushi",
    "empanada",
    "ice cream"
  ],
  "places": [
    "library",
    "stadium",
    "supermarket",
    "airport"
  ]
}
```
