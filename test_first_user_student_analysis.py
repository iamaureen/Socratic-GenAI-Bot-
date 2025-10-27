#!/usr/bin/env python3
"""
Test script to process only the first user's student queries with LLM labeling.
This is for testing purposes to verify the student response analysis works correctly.
"""

import pandas as pd
from student_response_processor import (
    read_input_file, 
    pair_bot_student_interactions, 
    analyze_student_responses_with_llm,
    enhance_dataframe_with_student_analysis
)
from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_URL
from ASUllmAPI import ModelConfig


def test_first_user_student_analysis():
    """Test student response analysis for the first user only."""
    
    print("=== Testing First User Student Response Analysis ===")
    
    # Define the model
    model = ModelConfig(name="gpt4_1",
                        provider="openai",
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)
    
    # Read input file
    input_file_path = "Input/Chronicles_sequential_interactions.csv"
    print(f"Reading input file: {input_file_path}")
    df = read_input_file(input_file_path)
    print(f"Total rows in dataset: {len(df)}")
    
    # Get first user
    first_user = df['Asurite'].iloc[0]
    print(f"Testing with first user: {first_user}")
    
    # Filter data for first user only
    first_user_df = df[df['Asurite'] == first_user]
    print(f"First user has {len(first_user_df)} interactions")
    
    # Show all interactions for this user
    print(f"\nAll interactions for user {first_user}:")
    first_user_df['sort_key'] = first_user_df['Interaction ID'].str.extract(r'(\d+)$').astype(int)
    first_user_df_sorted = first_user_df.sort_values('sort_key')
    
    for idx, row in first_user_df_sorted.iterrows():
        print(f"  {row['Interaction ID']}: {row['Interaction Type']} - {row['Text'][:50]}...")
    
    # Pair bot and student interactions for first user only
    print(f"\n=== Pairing Bot and Student Interactions for {first_user} ===")
    paired_interactions = pair_bot_student_interactions(first_user_df)
    
    if not paired_interactions:
        print("No paired interactions found for first user.")
        return
    
    print(f"Found {len(paired_interactions)} paired interactions")
    
    # Show the pairs that will be analyzed
    print(f"\nPairs to be analyzed:")
    for i, pair in enumerate(paired_interactions):
        print(f"  Pair {i+1}:")
        print(f"    Bot: {pair['bot_interaction_id']}")
        print(f"    Student: {pair['student_interaction_id']}")
        print(f"    Bot text: {pair['bot_text'][:80]}...")
        print(f"    Student text: {pair['student_text'][:80]}...")
        print()
    
    # Analyze student responses with LLM
    print(f"=== Analyzing Student Responses with LLM ===")
    student_analysis_results = analyze_student_responses_with_llm(paired_interactions, model)
    
    # Show analysis results
    print(f"\n=== LLM Analysis Results ===")
    for student_id, result in student_analysis_results.items():
        print(f"\nStudent ID: {student_id}")
        print(f"Bot message: {result.get('bot_message', '')[:100]}...")
        print(f"Student response: {result.get('student_response', '')[:100]}...")
        
        assigned_labels = result.get('assigned_labels', [])
        if assigned_labels:
            print(f"Assigned labels ({len(assigned_labels)}):")
            for label_data in assigned_labels:
                label_name = label_data.get('label', '')
                reasoning = label_data.get('reasoning', '')
                print(f"  - {label_name}: {reasoning}")
        else:
            print("No labels assigned")
    
    # Enhance DataFrame with analysis results
    print(f"\n=== Enhancing DataFrame with Analysis Results ===")
    enhanced_df = enhance_dataframe_with_student_analysis(first_user_df, student_analysis_results)
    
    # Save results to Excel
    output_file = "Output/test_first_user_student_analysis.xlsx"
    print(f"\n=== Saving Results ===")
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    enhanced_df.to_excel(output_file, index=False)
    print(f"Enhanced data saved to {output_file}")
    
    # Show summary
    print(f"\n=== Test Summary ===")
    print(f"User tested: {first_user}")
    print(f"Total interactions: {len(first_user_df)}")
    print(f"Paired interactions: {len(paired_interactions)}")
    print(f"Student interactions analyzed: {len(student_analysis_results)}")
    print(f"Enhanced data with {len(enhanced_df)} rows saved to {output_file}")
    
    # Show label distribution for this user
    student_rows = enhanced_df[enhanced_df['Interaction Type'] == 'Student Query']
    if len(student_rows) > 0:
        students_with_labels = len(student_rows[student_rows['label_count'] > 0])
        print(f"\nLabel Distribution for {first_user}:")
        print(f"- Students with labels: {students_with_labels}/{len(student_rows)}")
        print(f"- Average labels per student: {student_rows['label_count'].mean():.1f}")
        
        # Show most common labels for this user
        all_labels = []
        for idx, row in student_rows.iterrows():
            if row['labels'] != 'No labels assigned':
                labels_text = row['labels']
                label_names = [label.split(':')[0].strip() for label in labels_text.split(';')]
                all_labels.extend(label_names)
        
        if all_labels:
            from collections import Counter
            label_counts = Counter(all_labels)
            print(f"\nMost Common Labels for {first_user}:")
            for label, count in label_counts.most_common():
                print(f"  - {label}: {count}")
    
    print(f"\n✅ Test completed successfully!")
    return enhanced_df


if __name__ == "__main__":
    # Run the test
    result_df = test_first_user_student_analysis()
