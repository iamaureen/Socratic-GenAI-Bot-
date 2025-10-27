"""
Student response processor for pairing bot responses with student queries.
This module handles the pairing logic for each user, skipping first and last interactions.
"""

import pandas as pd
from typing import List, Dict, Tuple
import json
import time
from prompt_builder import build_student_response_classification_prompt
from llm_utils import process_llm_response


def read_input_file(file_path: str) -> pd.DataFrame:
    """
    Read the input CSV file and return the DataFrame.
    
    Args:
        file_path: Path to the input CSV file
    
    Returns:
        DataFrame with all columns from the input file
    """
    return pd.read_csv(file_path)


def pair_bot_student_interactions(df: pd.DataFrame) -> List[Dict[str, any]]:
    """
    Pair bot responses with student queries for each user.
    Skips first and last interaction IDs for each user as they are invalid.
    
    Args:
        df: DataFrame containing all interactions
    
    Returns:
        List of dictionaries containing paired interactions
    """
    paired_interactions = []
    
    # Group interactions by user (Asurite)
    user_groups = df.groupby('Asurite')
    
    for user_id, user_df in user_groups:
        print(f"Processing user: {user_id}")
        
        # Sort by Interaction ID to maintain chronological order
        # Extract numeric part for proper sorting
        user_df['sort_key'] = user_df['Interaction ID'].str.extract(r'(\d+)$').astype(int)
        user_df_sorted = user_df.sort_values('sort_key')
        
        # Get bot responses and student queries for this user
        user_bot_responses = user_df_sorted[user_df_sorted['Interaction Type'] == 'Bot Response']
        user_student_queries = user_df_sorted[user_df_sorted['Interaction Type'] == 'Student Query']
        
        print(f"  Total bot responses: {len(user_bot_responses)}")
        print(f"  Total student queries: {len(user_student_queries)}")
        
        # Skip first student (invalid) and last bot (no pair possible)
        if len(user_bot_responses) > 0 and len(user_student_queries) > 1:
            # Remove first student query (invalid)
            user_student_queries_filtered = user_student_queries.iloc[1:]
            # Remove last bot response (no student to pair with)
            user_bot_responses_filtered = user_bot_responses.iloc[:-1]
            
            print(f"  After filtering - Bot responses: {len(user_bot_responses_filtered)}")
            print(f"  After filtering - Student queries: {len(user_student_queries_filtered)}")
            
            # Pair bot responses with student queries
            min_length = min(len(user_bot_responses_filtered), len(user_student_queries_filtered))
            
            for i in range(min_length):
                bot_response = user_bot_responses_filtered.iloc[i]
                student_query = user_student_queries_filtered.iloc[i]
                
                # Create paired interaction
                paired_interaction = {
                    'user_id': user_id,
                    'pair_index': i + 1,
                    'bot_interaction_id': bot_response['Interaction ID'],
                    'student_interaction_id': student_query['Interaction ID'],
                    'bot_text': bot_response['Text'],
                    'student_text': student_query['Text'],
                    'bot_timestamp': bot_response.get('Timestamp', ''),
                    'student_timestamp': student_query.get('Timestamp', ''),
                    'paired_text': f"Bot Response: {bot_response['Text']}\n\nStudent Query: {student_query['Text']}"
                }
                
                paired_interactions.append(paired_interaction)
                
                print(f"    Pair {i+1}: {bot_response['Interaction ID']} + {student_query['Interaction ID']}")
        else:
            print(f"  Skipping user {user_id} - insufficient interactions for pairing (need at least 1 bot response and 2 student queries)")
    
    return paired_interactions




def analyze_student_responses_with_llm(paired_interactions: List[Dict[str, any]], model) -> Dict[str, Dict[str, any]]:
    """
    Analyze student responses using LLM and return results mapped by student interaction ID.
    
    Args:
        paired_interactions: List of paired bot-student interactions
        model: The LLM model configuration
    
    Returns:
        Dictionary mapping student interaction IDs to their analysis results
    """
    student_analysis_results = {}
    
    print(f"\n=== Analyzing Student Responses with LLM ===")
    print(f"Processing {len(paired_interactions)} bot-student pairs...")
    
    for i, pair in enumerate(paired_interactions):
        student_interaction_id = pair['student_interaction_id']
        paired_text = pair['paired_text']
        
        print(f"Processing pair {i+1}/{len(paired_interactions)}: {student_interaction_id}")
        print(f"Bot: {pair['bot_interaction_id']}")
        print(f"Student: {student_interaction_id}")
        print(f"Student text: {pair['student_text'][:100]}...")
        
        # Build prompt and process with LLM
        llm_prompt = build_student_response_classification_prompt(pair)
        result = process_llm_response(model, llm_prompt, "student", student_interaction_id, paired_text)
        
        # Store result with student interaction ID as key
        student_analysis_results[student_interaction_id] = result
    
    print(f"✓ Completed LLM analysis for {len(student_analysis_results)} student responses")
    return student_analysis_results


def enhance_dataframe_with_student_analysis(df: pd.DataFrame, student_analysis_results: Dict[str, Dict[str, any]]) -> pd.DataFrame:
    """
    Enhance the original DataFrame with student analysis results.
    
    Args:
        df: Original DataFrame with all columns
        student_analysis_results: Dictionary mapping student interaction IDs to analysis results
    
    Returns:
        Enhanced DataFrame with student analysis columns
    """
    enhanced_df = df.copy()
    
    # Initialize student analysis columns with empty values
    enhanced_df['labels'] = ''
    enhanced_df['reasoning'] = ''
    enhanced_df['label_count'] = 0
    
    # Process student queries using interaction ID lookup
    student_query_rows = enhanced_df[enhanced_df['Interaction Type'] == 'Student Query']
    processed_count = 0
    
    for idx, row in student_query_rows.iterrows():
        interaction_id = row['Interaction ID']
        
        # Look up analysis result by interaction ID
        if interaction_id in student_analysis_results:
            result = student_analysis_results[interaction_id]
            
            # Extract assigned labels
            assigned_labels = result.get('assigned_labels', [])
            if assigned_labels:
                # Extract just the label names
                label_names = [label_data.get('label', '') for label_data in assigned_labels]
                # Extract just the reasoning
                reasoning_texts = [label_data.get('reasoning', '') for label_data in assigned_labels]
                
                enhanced_df.loc[idx, 'labels'] = '; '.join(label_names)
                enhanced_df.loc[idx, 'reasoning'] = '; '.join(reasoning_texts)
                enhanced_df.loc[idx, 'label_count'] = len(assigned_labels)
            else:
                enhanced_df.loc[idx, 'labels'] = 'No labels assigned'
                enhanced_df.loc[idx, 'reasoning'] = 'No reasoning provided'
                enhanced_df.loc[idx, 'label_count'] = 0
            
            processed_count += 1
    
    print(f"✓ Enhanced {processed_count} student interactions with analysis results")
    return enhanced_df




def process_all_users_student_analysis(input_file_path: str, model, output_file_path: str = "Output/all_users_student_analysis.csv") -> pd.DataFrame:
    """
    Process all users' student responses with LLM analysis and output to CSV.
    Similar to test_first_user_student_analysis but for all users.
    
    Args:
        input_file_path: Path to the input CSV file
        model: The LLM model configuration
        output_file_path: Path where to save the CSV file
    
    Returns:
        Enhanced DataFrame with student analysis
    """
    # Start timing
    start_time = time.time()
    print("=== Processing All Users Student Response Analysis ===")
    
    # Read input file
    print(f"Reading input file: {input_file_path}")
    df = read_input_file(input_file_path)
    print(f"Total rows in dataset: {len(df)}")
    
    # Check if required columns exist
    required_columns = ['Asurite', 'Interaction ID', 'Interaction Type', 'Text']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        return df
    
    # Get unique users
    unique_users = df['Asurite'].unique()
    print(f"Found {len(unique_users)} unique users: {list(unique_users)}")
    
    # Pair bot and student interactions for all users
    print(f"\n=== Pairing Bot and Student Interactions for All Users ===")
    paired_interactions = pair_bot_student_interactions(df)
    
    if not paired_interactions:
        print("No paired interactions found.")
        return df
    
    print(f"Found {len(paired_interactions)} total paired interactions across all users")
    
    
    # Analyze student responses with LLM
    print(f"\n=== Analyzing Student Responses with LLM ===")
    student_analysis_results = analyze_student_responses_with_llm(paired_interactions, model)
    
    # Enhance DataFrame with analysis results
    print(f"\n=== Enhancing DataFrame with Analysis Results ===")
    enhanced_df = enhance_dataframe_with_student_analysis(df, student_analysis_results)
    
    # Save results to CSV
    print(f"\n=== Saving Results ===")
    import os
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    enhanced_df.to_csv(output_file_path, index=False)
    print(f"Enhanced data saved to {output_file_path}")
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Total users processed: {len(unique_users)}")
    print(f"Total paired interactions: {len(paired_interactions)}")
    print(f"Student interactions analyzed: {len(student_analysis_results)}")
    print(f"Enhanced data with {len(enhanced_df)} rows saved to {output_file_path}")
    
    # Show label distribution
    student_rows = enhanced_df[enhanced_df['Interaction Type'] == 'Student Query']
    if len(student_rows) > 0:
        students_with_labels = len(student_rows[student_rows['label_count'] > 0])
        print(f"\nOverall Label Distribution:")
        print(f"- Students with labels: {students_with_labels}/{len(student_rows)}")
        print(f"- Average labels per student: {student_rows['label_count'].mean():.1f}")
        
        # Show most common labels across all users
        all_labels = []
        for idx, row in student_rows.iterrows():
            if row['labels'] != 'No labels assigned':
                labels_text = row['labels']
                label_names = [label.strip() for label in labels_text.split(';')]
                all_labels.extend(label_names)
        
        if all_labels:
            from collections import Counter
            label_counts = Counter(all_labels)
            print(f"\nMost Common Labels Across All Users:")
            for label, count in label_counts.most_common(10):
                print(f"  - {label}: {count}")
        
        # Show label distribution by user
        print(f"\nLabel Distribution by User:")
        for user_id in unique_users:
            user_student_rows = student_rows[enhanced_df['Asurite'] == user_id]
            if len(user_student_rows) > 0:
                user_students_with_labels = len(user_student_rows[user_student_rows['label_count'] > 0])
                avg_labels = user_student_rows['label_count'].mean()
                print(f"  {user_id}: {user_students_with_labels}/{len(user_student_rows)} students with labels (avg: {avg_labels:.1f})")
    
    # Calculate and display execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n Processing completed successfully!")
    print(f"\n Total execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")
    return enhanced_df




if __name__ == "__main__":
    # Process all users' student responses with LLM analysis
    from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_URL
    from ASUllmAPI import ModelConfig
    
    # Define the model
    model = ModelConfig(name="gpt4_1",
                        provider="openai",
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)
    
    input_file = "Input/Chronicles_sequential_interactions.csv"
    output_file = "Output/Chronicles_student_labels.csv"
    
    enhanced_df = process_all_users_student_analysis(input_file, model, output_file)
