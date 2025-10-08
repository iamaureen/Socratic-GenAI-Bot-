import configparser

config = configparser.ConfigParser(interpolation=None)
config.read('credentials.conf')

TEST_LLMs_API_ACCESS_TOKEN = config.get('TEST', 'access_token')
TEST_LLMs_REST_API_URL = config.get('TEST', 'rest_api_url')
TEST_LLMs_REST_API_PROVIDERS_URL = config.get('TEST', 'model_list_endpoint')
TEST_LLMs_WS_URL = config.get('TEST', 'ws_url')
