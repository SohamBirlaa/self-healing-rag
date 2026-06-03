"""
Tests for generate node
- Groq LLM mock
- Empty documents case
- Normal generation case
"""

from unittest.mock import patch, MagicMock


def test_generate_returns_answer():
    """Normal case — answer aana chahiye"""

    with patch("app.nodes.generate._get_llm") as mock_llm:
        mock_response      = MagicMock()
        mock_response.content = "The project uses LangGraph and FastAPI."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.generate import generate
        result = generate({
            "question":           "What is the project about?",
            "rewritten_question": "",
            "documents":          ["LangGraph is used for orchestration.", "FastAPI is the backend."]
        })

    assert "answer" in result
    assert len(result["answer"]) > 0
    assert "LangGraph" in result["answer"]


def test_generate_empty_documents():
    """No documents — fallback message aana chahiye"""

    from app.nodes.generate import generate
    result = generate({
        "question":           "What is this?",
        "rewritten_question": "",
        "documents":          []
    })

    assert "answer" in result
    assert result["answer"] != ""


def test_generate_uses_rewritten_question():
    """Rewritten question available ho toh woh use hona chahiye"""

    with patch("app.nodes.generate._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "Answer based on rewritten question."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.generate import generate
        generate({
            "question":           "Original question",
            "rewritten_question": "Better rewritten question",
            "documents":          ["Some context here."]
        })

        # Prompt mein rewritten question hona chahiye
        call_args = mock_llm.return_value.invoke.call_args[0][0]
        assert "Better rewritten question" in call_args


def test_generate_combines_documents():
    """Multiple documents context mein combine hone chahiye"""

    with patch("app.nodes.generate._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "Combined answer."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.generate import generate
        generate({
            "question":           "Tell me everything",
            "rewritten_question": "",
            "documents":          ["Doc 1 content.", "Doc 2 content.", "Doc 3 content."]
        })

        # Prompt mein saare docs hone chahiye
        call_args = mock_llm.return_value.invoke.call_args[0][0]
        assert "Doc 1 content." in call_args
        assert "Doc 2 content." in call_args
        assert "Doc 3 content." in call_args