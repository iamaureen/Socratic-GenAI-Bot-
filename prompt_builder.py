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

For the chosen label, provide:
- a **rationale** (one concise sentence, 10–25 words), explaining why this question fits that category and  
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

---

### STEP 3 — Output Format
Return the output in **strict JSON** format.

Each input text must be represented as one JSON object with the following keys:
- "original_text" — the full input text exactly as received.
- "non_question_part" — all non-question sentences (statements, explanations, feedback).
- "question_part" — all question sentences combined into one string.
- "label" — one of: ["Clarification", "Assumptions", "Reasons_Evidence", "Viewpoints", "Implications", "Meta"].
- "rationale" — one concise sentence (10–25 words) explaining why the label fits the question part.
- "confidence" — a numeric score between 0 and 1 representing confidence in the classification.

Do not include any commentary, markdown formatting, or text outside the JSON.



### Example

**Input:**
Exactly! Glucose is like the plant's food, providing the energy and building blocks it needs to grow and stay alive. Now, let's dive a bit deeper into the process. Photosynthesis occurs in two main stages: the light-dependent reactions and the Calvin Cycle. 
What do you think happens during the light-dependent reactions? Why might they be called "light-dependent"?

**Expected Output:**

  {{
    "original_text": "Exactly! Glucose is like the plant's food... Why might they be called 'light-dependent'?",
    "non_question_part": "Exactly! Glucose is like the plant's food, providing the energy and building blocks it needs to grow and stay alive. Now, let's dive a bit deeper into the process. Photosynthesis occurs in two main stages: the light-dependent reactions and the Calvin Cycle.",
    "question_part": "What do you think happens during the light-dependent reactions? Why might they be called 'light-dependent'?",
    "label": "Reasons_Evidence",
    "rationale": "Both questions encourage the learner to explain a process and reason about underlying mechanisms.",
    "confidence": 0.92
  }}


### INPUT TEXT
{bot_response}

"""