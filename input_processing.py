import pandas as pd
import json
from typing import List, Dict, Any


def input_reader(filePath: str) -> List[str]:
    """
    Read CSV file and extract bot responses as a list.
    Handles both old format (Bot Response column) and new format (Interaction Type + Text columns).
    """
    # Read the CSV file
    df = pd.read_csv(filePath)

    # Check if it's the new format (has Interaction Type column)
    if 'Interaction Type' in df.columns:
        # New format: filter for Bot Response interactions and extract Text
        bot_responses_df = df[df['Interaction Type'] == 'Bot Response']
        bot_responses = bot_responses_df['Text'].tolist()
    else:
        # Old format: extract the Bot Response column
        bot_responses = df['Bot Response'].tolist()

    return bot_responses


def process_input_with_all_columns(filePath: str) -> pd.DataFrame:
    """
    Read CSV file and return the entire DataFrame with all columns preserved.
    This function is used for comprehensive processing that maintains all original data.
    """
    # Read the CSV file
    df = pd.read_csv(filePath)
    
    return df


def enhance_dataframe_with_analysis(df: pd.DataFrame, analysis_results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Enhance the original DataFrame with analysis results from prompt_builder.
    Handles both old and new formats, ensuring labels are correctly matched to bot responses.
    
    Args:
        df: Original DataFrame with all columns
        analysis_results: List of analysis results from prompt_builder processing
    
    Returns:
        Enhanced DataFrame with original columns plus analysis columns
    """
    # Create a copy of the original DataFrame
    enhanced_df = df.copy()
    
    # Initialize analysis columns with empty values
    enhanced_df['original_text'] = ''
    enhanced_df['non_question_part'] = ''
    enhanced_df['question_part'] = ''
    enhanced_df['socratic_label'] = ''
    enhanced_df['rationale'] = ''
    enhanced_df['confidence'] = 0.0
    
    # Check if it's the new format (has Interaction Type column)
    if 'Interaction Type' in df.columns:
        # New format: match analysis results to Bot Response rows using Interaction ID
        bot_response_rows = df[df['Interaction Type'] == 'Bot Response']
        
        # Create a mapping from Interaction ID to analysis results
        analysis_index = 0
        for idx, row in bot_response_rows.iterrows():
            if analysis_index < len(analysis_results):
                result = analysis_results[analysis_index]
                enhanced_df.loc[idx, 'original_text'] = result.get('original_text', '')
                enhanced_df.loc[idx, 'non_question_part'] = result.get('non_question_part', '')
                enhanced_df.loc[idx, 'question_part'] = result.get('question_part', '')
                enhanced_df.loc[idx, 'socratic_label'] = result.get('socratic_label', '')
                enhanced_df.loc[idx, 'rationale'] = result.get('rationale', '')
                enhanced_df.loc[idx, 'confidence'] = result.get('confidence', 0.0)
                analysis_index += 1
    else:
        # Old format: apply analysis results to all rows (assuming all are bot responses)
        for i, result in enumerate(analysis_results):
            if i < len(enhanced_df):
                enhanced_df.iloc[i]['original_text'] = result.get('original_text', '')
                enhanced_df.iloc[i]['non_question_part'] = result.get('non_question_part', '')
                enhanced_df.iloc[i]['question_part'] = result.get('question_part', '')
                enhanced_df.iloc[i]['socratic_label'] = result.get('socratic_label', '')
                enhanced_df.iloc[i]['rationale'] = result.get('rationale', '')
                enhanced_df.iloc[i]['confidence'] = result.get('confidence', 0.0)
    
    return enhanced_df


def save_enhanced_dataframe(df: pd.DataFrame, output_path: str) -> None:
    """
    Save the enhanced DataFrame to an Excel file.
    
    Args:
        df: Enhanced DataFrame to save
        output_path: Path where to save the Excel file
    """
    # Create output directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to Excel
    df.to_excel(output_path, index=False)
    print(f"Enhanced data saved to {output_path}")
