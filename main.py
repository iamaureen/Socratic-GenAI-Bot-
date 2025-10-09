from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_URL
from ASUllmAPI import ModelConfig, query_llm
from prompt_builder import build_bot_response_classification_prompt
from input_processing import (
    input_reader, 
    process_input_with_all_columns, 
    enhance_dataframe_with_analysis, 
    save_enhanced_dataframe
)
import json
import pandas as pd

if __name__ == '__main__':
    # define the model
    model = ModelConfig(name="gpt4_1",  #llama3_2-90b
                        provider="openai",  #aws
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)

    # Read the input file with all columns preserved
    input_file_path = "Input/pilot_-_stem_craft_interactions.csv"
    original_df = process_input_with_all_columns(input_file_path)
    
    # Extract bot responses for processing
    bot_responses = input_reader(input_file_path)

    results = []
    print(f"Processing {len(bot_responses)} bot responses...")
    
    for i, response in enumerate(bot_responses):
        print(f"Processing response {i+1}/{len(bot_responses)}")
        print(f"Response: {response[:100]}...")  # Show first 100 chars for progress tracking
        
        llm_prompt = build_bot_response_classification_prompt(bot_response=response)
        llm_response = query_llm(model=model,
                                 query=llm_prompt,
                                 # number of retries when API call is NOT successful
                                 num_retry=3,
                                 # number of seconds to sleep when API call successful
                                 success_sleep=0.0,
                                 # number of seconds to sleep when API call is NOT successful
                                 fail_sleep=1.0)

        response_text = llm_response.get('response')
        # Expecting strict JSON per instructions above
        try:
            parsed = json.loads(response_text) if isinstance(response_text, str) else response_text
        except Exception:
            # If the model returned code fences or stray text, try to salvage the JSON substring
            if isinstance(response_text, str):
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1 and end > start:
                    parsed = json.loads(response_text[start:end + 1])
                else:
                    raise
            else:
                raise

        results.append(parsed)

    # Enhance the original DataFrame with analysis results
    enhanced_df = enhance_dataframe_with_analysis(original_df, results)
    
    # Save the enhanced DataFrame to Excel
    output_path = "Output/enhanced_stem_craft_interactions.xlsx"
    save_enhanced_dataframe(enhanced_df, output_path)
    
    print(f"\nProcessing complete!")
    print(f"Enhanced data with {len(enhanced_df)} rows saved to {output_path}")
    print(f"Columns in output: {list(enhanced_df.columns)}")