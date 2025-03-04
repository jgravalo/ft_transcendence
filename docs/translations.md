# Adding translations in Pong42

This guide explains how multi-language support works in the application and how to add new translations. The system uses i18n tags in both front-end and back-end templates, and Django's translation framework to manage different languages.

## Overview

The translation system is based on:
- i18n tags in front-end HTML files and back-end templates.
- Translation keys stored in translations.py.
- .po files containing actual translations for each language.
- Django's gettext_lazy (`_()`) for handling translations directly in Python files like views.py.

## 1. Adding Translations Tags

### Option 1: Using i18n Tags in Templates
To make text translatable in front-end and back-end templates, use the `data-i18n` attribute:

```html
<!--Frontend HTML-->
<a href="/" data-i18n="button.home">Home</a>
<!--Backend HTML (Django) in templates-->
<h5 class="modal-title" data-i18n="register.title">Register</h5>
```

These tags reference translation keys `button.home` and `register.title` from translations.py.

Note : If you have different "Login" words in different places/pages, it is better to use different tags like `home.login` and `game.login`. Both will then point to the same translation word in translation keys.


After adding the tags in the templates/views, you need to add the corresponding translations keys in `/back/app/language/translations.py` as such : 

```python
from django.utils.translation import gettext_lazy as _

TRANSLATION_KEYS = {
    "button.home": _( "Home"),
    "register.title": _( "Register"),
}
```

These keys will match the i18n tag (left side) to the actual translation in .po files (right side).

Note : As mentionned before, there can be multiple i18n tags referencing to the same translation in .po file (i.e. `home.login` and `game.login`)

### Option 2: Using gettext_lazy in Python Files
For text that needs to be translated within Python files (e.g., views), use `gettext_lazy`:

```python
from django.utils.translation import gettext_lazy as _

error_messages = {
    'user_not_found': _( "User does not exist"),
}
```

Here gettext will fetch the translation corresponding to the translation key `User does not exist` from translations.py.

## 2. Adding Translations in .po files

Each language has a corresponding .po file inside `/back/app/locale/<lang_code>/LC_MESSAGES/django.po`. These files contain the actual translations.

```
#Example for locale/es/LC_MESSAGES/django.po

#: language/translations.py:4
msgid "Home"
msgstr "Inicio"

#: language/translations.py:6
msgid "Register"
msgstr "Registrarse"

#: language/translations.py:33
msgid "User does not exist"
msgstr "El usuario no existe"
```

Notes on .po Files:
- Line numbers are included for reference but can be ignored.
- You MUST add translations for the 3 languages.
- Make sure not to duplicate words here if they are already translated beforehand.

### 4: Updating Translations
To update and compile translations after making changes:

```python
python manage.py compilemessages
```

This command is called upon building the back container in `init.sh`