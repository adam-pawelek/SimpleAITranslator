# SimpleAITranslator
[![Test](https://github.com/adam-pawelek/SimpleAITranslator/actions/workflows/test.yml/badge.svg)](https://github.com/adam-pawelek/SimpleAITranslator/actions/workflows/test.yml)
[![Python package - Publish](https://github.com/adam-pawelek/SimpleAITranslator/actions/workflows/publish.yml/badge.svg)](https://github.com/adam-pawelek/SimpleAITranslator/actions/workflows/publish.yml)
[![Python Versions](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12-blue)](https://www.python.org/)
[![PyPI version](https://img.shields.io/pypi/v/simpleaitranslator)](https://pypi.org/project/simpleaitranslator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
## Overview

SimpleAITranslator is a Python library designed to identify the language of a given text and translate text between multiple languages using OpenAI's GPT-4o. The library is especially useful for translating text containing multiple languages into a single target language.

## Features

- **Language Detection:** Identify the language of a given text in ISO 639-3 format.
- **Translation:** Translate text containing multiple languages into another language in ISO 639-3 format.

## Requirements

To use this library, you must have an OpenAI API key. This key allows the library to utilize OpenAI's GPT-4o for translation and language detection.



## Installation

You can install the SimpleAITranslator library from PyPI:

```bash
pip install simpleaitranslator
```

## Usage

### Setting the OpenAI API Key

Before using SimpleAITranslator, you need to set your OpenAI API key. You can do this by calling the `set_openai_api_key` function.

```python
from simpleaitranslator.translator import set_openai_api_key

# Set your OpenAI API key
set_openai_api_key("YOUR_OPENAI_API_KEY")
```

### Setting the Azure OpenAI API Key

If you are using Azure's OpenAI services, you need to set your Azure OpenAI API key along with additional required parameters. Use the `set_azure_openai_api_key` function to do this.

```python
from simpleaitranslator.translator import set_azure_openai_api_key

# Set your Azure OpenAI API key
set_azure_openai_api_key(
    azure_endpoint="YOUR_AZURE_ENDPOINT",
    api_key="YOUR_AZURE_API_KEY",
    api_version="YOUR_API_VERSION",
    azure_deployment="YOUR_AZURE_DEPLOYMENT"
)
```


### Language Detection

To detect the language of a given text:

```python
from simpleaitranslator.translator import get_text_language,set_openai_api_key
set_openai_api_key("YOUR_OPENAI_API_KEY")

print(get_text_language("Hello world"))  # Output: 'eng'
```

### Translation

To translate text containing multiple languages into another language:

```python
from simpleaitranslator.translator import translate, set_openai_api_key
set_openai_api_key("YOUR_OPENAI_API_KEY")

print(translate("Cześć jak się masz? Meu nome é Adam", "eng"))  # Output: "Hello how are you? My name is Adam"
```


### Full Example

Here is a complete example demonstrating how to use the library:

```python
from simpleaitranslator.translator import get_text_language, translate, set_openai_api_key
set_openai_api_key("YOUR_OPENAI_API_KEY")

# Detect language
print(get_text_language("jak ty się nazywasz"))  # Output: 'pol'

# Translate text
print(translate("Cześć jak się masz? Meu nome é Adam", "eng"))  # Output: "Hello how are you? My name is Adam"
```

## Supported Languages

SimpleAITranslator supports all languages supported by GPT-4o. For a complete list of language codes, you can visit the [ISO 639-3 website](https://iso639-3.sil.org/code_tables/639/data).

Here are some of the most popular languages and their ISO 639-3 codes:

- English (eng)
- Spanish (spa)
- French (fra)
- German (deu)
- Chinese (zho)
- Japanese (jpn)
- Korean (kor)
- Portuguese (por)
- Russian (rus)
- Italian (ita)
- Dutch (nld)
- Arabic (ara)
- Hindi (hin)
- Bengali (ben)
- Turkish (tur)
- Polish (pol)
- Swedish (swe)
- Norwegian (nor)
- Danish (dan)
- Finnish (fin)
- Greek (ell)
- Hebrew (heb)

## Additional Resources

- [PyPI page](https://pypi.org/project/simpleaitranslator/)
- [ISO 639-3 Codes](https://iso639-3.sil.org/code_tables/639/data)
- [Github project repository](https://github.com/adam-pawelek/SimpleAITranslator)

## Authors
- Adam Pawełek  
  - [LinkedIn](https://www.linkedin.com/in/adam-roman-pawelek/)  
  - [Email](mailto:adam.pwk@outlook.com)
  


## License

SimpleAITranslator is licensed under the MIT License. See the LICENSE file for more details.


