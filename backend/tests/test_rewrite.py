"""
Tests for rewrite node
- Groq LLM mock
- Loop prevention
- History tracking
- Fallback when same question returned
"""

from unittest.mock import patch, MagicMock


def test_rewrite_returns_new_question():
    """Normal case — naya question return hona chahiye"""

    with patch("app.nodes.rewrite._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "What are the specific technical components used?"
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.rewrite import rewrite
        result = rewrite({
            "question":           "What is the architecture?",
            "rewritten_question": "",
            "previous_questions": []
        })

    assert "rewritten_question" in result
    assert result["rewritten_question"] != ""
    assert result["rewritten_question"] == "What are the specific technical components used?"


def test_rewrite_tracks_history():
    """Previous questions mein original question add hona chahiye"""

    with patch("app.nodes.rewrite._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "New improved question."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.rewrite import rewrite
        result = rewrite({
            "question":           "Original question",
            "rewritten_question": "",
            "previous_questions": []
        })

    assert "previous_questions" in result
    assert "Original question" in result["previous_questions"]


def test_rewrite_loop_prevention():
    """Same question return hone pe fallback apply hona chahiye"""

    with patch("app.nodes.rewrite._get_llm") as mock_llm:
        mock_response         = MagicMock()
        # LLM same question return kar raha hai
        mock_response.content = "What is the architecture?"
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.rewrite import rewrite
        result = rewrite({
            "question":           "What is the architecture?",
            "rewritten_question": "",
            "previous_questions": []
        })

    # Same question nahi hona chahiye
    assert result["rewritten_question"] != "What is the architecture?"


def test_rewrite_appends_to_existing_history():
    """Existing history mein naya question add hona chahiye"""

    with patch("app.nodes.rewrite._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "Third attempt question."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.rewrite import rewrite
        result = rewrite({
            "question":           "Second attempt",
            "rewritten_question": "Second attempt",
            "previous_questions": ["First attempt"]
        })

    assert len(result["previous_questions"]) == 2
    assert "First attempt"  in result["previous_questions"]
    assert "Second attempt" in result["previous_questions"]