"""
Tests for critic node
- Groq LLM mock
- PASS case
- FAIL case
- Empty answer case
- Parse edge cases
"""

from unittest.mock import patch, MagicMock


def test_critic_pass():
    """High confidence answer — PASS aana chahiye"""

    with patch("app.nodes.critic._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "DECISION: PASS\nCONFIDENCE: 0.92\nREASON: Answer is grounded in context."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.critic import critic
        result = critic({
            "question":           "What is X?",
            "rewritten_question": "",
            "documents":          ["Context about X."],
            "answer":             "X is a thing described in context."
        })

    assert result["decision"]         == "PASS"
    assert result["confidence_score"] == 0.92


def test_critic_fail():
    """Low confidence answer — FAIL aana chahiye"""

    with patch("app.nodes.critic._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "DECISION: FAIL\nCONFIDENCE: 0.2\nREASON: Answer is hallucinated."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.critic import critic
        result = critic({
            "question":           "What is X?",
            "rewritten_question": "",
            "documents":          ["Context about X."],
            "answer":             "X is something made up."
        })

    assert result["decision"]         == "FAIL"
    assert result["confidence_score"] == 0.2


def test_critic_empty_answer():
    """Empty answer — auto FAIL hona chahiye, LLM call nahi hona chahiye"""

    with patch("app.nodes.critic._get_llm") as mock_llm:
        from app.nodes.critic import critic
        result = critic({
            "question":           "What?",
            "rewritten_question": "",
            "documents":          [],
            "answer":             ""
        })

        # LLM call nahi hona chahiye
        mock_llm.return_value.invoke.assert_not_called()

    assert result["decision"]         == "FAIL"
    assert result["confidence_score"] == 0.0


def test_critic_confidence_clamped():
    """Confidence 0-1 ke beech honi chahiye"""

    with patch("app.nodes.critic._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "DECISION: PASS\nCONFIDENCE: 1.5\nREASON: Test."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.critic import critic
        result = critic({
            "question":           "Test?",
            "rewritten_question": "",
            "documents":          ["Context."],
            "answer":             "Answer."
        })

    assert result["confidence_score"] <= 1.0
    assert result["confidence_score"] >= 0.0


def test_critic_case_insensitive_parse():
    """Lowercase decision bhi parse hona chahiye"""

    with patch("app.nodes.critic._get_llm") as mock_llm:
        mock_response         = MagicMock()
        mock_response.content = "decision: pass\nconfidence: 0.8\nreason: looks good."
        mock_llm.return_value.invoke.return_value = mock_response

        from app.nodes.critic import critic
        result = critic({
            "question":           "Test?",
            "rewritten_question": "",
            "documents":          ["Context."],
            "answer":             "Answer."
        })

    assert result["decision"] == "PASS"