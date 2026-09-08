# Secret Words

This document describes where **Discord Impostor Bot** gets its secret words, how the word data is organized, and how the available words are selected.

v2.0.0 uses a static word catalogue stored outside the application source code.

## Words File

Secret words are stored in:

```text
data/words.json
```

Keeping the word catalogue outside `src/` allows the available words to be maintained without modifying the application code.

## Data Format

The file uses JSON.

Its root object contains categories, and each category contains a list of available words.

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

Each category name acts as the key used to access its word list.

## Default Category

The current default category is:

```text
general
```

When no specific category is requested, words are selected from this category.

Category selection is not currently exposed through the Discord interface.

## Word Selection

A word is selected randomly from the requested category.

For example, given:

```json
{
  "general": [
    "pizza",
    "beach",
    "dog"
  ]
}
```

a selection may return:

```text
pizza
```

Each selection must return one of the words available in that category.

## Adding Words

To add words, edit `data/words.json` and append them to the appropriate category.

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

Keep the existing category structure and ensure the resulting file remains valid JSON.

## Adding Categories

Additional categories can be added to the same file.

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

Adding a category to the file does not automatically expose it as a selectable option in Discord.

The bot continues using the default category unless another category is explicitly requested by the application.

## Data Requirements

The word catalogue must satisfy the following conditions:

| Requirement        | Description                                         |
| ------------------ | --------------------------------------------------- |
| File exists        | `data/words.json` must be available                 |
| Valid JSON         | The file must be parseable as JSON                  |
| Object root        | The JSON root must contain the category mapping     |
| Category exists    | A requested category must exist                     |
| Non-empty category | A category must contain at least one available word |

If the word catalogue cannot provide a valid word, word selection fails instead of returning an invalid value.

## Common Failure Cases

| Case                               | Result                                     |
| ---------------------------------- | ------------------------------------------ |
| Words file is missing              | Words cannot be loaded                     |
| Words file contains no usable data | Words cannot be loaded                     |
| JSON structure is invalid          | Words cannot be loaded correctly           |
| Requested category does not exist  | No word can be selected from that category |
| Requested category is empty        | No word can be selected                    |

These failures are handled by the word-loading/provider boundary rather than by returning arbitrary fallback words.

## Recommendations

When maintaining the catalogue:

* prefer familiar words that players can describe indirectly;
* avoid unnecessarily obscure or highly specialized terms;
* avoid duplicate entries where possible;
* keep categories semantically coherent;
* maintain enough variety in the `general` category;
* validate the JSON after large edits.

## Related Documentation

* [`rules.md`](rules.md) describes the game rules involving secret information.
* [`game-flow.md`](game-flow.md) describes when word selection occurs during a game.
* [`architecture.md`](architecture.md) describes the technical word-provider boundary.
