# app/summarizer.py

from config import client

async def summarize_page(text):
    """
    Summarizes the provided text content using the OpenAI GPT-4o-mini model.
    """
    prompt = f"""Summarize the following website page content in 3–5 concise sentences, highlighting key features and purpose only:\n\n\"\"\"\n{text[:4000]}\n\"\"\""""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
            {"role": "system", "content": "You are a professional summarizer for web crawled content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("GPT Error:", e)
        return f"❌ Error summarizing this page: {str(e)}"