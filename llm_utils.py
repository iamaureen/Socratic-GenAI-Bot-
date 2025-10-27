"""
LLM processing utilities for the Socratic GenAI Bot project.
This module contains helper functions for processing LLM responses with error handling.
"""

import json


def process_llm_response(model, prompt, interaction_type, interaction_id, interaction_text, retry_count=3):
    """
    Helper method to process LLM responses with error handling.
    
    Args:
        model: The LLM model configuration
        prompt: The prompt to send to the LLM
        interaction_type: "bot" or "student" for logging
        interaction_id: ID for tracking
        interaction_text: The text being processed
        retry_count: Number of retries for failed API calls
    
    Returns:
        dict: Parsed JSON response or error placeholder
    """
    from ASUllmAPI import query_llm
    
    try:
        llm_response = query_llm(model=model,
                                 query=prompt,
                                 num_retry=retry_count,
                                 success_sleep=0.0,
                                 fail_sleep=1.0)

        response_text = llm_response.get('response')
        
        # Parse JSON response
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

        print(f"✓ Successfully processed {interaction_type} {interaction_id}")
        return parsed
        
    except Exception as e:
        print(f"✗ Error processing {interaction_type} {interaction_id}: {e}")
        
        # Return appropriate error placeholder based on interaction type
        if interaction_type == "bot":
            return {
                "non_question_part": "",
                "question_part": "",
                "socratic_label": "Error",
                "rationale": f"Processing error: {str(e)[:50]}",
                "confidence": 0.0
            }
        else:  # student
            return {
                "bot_message": interaction_text,
                "student_response": interaction_text,
                "assigned_labels": [
                    {
                        "label": "Error",
                        "reasoning": f"Processing error: {str(e)[:50]}"
                    }
                ]
            }
