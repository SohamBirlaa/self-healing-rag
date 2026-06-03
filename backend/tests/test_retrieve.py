"""
Tests for retrieve node
- HuggingFace API mock
- ChromaDB mock
- CrossEncoder mock
"""

from unittest.mock import patch, MagicMock
import numpy as np


def test_retrieve_returns_documents():
    """Normal case — docs milne chahiye"""

    with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
         patch("app.nodes.retrieve._get_reranker")  as mock_rer, \
         patch("app.nodes.retrieve._get_collection") as mock_col:

        # HF API mock — fake embedding return karo
        mock_hf.return_value.feature_extraction.return_value = \
            np.array([0.1, 0.2, 0.3])

        # ChromaDB mock
        mock_col.return_value.count.return_value = 2
        mock_col.return_value.query.return_value = {
            "documents": [["Chunk 1 about project.", "Chunk 2 about stack."]],
            "distances": [[0.1, 0.2]]
        }

        # Reranker mock
        mock_rer.return_value.predict.return_value = \
            np.array([0.9, 0.7])

        from app.nodes.retrieve import retrieve
        result = retrieve({
            "question":           "What is the project about?",
            "rewritten_question": ""
        })

    assert "documents" in result
    assert len(result["documents"]) > 0
    assert "retrieval_score" in result
    assert 0.0 <= result["retrieval_score"] <= 1.0


def test_retrieve_empty_db():
    """Empty ChromaDB — empty list aana chahiye"""

    with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
         patch("app.nodes.retrieve._get_reranker"), \
         patch("app.nodes.retrieve._get_collection") as mock_col:

        mock_hf.return_value.feature_extraction.return_value = \
            np.array([0.1, 0.2, 0.3])

        mock_col.return_value.count.return_value = 0

        from app.nodes.retrieve import retrieve
        result = retrieve({
            "question":           "Anything?",
            "rewritten_question": ""
        })

    assert result["documents"] == []
    assert result["retrieval_score"] == 0.0


def test_retrieve_uses_rewritten_question():
    """Rewritten question available ho toh woh use hona chahiye"""

    with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
         patch("app.nodes.retrieve._get_reranker")  as mock_rer, \
         patch("app.nodes.retrieve._get_collection") as mock_col:

        mock_hf.return_value.feature_extraction.return_value = \
            np.array([0.1, 0.2, 0.3])

        mock_col.return_value.count.return_value = 1
        mock_col.return_value.query.return_value = {
            "documents": [["Some context."]],
            "distances": [[0.1]]
        }
        mock_rer.return_value.predict.return_value = np.array([0.8])

        from app.nodes.retrieve import retrieve
        result = retrieve({
            "question":           "Original question",
            "rewritten_question": "Better rewritten question"
        })

        # HF API ko rewritten question se call hona chahiye
        call_args = mock_hf.return_value.feature_extraction.call_args
        assert call_args[1]["text"] == "Better rewritten question"

    assert len(result["documents"]) > 0