import pytest

from simpleaitranslator.exceptions import NoneAPIKeyProvidedError
from simpleaitranslator.translator import set_openai_api_key, set_azure_openai_api_key


def test_set_openai_api_key_none_api_key():
    with pytest.raises(NoneAPIKeyProvidedError) as excinfo:
        set_openai_api_key(None)
    assert str(excinfo.value) == "Provide a valid API key. Right now you passed None value to this function"


def test_set_azure_openai_api_key_no_api_key():
    with pytest.raises(NoneAPIKeyProvidedError):
        set_azure_openai_api_key('https://example.com', '', 'v1', 'deployment')

def test_set_azure_openai_api_key_no_azure_deployment():
    with pytest.raises(ValueError, match='azure_deployment is required - current value is None'):
        set_azure_openai_api_key('https://example.com', 'test_api_key', 'v1', None)

def test_set_azure_openai_api_key_no_api_version():
    with pytest.raises(ValueError, match='api_version is required - current value is None'):
        set_azure_openai_api_key('https://example.com', 'test_api_key', '', 'deployment')

def test_set_azure_openai_api_key_no_azure_endpoint():
    with pytest.raises(ValueError, match='azure_endpoint is required - current value is None'):
        set_azure_openai_api_key('', 'test_api_key', 'v1', 'deployment')
