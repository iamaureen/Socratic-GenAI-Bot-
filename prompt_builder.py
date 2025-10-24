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