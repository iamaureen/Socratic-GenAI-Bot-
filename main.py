from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_URL
from ASUllmAPI import ModelConfig, query_llm

if __name__ == '__main__':
    # define the model
    model = ModelConfig(name="gpt4_1",  #llama3_2-90b
                        provider="openai",  #aws
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)

    query = "define socratic method"

    llm_response = query_llm(model=model,
                             query=query,
                             # number of retries when API call is NOT successful
                             num_retry=3,
                             # number of seconds to sleep when API call successful
                             success_sleep=0.0,
                             # number of seconds to sleep when API call is NOT successful
                             fail_sleep=1.0)

    print(llm_response.get('response'))