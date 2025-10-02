SUMMARY_PROMPT_TEMPLATE = """
    User asked: {{user_question}}
    SQL generated: {{generated_sql}}
    Total results: {{total_results}}
    Preview (first 5 rows): {{preview_rows}}

    Instructions:
    - Respond in **Markdown only**.
    - Use emojis to make the response friendly and engaging where appropriate.
    - If no preview rows, clearly say no data was found; do **not** invent data.
    - If results exist, summarize in a friendly, non-technical way.
    - Add a clear/descriptive title above any table; Format tables cleanly using **Markdown**; align columns properly.
    - Use human-readable headers and terms.
    - Make sure to highlight any important trends or patterns.
"""