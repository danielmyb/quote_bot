# Database directory

Inside this directory all data is stored that has to be saved persistently.\
The token for the bot has to be stored inside a ``.token`` file inside this directory
as plain text.

The directory also contains the localization file (``localization.json``).
This file contains all dialog strings that are used inside the bot.

#### Localization example:

```json
{
  "languages": {
    "Deutsch": "DE",
    "English": "EN"
  },
  "yes": {
    "DE": "Ja",
    "EN": "Yes"
  },
  "no": {
    "DE": "Nein",
    "EN": "No"
  },
  "greeting": {
    "DE": "Hallo {USERNAME}!",
    "EN": "Hello {USERNAME}!"
  }
}
```

To add a new language the language and its code have to be added to the ``languages`` entry.
For example you could add French like this:
```json
"languages": {
    "Deutsch": "DE",
    "English": "EN",
    "French": "FR"
  }
```

Note that the language codes are limited to exactly **two** characters.

For adding a new translation you have to add an entry under the keyword like this:
```json
"yes": {
    "DE": "Ja",
    "EN": "Yes",
    "FR": "Oui"
  },
```

If there is no entry for a language the default language is used (currently German).