
import os
import difflib

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


# ==========================================
# CONFIGURATION
# ==========================================

load_dotenv()

MODEL_NAME = "gemini-3.8-flash"

MAX_LINES_PER_CHUNK = 80


# ==========================================
# CODE CHUNKING
# ==========================================

def chunk_code(code, max_lines=MAX_LINES_PER_CHUNK):

    lines = code.splitlines()

    if not lines:
        return []

    return [
        "\n".join(lines[i:i + max_lines])
        for i in range(0, len(lines), max_lines)
    ]


# ==========================================
# RESPONSE CLEANING
# ==========================================

def clean_markdown(content):

    if isinstance(content, list):

        parts = []

        for block in content:

            if isinstance(block, dict):

                if block.get("type") == "text":
                    parts.append(block.get("text", ""))

            elif isinstance(block, str):
                parts.append(block)

        text = "\n".join(parts)

    elif isinstance(content, str):
        text = content

    else:
        text = str(content)

    # Fix escaped newlines
    text = text.replace("\\n", "\n")
    text = text.replace("\\t", "\t")

    return text.strip()


# ==========================================
# SIMILARITY CHECK
# ==========================================

def is_similar(text1, text2, threshold=0.97):

    return (
        difflib.SequenceMatcher(
            None, text1, text2
        ).ratio() >= threshold
    )


def starts_with_same_section(text1, text2):

    head1 = text1.strip().split("\n")[0:2]
    head2 = text2.strip().split("\n")[0:2]

    return any(
        h1 == h2
        for h1, h2 in zip(head1, head2)
    )


# ==========================================
# GEMINI MODEL
# ==========================================

def get_llm():

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY missing. Please configure your .env file."
        )

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=api_key,
        temperature=0.3,
        max_retries=2
    )

    return llm


# ==========================================
# MAIN CODE EXPLANATION PROMPT
# ==========================================

def build_explanation_chain():

    prompt = PromptTemplate(

        input_variables=[
            "code",
            "code_language",
            "level_of_detail",
            "output_language"
        ],

        template="""

You are an expert AI Programming Tutor, Senior Software
Engineer, and patient coding mentor.

Your responsibility is to teach programming concepts
clearly, accurately, and step by step.

You must behave like a personal programming teacher.

========================================
USER SETTINGS
========================================

Programming Language: {code_language}

Explanation Level: {level_of_detail}

Response Language: {output_language}

========================================
IMPORTANT INSTRUCTIONS
========================================

1. Explain the code in the selected language.

2. Use simple and beginner-friendly language.

3. Do not skip important statements.

4. Explain WHY each important line is used.

5. Explain the role of every important variable.

6. Explain how variable values change during execution.

7. Use proper Markdown formatting.

8. Use headings, bullet points, tables and code blocks.

9. Never return JSON or Python dictionary representations.

10. Never display literal escaped newline characters.

11. Do not put the complete explanation inside one paragraph.

12. Keep the explanation technically correct.

13. Do not unnecessarily repeat the original code.

========================================
EXPLANATION FORMAT
========================================

## 1. Overview

Explain what the program does in simple words.

Also explain the real-world or problem-solving purpose.

## 2. Important Concepts

Explain:

- Algorithm used
- Important variables
- Loops and conditions
- Functions
- Data structures
- Important programming concepts

## 3. Line-by-Line Explanation

Explain each meaningful line or logical block.

For every important line, use:

### Code

Show the relevant small code statement.

### Meaning

Explain what it does.

### Why is it used?

Explain why the programmer needs it.

Do not skip important lines.

## 4. Dry Run (Step-by-Step)

If the code is an algorithm or problem-solving program,
perform a complete dry run.

If the user has not provided input, create a small,
valid example input.

Explain each iteration.

Use a table with columns such as:

| Step | Current Element | Variable Values | Action | Result |

For every iteration explain:

1. What happens first?
2. Which condition is checked?
3. Which variable changes?
4. Why does it change?
5. What is the current result?

Do not skip important iterations.

## 5. Final Output

Show the expected output in a code block.

Explain how the output is obtained.

## 6. Time Complexity

Explain time complexity using Big O notation.

Explain why that complexity occurs.

## 7. Space Complexity

Explain extra memory usage in simple words.

## 8. Key Takeaways

Summarize the most important learning points.

========================================
EXPLANATION DEPTH
========================================

Brief:
Short explanation with the main idea.

Moderate:
Main logic and important statements.

Detailed:
Line-by-line explanation and dry run.

Comprehensive:
Deep explanation, every important statement,
complete dry run, reasoning and edge cases.

========================================
CODE TO EXPLAIN
========================================

```{code_language}
{code}
```

Remember:

Teach like a personal coding tutor.

The user should understand HOW the code works,
WHY it works, and HOW the output is produced.

"""

    )

    llm = get_llm()

    return prompt | llm


# ==========================================
# EXPLAIN CODE
# ==========================================

def explain_code(
    code: str,
    code_language="Python",
    level_of_detail="Detailed",
    output_language="English"
):

    try:

        if not code or not code.strip():
            return "Please provide code to explain."

        chain = build_explanation_chain()

        chunks = chunk_code(code)

        explanations = []

        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):

            # Add context for large programs
            if total_chunks > 1:

                chunk = f"""
This is part {i + 1} of {total_chunks}
of a larger program.

Explain this section in context.
Do not assume this section is the entire program.

{chunk}
"""

            output = chain.invoke({

                "code": chunk,

                "code_language": code_language,

                "level_of_detail": level_of_detail,

                "output_language": output_language

            })

            # Extract actual text from Gemini response
            explanation_text = getattr(
                output,
                "content",
                output
            )

            cleaned = clean_markdown(explanation_text)

            if cleaned:
                explanations.append(cleaned)

        if not explanations:
            return "No explanation generated."

        # Preserve all chunks; do not accidentally discard
        # sections merely because they share headings.
        return "\n\n---\n\n".join(explanations)

    except Exception as e:

        return f"❌ Error: {str(e)}"


# ==========================================
# FOLLOW-UP QUESTIONS
# ==========================================

def handle_user_query(
    code,
    user_query,
    output_language="English"
):

    try:

        if not code or not code.strip():
            return "Please provide the original code."

        if not user_query or not user_query.strip():
            return "Please enter your question."

        prompt = PromptTemplate(

            input_variables=[
                "code",
                "user_query",
                "output_language"
            ],

            template="""

You are an expert AI programming tutor.

The user has already received an explanation
of a programming code snippet.

Now answer the user's follow-up question.

========================================
CODE
========================================

```text
{code}
```

========================================
USER QUESTION
========================================

{user_query}

========================================
INSTRUCTIONS
========================================

1. Respond in {output_language}.

2. Explain in simple beginner-friendly language.

3. Answer the exact question.

4. Use step-by-step reasoning in the explanation.

5. Use code examples wherever useful.

6. Use Markdown headings and bullet points.

7. Explain WHY something happens.

8. Avoid unnecessary repetition.

9. Do not return JSON or dictionary representations.

10. Format the response properly.

"""

        )

        llm = get_llm()

        chain = prompt | llm

        response = chain.invoke({

            "code": code,

            "user_query": user_query,

            "output_language": output_language

        })

        content = getattr(
            response,
            "content",
            response
        )

        return clean_markdown(content)

    except Exception as e:

        return f"❌ Error: {str(e)}"