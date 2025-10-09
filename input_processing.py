import pandas as pd
import json
from typing import List, Dict, Any


def input_reader(filePath: str) -> List[str]:
    """
    Read CSV file and extract bot responses as a list.
    """
    # Read the CSV file
    df = pd.read_csv(filePath)

    # Extract the bot_response column as a list
    bot_responses = df['Bot Response'].tolist()  # dropna removes any missing values

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
    
    Args:
        df: Original DataFrame with all columns
        analysis_results: List of analysis results from prompt_builder processing
    
    Returns:
        Enhanced DataFrame with original columns plus analysis columns
    """
    # Create a copy of the original DataFrame
    enhanced_df = df.copy()
    
    # Add analysis columns
    enhanced_df['original_text'] = [result.get('original_text', '') for result in analysis_results]
    enhanced_df['non_question_part'] = [result.get('non_question_part', '') for result in analysis_results]
    enhanced_df['question_part'] = [result.get('question_part', '') for result in analysis_results]
    enhanced_df['label'] = [result.get('label', '') for result in analysis_results]
    enhanced_df['rationale'] = [result.get('rationale', '') for result in analysis_results]
    enhanced_df['confidence'] = [result.get('confidence', 0.0) for result in analysis_results]
    
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
