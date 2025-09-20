from openai_summary import openai_summarize

openai_llm = lambda t: openai_summarize(t, model="gpt-5-nano")

def summarize_item(item: dict, llm=None) -> dict:
    text = (item.get("summary_raw") or item.get("title") or "").strip()
    if not text:
        return {**item, "summary": "No summary available for this article"}
    if llm:
        try:
            summary = llm(text)             #try, else fallback
        except Exception as e:
            print(f"[WARN] Summarization failed for {item.get('title')}: {e}")
            summary = ". ".join(text.split(". ")[:2]).strip()
    else:
        summary = ". ".join(text.split(". ")[:2]).strip()

    return {**item, "summary": summary}
