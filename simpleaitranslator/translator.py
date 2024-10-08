import asyncio
from openai import AsyncAzureOpenAI
from openai import AsyncOpenAI
from simpleaitranslator.exceptions import MissingAPIKeyError, NoneAPIKeyProvidedError, InvalidModelName
from simpleaitranslator.utils.enums import ModelForTranslator
from pydantic import BaseModel

from simpleaitranslator.utils.iso639_1 import iso_639_1_codes
from simpleaitranslator.utils.text_splitter import split_text_to_chunks, get_first_n_words
from typing import Optional
from abc import ABC, abstractmethod
CHATGPT_MODEL_NAME = ModelForTranslator.BEST_BIG_MODEL
global_client = None
MAX_LENGTH = 1000
MAX_LENGTH_MINI_TEXT_CHUNK = 128


class Translator(ABC):
    class TextLanguageFormat(BaseModel):
        language_ISO_639_1_code: str

    class TranslateFormat(BaseModel):
        translated_text: str

    class HowManyLanguages(BaseModel):
        number_of_languages: int

    class TextLanguage(BaseModel):
        language_ISO_639_1_code: str
        language_name: str

    def __init__(self):
        self.client = None
        self.chatgpt_model_name = None
        self.max_length = MAX_LENGTH
        self.max_length_mini_text_chunk = MAX_LENGTH_MINI_TEXT_CHUNK

    @abstractmethod
    def _set_api_key(self):
        pass

    @abstractmethod
    def _set_llm(self, chatgpt_model_name):
        pass

    async def async_get_text_language(self, text) -> TextLanguage:
        text = get_first_n_words(text, self.max_length)
        messages = [
            {"role": "system", "content": f"You are a language detector. You should return only the ISO 639-1 code of the text provided by user. All ISO-639-1 codes you can find here:\n {iso_639_1_codes}"},
            {"role": "user", "content": text}
        ]

        response = await self.client.beta.chat.completions.parse(
            model=self.chatgpt_model_name.value,
            messages=messages,
            response_format=Translator.TextLanguageFormat  # auto is default, but we'll be explicit
        )

        response_message = response.choices[0].message.parsed.language_ISO_639_1_code
        detected_language = Translator.TextLanguage(
            language_ISO_639_1_code=response_message,
            language_name=iso_639_1_codes[response_message]
        )
        return detected_language

    def get_text_language(self, text: str) -> TextLanguage:
        """
        Detects the language of a given text using a specified ChatGPT model (ISO 639-1 code).

        Parameters:
        -----------
        Required:
        - text : str
            The text to detect the language of.

        Optional:
        - chatgpt_model_name : Optional[ChatGPTModelForTranslator], optional
            ChatGPT model for language detection. Default is None.
        - open_ai_api_key_for_this_translation : Optional[str], optional
            OpenAI API key for the translation. Default is None.

        Returns:
        --------
        str
            ISO 639-1 code of the detected language.

        """
        result = asyncio.run(self.async_get_text_language(text))
        return result

    async def translate_chunk_of_text(self, text_chunk: str, to_language: str) -> str:
        if not self.client:
            raise MissingAPIKeyError()

        messages = [
            {"role": "system",
             "content": f"You are a language translator. You should translate text provided by user to the {to_language} language. Don't write additional message like This is translated text just translate text."},
            {"role": "user", "content": text_chunk}
        ]

        response = await self.client.beta.chat.completions.parse(
            model=self.chatgpt_model_name.value,
            messages=messages,
            response_format=Translator.TranslateFormat  # auto is default, but we'll be explicit
        )

        response_message = response.choices[0].message.parsed.translated_text
        return response_message


    async def async_translate_text(self, text: str, to_language ="eng") -> str:
        text_chunks = split_text_to_chunks(text, self.max_length)

        # Run how_many_languages_are_in_text concurrently
        # Chunks that contain more than one language will be split (this will simplify translation for the LLM)
        counted_number_of_languages = await asyncio.gather(*[self.how_many_languages_are_in_text(text_chunk) for text_chunk in text_chunks])

        tasks = []
        for index, text_chunk in enumerate(text_chunks):
            if counted_number_of_languages[index] > 1:
                mini_text_chunks = split_text_to_chunks(text_chunk, self.max_length_mini_text_chunk)
                for mini_text_chunk in mini_text_chunks:
                    tasks.append(self.translate_chunk_of_text(mini_text_chunk, to_language))
            else:
                tasks.append(self.translate_chunk_of_text(text_chunk, to_language))

        translated_list = await asyncio.gather(*tasks)
        return " ".join(translated_list)

    def translate(self, text, to_language="eng") -> str: #ISO 639-1
        """
        Translates the given text to the specified language.

        Required Parameters:
        --------------------
        text (str):
            The text to be translated.

        to_language (str):
            The target language code (ISO 639-1). Default is "eng" (English).

        Optional Parameters:
        --------------------
        chatgpt_model_name (Optional[ChatGPTModelForTranslator]):
            The specific ChatGPT model to be used for this translation request.
            If not provided, the global/default model will be used.

            Line to import enums:
            from simpleaitranslator.utils.enums import ChatGPTModel

            Recommended enums are:
            - ChatGPTModelForTranslator.BEST_BIG_MODEL
            - ChatGPTModelForTranslator.BEST_SMALL_MODEL

        open_ai_api_key_for_this_translation (Optional[str]):
            An optional API key for OpenAI to be used specifically for this translation request.
            This is useful if you want to override the global API key for this particular request.
            Note that this will only work with the OpenAI client, not with the AzureOpenAI client.

        Returns:
        --------
        str:
            The translated text.
        """
        translated_text = asyncio.run(self.async_translate_text(text, to_language))
        return translated_text

    async def how_many_languages_are_in_text(self, text: str) -> int:
        completion = await self.client.beta.chat.completions.parse(
            model=self.chatgpt_model_name.value,
            messages=[
                {"role": "system",
                 "content": "You are text languages counter you should count how many languaes are in provided by user text"},
                {"role": "user", "content": f"Please count how many languaes are in this text:\n{text}"},
            ],
            response_format=Translator.HowManyLanguages,
        )
        event = completion.choices[0].message.parsed.number_of_languages
        return event


class TranslatorOpenAI(Translator):
    def __init__(self, open_ai_api_key, chatgpt_model_name=ModelForTranslator.BEST_BIG_MODEL.value):
        self._set_api_key(open_ai_api_key)
        self._set_llm(chatgpt_model_name)
        self.max_length = MAX_LENGTH
        self.max_length_mini_text_chunk = MAX_LENGTH_MINI_TEXT_CHUNK


    def _set_api_key(self, api_key):
        """
        Sets the API key for the OpenAI client.

        Parameters:
        api_key (str): The API key for authenticating with the OpenAI API.

        Raises:
        NoneAPIKeyProvidedError: If the api_key is empty or None.
        """
        if not api_key:
            raise NoneAPIKeyProvidedError()
        self.client = AsyncOpenAI(api_key=api_key)

    def _set_llm(self, chatgpt_model_name: str):
        """
        Sets the default ChatGPT model.

        This function allows you to change the default ChatGPT model used in the application.

        Parameters:
        chatgpt_model_name (str): The name of the ChatGPT model to set.

        Raises:
        InvalidModelName: If the provided model name is not valid.
        ValueError: If the chatgpt_model_name is None or in an incorrect format.
        """

        def validate_model(model_to_check: str) -> None:
            if model_to_check not in {model.value for model in ModelForTranslator}:
                raise InvalidModelName(invalid_model_name=model_to_check)

        if isinstance(chatgpt_model_name, str):
            validate_model(chatgpt_model_name)
            self.chatgpt_model_name = ModelForTranslator(chatgpt_model_name)
        else:
            raise ValueError('chatgpt_model_name is required - current value is None or has wrong format')



class TranslatorAzureOpenAI(TranslatorOpenAI):
    def __init__(self, azure_endpoint: str, api_key: str, api_version: str, azure_deployment: str, chatgpt_model_name=ModelForTranslator.BEST_BIG_MODEL.value):
        self._set_api_key(azure_endpoint, api_key, api_version, azure_deployment)
        self._set_llm(chatgpt_model_name)
        self.max_length = MAX_LENGTH
        self.max_length_mini_text_chunk = MAX_LENGTH_MINI_TEXT_CHUNK

    def _set_api_key(self,azure_endpoint: str, api_key: str, api_version: str, azure_deployment: str):
        """
        Sets the API key and related parameters for the Azure OpenAI client.

        Parameters:
        azure_endpoint (str): The endpoint URL for the Azure OpenAI service.
        api_key (str): The API key for authenticating with the Azure OpenAI API.
        api_version (str): The version of the Azure OpenAI API to use.
        azure_deployment (str): The specific deployment of the Azure OpenAI service.

        Raises:
        NoneAPIKeyProvidedError: If the api_key is empty or None.
        ValueError: If azure_endpoint, api_version, or azure_deployment are empty or None.
        """
        if not api_key:
            raise NoneAPIKeyProvidedError()
        if not azure_deployment:
            raise ValueError('azure_deployment is required - current value is None')
        if not api_version:
            raise ValueError('api_version is required - current value is None')
        if not azure_endpoint:
            raise ValueError('azure_endpoint is required - current value is None')
        self.client = AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version,
            azure_deployment=azure_deployment
        )


'''
#Not supported yet waiting for LLM update
class TranslatorMistral(Translator):
    def __init__(self, open_ai_api_key, chatgpt_model_name=ModelForTranslator.MISTRAL_LARGE.value):
        self._set_api_key(open_ai_api_key)
        self._set_llm(chatgpt_model_name)
        self.max_length = MAX_LENGTH
        self.max_length_mini_text_chunk = MAX_LENGTH_MINI_TEXT_CHUNK

    def _set_api_key(self, api_key):
        """
        Sets the API key for the OpenAI client.

        Parameters:
        api_key (str): The API key for authenticating with the OpenAI API.

        Raises:
        NoneAPIKeyProvidedError: If the api_key is empty or None.
        """
        if not api_key:
            raise NoneAPIKeyProvidedError()
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1") # mistral

    def _set_llm(self, chatgpt_model_name: str):
        """
        Sets the default ChatGPT model.

        This function allows you to change the default ChatGPT model used in the application.

        Parameters:
        chatgpt_model_name (str): The name of the ChatGPT model to set.

        Raises:
        InvalidModelName: If the provided model name is not valid.
        ValueError: If the chatgpt_model_name is None or in an incorrect format.
        """

        def validate_model(model_to_check: str) -> None:
            if model_to_check not in {model.value for model in ModelForTranslator}:
                raise InvalidModelName(invalid_model_name=model_to_check)

        if isinstance(chatgpt_model_name, str):
            validate_model(chatgpt_model_name)
            self.chatgpt_model_name = ModelForTranslator(chatgpt_model_name)
        else:
            raise ValueError('chatgpt_model_name is required - current value is None or has wrong format')

'''




