from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_URL
from ASUllmAPI import ModelConfig
from prompt_builder import build_bot_response_classification_prompt
from input_processing import (
    input_reader, 
    process_input_with_all_columns, 
    enhance_dataframe_with_analysis, 
    save_enhanced_dataframe
)
from llm_utils import process_llm_response
import pandas as pd
import time

if __name__ == '__main__':
    # Start timing
    start_time = time.time()
    print("=== Bot Response Processor Started ===")
    
    # define the model
    model = ModelConfig(name="gpt4_1",  #llama3_2-90b
                        provider="openai",  #aws
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)

    # Read the input file with all columns preserved
    input_file_path = "Input/Chronicles_sequential_interactions.csv"  # Updated to use new format file
    original_df = process_input_with_all_columns(input_file_path)
    
    # Extract bot responses for processing
    bot_responses = input_reader(input_file_path)

    results = []
    print(f"Processing {len(bot_responses)} bot responses...")
    
    # Get bot response rows for better tracking
    if 'Interaction Type' in original_df.columns:
        bot_response_rows = original_df[original_df['Interaction Type'] == 'Bot Response']
        print(f"Found {len(bot_response_rows)} bot response interactions")
    
    for i, response in enumerate(bot_responses):
        print(f"Processing response {i+1}/{len(bot_responses)}")
        if 'Interaction Type' in original_df.columns:
            interaction_id = bot_response_rows.iloc[i]['Interaction ID'] if i < len(bot_response_rows) else f"response_{i+1}"
            print(f"Interaction ID: {interaction_id}")
        else:
            interaction_id = f"response_{i+1}"
        print(f"Response: {response[:100]}...")  # Show first 100 chars for progress tracking
        
        llm_prompt = build_bot_response_classification_prompt(bot_response=response)
        parsed = process_llm_response(model, llm_prompt, "bot", interaction_id, response)
        results.append(parsed)

    # Enhance the original DataFrame with analysis results
    enhanced_df = enhance_dataframe_with_analysis(original_df, results)
    
    # Save the enhanced DataFrame to Excel
    output_path = "Output/Chronicles_bot_labels.xlsx" #change the output file name here
    save_enhanced_dataframe(enhanced_df, output_path)
    
    # Calculate and display execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\nProcessing complete!")
    print(f"Enhanced data with {len(enhanced_df)} rows saved to {output_path}")
    print(f"Columns in output: {list(enhanced_df.columns)}")
    print(f"\n⏱️  Total execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")