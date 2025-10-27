def build_student_response_classification_prompt(paired_interaction):
    """
    Build a prompt for analyzing student responses in relation to bot questions.
    
    Args:
        paired_interaction: Dictionary containing bot and student interaction data
    
    Returns:
        Formatted prompt string for LLM analysis
    """
    # Extract bot message and student response from paired interaction
    bot_message = paired_interaction.get('bot_text', '')
    student_response = paired_interaction.get('student_text', '')
    
    return f"""You are an expert in discourse analysis and educational game design. Your task is to evaluate a single interaction turn between a student and a GenAI Socratic tutoring bot.

You will be given:
- The bot's message (which may include a question, feedback, or instruction)
- The student's immediate response

Your job is to **analyze the student response in context** of the bot's message and assign **engagement labels** that describe how the student is participating in the learning or narrative process.

---

### STEP 1 — Read the Bot and Student Turn

BOT: {bot_message}

STUDENT: {student_response}

---

### STEP 2 — Choose All Applicable Labels for the Student Response

Select any of the following labels that apply to the **student's turn** (you may assign more than one if appropriate):

| **Label** | **Description** |
|----------|------------------|
| **Narrative Participation** | The student engages with the story world by making choices, describing setting or events, staying in character, or proposing story actions. |
| **Factual Explanation** | The student provides a correct or relevant explanation of a scientific concept, summary, or observation. |
| **Incorrect Attempt** | The student attempts to answer but provides factually incorrect or confused information. |
| **IDK / Not Sure** | The student explicitly expresses uncertainty or gives a non-answer (e.g., “I don’t know”, “not sure”). |

---

### STEP 3 — For Each Assigned Label, Provide a Reason

For each label you assign, write a brief explanation (max 25 words) explaining why it fits the student’s response. Do not include labels that do not apply.

---

### STEP 4 — Output Format (strict JSON)

Return your analysis in the following format:

{{
  "bot_message": "[verbatim bot message]",
  "student_response": "[verbatim student response]",
  "assigned_labels": [
    {{
      "label": "Narrative Participation",
      "reasoning": "The student chooses a setting and describes it using sensory language."
    }},
    {{
      "label": "Factual Explanation",
      "reasoning": "The student accurately explains the role of sunlight in the light-dependent reactions."
    }}
  ]
}}

"""


def build_bot_response_classification_prompt(bot_response):
    return f"""You are a trained discourse analyst specializing in Socratic dialogue and critical thinking.

Your task is to analyze each provided text turn, which may include both explanatory statements and one or more questions.

---

### STEP 1 — Separate Question and Non-Question Parts
- Identify all text segments that are genuine **questions** (ending with a question mark “?”).
- Combine all questions into a single contiguous block called **Question_Part**.
- Combine the remaining statements, explanations, or feedback into **NonQuestion_Part**.
- Do not paraphrase or remove punctuation — preserve wording exactly.

---

### STEP 2 — Classify the Question Portion Collectively
Treat all questions together as a single Socratic act and classify them using the **six Socratic question types** from *Richard Paul & Linda Elder (2006)*.

Choose **one** label that best describes the dominant intent of the combined Question_Part.

Available labels:
1. **Clarification** — seeks meaning, definitions, or examples.  
2. **Assumptions** — probes underlying beliefs or premises.  
3. **Reasons_Evidence** — requests justification, explanation, or proof.  
4. **Viewpoints** — explores alternative perspectives or opposing ideas.  
5. **Implications** — examines logical or practical consequences.  
6. **Meta** — reflects on the question itself or on thinking processes.  
7. **Other** — use only if there is no question present or if none of the six categories clearly apply.

**Always prefer one of the six Socratic categories when a question is present. Use "Other" only when the input lacks questions or is completely out of scope.**

For the chosen label, provide:
- a **rationale** (one concise sentence, 10–25 words), explaining why this question fits that category, and  
- a **confidence** score between 0 and 1 (e.g., 0.86) indicating your confidence in this classification.

---

### Category Reference

| Label | Focus | Example |
|--------|--------|----------|
| **Clarification** | Seeks meaning, restatement, or examples | “What do you mean by that?” |
| **Assumptions** | Probes what is taken for granted | “What are you assuming?” |
| **Reasons_Evidence** | Asks for justification or proof | “What evidence supports that idea?” |
| **Viewpoints** | Invites alternative perspectives | “How might someone else view this?” |
| **Implications** | Explores consequences or logical outcomes | “If that is true, what follows?” |
| **Meta** | Reflects on the question or process itself | “Why is this question important?” |
| **Other** | Use only if there is no question or it does not fit any category | [No example required] |

---

### STEP 3 — Output Format
Return the output in **strict JSON** format.

Each input text must be represented as one JSON object with the following keys:
- "non_question_part" — all non-question sentences (statements, explanations, feedback).
- "question_part" — all question sentences combined into one string.
- "socratic_label" — one of: ["Clarification", "Assumptions", "Reasons_Evidence", "Viewpoints", "Implications", "Meta", "Other"].
- "rationale" — one concise sentence (10–25 words) explaining why the label fits the question part.
- "confidence" — a numeric score between 0 and 1 representing confidence in the classification.

Do not include any commentary, markdown formatting, or text outside the JSON.

---

### INPUT TEXT
{bot_response}

"""