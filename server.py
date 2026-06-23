#!/usr/bin/env python3

import os
from typing import Any

from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from google import genai
from google.genai import types


load_dotenv()

mcp = FastMCP("ollama-gemini-grounded-search")


def extract_sources(response: Any) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    seen: set[str] = set()

    for candidate in getattr(response, "candidates", []) or []:
        grounding_metadata = getattr(candidate, "grounding_metadata", None)
        if not grounding_metadata:
            continue

        chunks = getattr(grounding_metadata, "grounding_chunks", []) or []
        for chunk in chunks:
            web = getattr(chunk, "web", None)
            if not web:
                continue

            url = getattr(web, "uri", "") or ""
            title = getattr(web, "title", "") or url

            if url and url not in seen:
                seen.add(url)
                sources.append({"title": title, "url": url})

    return sources


@mcp.tool()
def google_grounded_search(query: str) -> str:
    """
    Search the public web using Gemini Google Search grounding.
    Use this when current web information or source links are needed.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "ERROR: GEMINI_API_KEY is not set."

    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
Answer the user's query using Google Search grounding.
Be concise.
Preserve the user's language.
Include source links if available.

Query:
{query}
""".strip()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ],
            temperature=0.2,
        ),
    )

    text = (getattr(response, "text", None) or "").strip()
    sources = extract_sources(response)

    if sources:
        text += "\n\nSources:\n"
        for i, source in enumerate(sources, start=1):
            text += f"{i}. {source['title']} — {source['url']}\n"

    return text.strip() or "No answer returned by Gemini."


if __name__ == "__main__":
    mcp.run()

