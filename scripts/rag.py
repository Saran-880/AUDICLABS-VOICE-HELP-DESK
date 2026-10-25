
import os
import re
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from backend import AudicLabsError, check_health
from scripts.hybrid_retriever import build_retrievers


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=False)

UNKNOWN_ANSWER = (
    "I couldn't find sufficient information in the AudicLabs documentation."
)

SYSTEM_PROMPT = """
You are a helpful voice help desk assistant for AudicLabs documentation.

Follow these rules carefully:

1. Answer documentation questions using only the supplied documentation context.
2. Never invent endpoints, features, limits, or instructions.
3. Give complete, accurate answers in simple English.
4. For how-to questions, explain the steps in order when supported.
5. Be concise but include important details.
6. Cite documentation answers using valid source IDs such as [S1] or [S2].
7. Only cite sources that directly support the answer.
8. If documentation does not contain enough information, reply exactly:
   "I couldn't find sufficient information in the AudicLabs documentation."
9. If the user requests Hindi, answer in Hindi.
10. Never reveal API keys, secrets, or environment variable values.
11. For questions about previous messages, use conversation history.
12. History can establish what was discussed earlier, but it must not be
    treated as evidence for unrelated documentation facts.
13. If asked to reveal secrets, politely refuse.
14. When asked to check the live AudicLabs API health or service status,
    call the check_audiclabs_api_health tool.
15. Report the health tool result accurately. Do not claim the service is
    healthy if the health check fails.
16. The health endpoint checks the Noise Suppressor health endpoint only.
    Do not claim that all AudicLabs services are healthy based on this result.
17. Health-check results are operational data and do not require documentation
    citations. Documentation answers still require valid citations.
"""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    (
        "human",
        """Conversation history:
{history}

User question:
{question}

Retrieved documentation:
{context}

Answer the question using the rules above.
Use the health-check tool when appropriate."""
    ),
])


@tool
def check_audiclabs_api_health() -> str:
    """Check the live AudicLabs Noise Suppressor health endpoint.
    Use this tool when the user asks whether the AudicLabs API or service
    is healthy, online, or available.
    """
    try:
        result = check_health()
        return (
            "Health endpoint request succeeded. "
            f"Endpoint response: {result}"
        )
    except AudicLabsError as exc:
        return f"Health check failed: {exc}"
    except Exception as exc:
        # Do not expose unexpected exception messages to the user/model.
        return (
            "Health check failed unexpectedly. "
            f"Error type: {type(exc).__name__}"
        )


@lru_cache(maxsize=1)
def get_retrievers():
    """Initialize the retrievers once per Python process."""
    return build_retrievers()


def format_documents(documents):
    """Format retrieved chunks and assign citation IDs by source URL."""
    sections = []
    source_map = {}
    section_indexes = {}
    url_to_source_id = {}

    for document in documents:
        metadata = document.metadata or {}
        title = metadata.get("title", "AudicLabs documentation")
        url = metadata.get("url", "")
        content = document.page_content.strip()

        if not content:
            continue

        # Merge chunks from the same page under one citation ID.
        if url and url in url_to_source_id:
            source_id = url_to_source_id[url]
            section_index = section_indexes[source_id]
            sections[section_index] += f"\n\n{content}"
            continue

        source_id = f"S{len(source_map) + 1}"

        source_map[source_id] = {
            "title": title,
            "url": url,
        }

        if url:
            url_to_source_id[url] = source_id

        section_indexes[source_id] = len(sections)

        sections.append(
            f"[{source_id}]\n"
            f"Page title: {title}\n"
            f"Page URL: {url}\n"
            f"Documentation content:\n{content}"
        )

    return "\n\n---\n\n".join(sections), source_map


def extract_citation_ids(answer):
    """Recognize ASCII and full-width citation IDs."""
    matches = re.findall(r"\[([Ss]\d+)\]|【([Ss]\d+)】", answer)

    citation_ids = []

    for ascii_id, fullwidth_id in matches:
        citation_id = (ascii_id or fullwidth_id).upper()

        if citation_id not in citation_ids:
            citation_ids.append(citation_id)

    return citation_ids


def normalize_citations(answer, valid_ids):
    """Normalize valid citations and remove invalid citation IDs."""

    def replace_citation(match):
        citation_id = (match.group(1) or match.group(2)).upper()

        if citation_id in valid_ids:
            return f"[{citation_id}]"

        return ""

    return re.sub(
        r"\[([Ss]\d+)\]|【([Ss]\d+)】",
        replace_citation,
        answer,
    ).strip()


def _content_to_text(content):
    """Convert model response content into a plain-text answer."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        return "\n".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("text")
        ).strip()

    return str(content).strip()


def _invoke_with_health_tool(llm, question, history, context):
    """Invoke the model and execute its health-check tool call if requested."""
    tool_model = llm.bind_tools([check_audiclabs_api_health])

    messages = PROMPT.format_messages(
        question=question,
        history=history or "No previous conversation.",
        context=context,
    )

    response = tool_model.invoke(messages)
    tool_calls = getattr(response, "tool_calls", []) or []

    if not tool_calls:
        return _content_to_text(response.content)

    messages.append(response)

    for tool_call in tool_calls:
        if tool_call.get("name") != "check_audiclabs_api_health":
            continue

        try:
            result = check_audiclabs_api_health.invoke(
                tool_call.get("args", {})
            )
        except Exception as exc:
            result = (
                "Health check failed unexpectedly. "
                f"Error type: {type(exc).__name__}"
            )

        messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            )
        )

    # Ask the model to explain the actual tool result.
    final_response = llm.invoke(messages)
    return _content_to_text(final_response.content)


def answer_question(question, history=""):
    """
    Retrieve grounded documentation and return an answer with sources.
    Keeps the existing interface used by app.py and evaluate.py.
    """
    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "sources": [],
        }

    if not os.getenv("GROQ_API_KEY"):
        return {
            "answer": (
                "The language model is not configured. "
                "Please check the server environment."
            ),
            "sources": [],
        }

    try:
        # Retrieve documentation context.
        _, _, hybrid_retriever = get_retrievers()
        documents = hybrid_retriever.invoke(question)
        context, source_map = format_documents(documents)

        # The health tool can still be used if retrieval returns no documents.
        if not context.strip():
            context = "No relevant documentation was retrieved."

        llm = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0,
            max_tokens=800,
        )

        answer = _invoke_with_health_tool(
            llm=llm,
            question=question,
            history=history,
            context=context,
        )

        if not answer:
            return {
                "answer": (
                    "Sorry, I couldn't generate an answer. "
                    "Please try again."
                ),
                "sources": [],
            }

        # Preserve the exact unknown-answer fallback.
        if UNKNOWN_ANSWER.lower() in answer.lower():
            return {
                "answer": UNKNOWN_ANSWER,
                "sources": [],
            }

        # Resolve citations against the retrieved source map.
        cited_ids = extract_citation_ids(answer)
        valid_ids = set(source_map)

        sources = []

        for source_id in cited_ids:
            source = source_map.get(source_id)

            if source and source["url"]:
                sources.append({
                    "title": source["title"],
                    "url": source["url"],
                })

        answer = normalize_citations(answer, valid_ids)

        if not answer:
            return {
                "answer": (
                    "Sorry, I couldn't generate a complete answer. "
                    "Please try again."
                ),
                "sources": [],
            }

        return {
            "answer": answer,
            "sources": sources,
        }

    except Exception as exc:
        # Keep technical details in the terminal for debugging.
        print(f"RAG error: {type(exc).__name__}: {exc}")

        return {
            "answer": (
                "Sorry, I couldn't process that question right now. "
                "Please try again."
            ),
            "sources": [],
        }


if __name__ == "__main__":
    question = input("Ask an AudicLabs question: ")
    result = answer_question(question)

    print("\nANSWER")
    print(result["answer"])

    print("\nSOURCES")

    if result["sources"]:
        for source in result["sources"]:
            print(f"- {source['title']}: {source['url']}")
    else:
        print("No sources returned.")
