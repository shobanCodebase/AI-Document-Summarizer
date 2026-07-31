def build_chunk_summary_prompt(chunk_text: str) -> tuple[str, str]:
    system_prompt = (
        "You are an expert at summarizing documents concisely while "
        "preserving key facts, figures, and important details."
    )
    user_prompt = (
        f"Summarize the following section of a document. Focus on the "
        f"key points and factual content, in 3-5 sentences.\n\n"
        f"Section:\n{chunk_text}"
    )
    return system_prompt, user_prompt

def build_final_summary_prompt(combined_summaries: str) -> tuple[str, str]:
    system_prompt = (
        "You are an expert document analyst who creates clear, well-organized "
        "summaries from partial section summaries of a larger document."
    )
    user_prompt = (
        f"Below are summaries of different sections of a document. "
        f"Synthesize them into one cohesive analysis.\n\n"
        f"Section summaries:\n{combined_summaries}\n\n"
        f"Return ONLY valid JSON in exactly this structure, with no additional "
        f"text before or after it:\n"
        f'{{\n'
        f'  "executive_summary": "<a 2-3 paragraph cohesive summary>",\n'
        f'  "bullet_points": ["...", "..."],\n'
        f'  "key_takeaways": ["...", "..."],\n'
        f'  "action_items": ["...", "..."]\n'
        f'}}'
    )
    return system_prompt, user_prompt