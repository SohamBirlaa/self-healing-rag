# """
# Integration tests for full LangGraph pipeline
# - Full PASS flow
# - FAIL then retry flow  
# - Max retries exceeded
# """

# from unittest.mock import patch, MagicMock
# import numpy as np


# def _make_initial_state(question="What is the architecture?"):
#     return {
#         "question":            question,
#         "rewritten_question":  "",
#         "previous_questions":  [],
#         "documents":           [],
#         "answer":              "",
#         "decision":            "",
#         "retry_count":         0,
#         "retrieval_score":     0.0,
#         "confidence_score":    0.0
#     }


# def _mock_retrieve(mock_hf, mock_rer, mock_col):
#     """Retrieve node ke liye common mocks"""
#     mock_hf.return_value.feature_extraction.return_value = \
#         np.array([0.1, 0.2, 0.3])
#     mock_col.return_value.count.return_value = 1
#     mock_col.return_value.query.return_value = {
#         "documents": [["Some context about the system."]],
#         "distances": [[0.1]]
#     }
#     mock_rer.return_value.predict.return_value = np.array([0.9])


# def test_graph_full_pass():
#     """Pipeline PASS pe complete hona chahiye — 0 retries"""

#     with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
#          patch("app.nodes.retrieve._get_reranker")   as mock_rer, \
#          patch("app.nodes.retrieve._get_collection") as mock_col, \
#          patch("app.nodes.generate._get_llm")        as mock_gen, \
#          patch("app.nodes.critic._get_llm")          as mock_crit:

#         _mock_retrieve(mock_hf, mock_rer, mock_col)

#         gen_response         = MagicMock()
#         gen_response.content = "The system uses a layered architecture."
#         mock_gen.return_value.invoke.return_value = gen_response

#         crit_response         = MagicMock()
#         crit_response.content = "DECISION: PASS\nCONFIDENCE: 0.9\nREASON: Grounded in context."
#         mock_crit.return_value.invoke.return_value = crit_response

#         from app.graph import graph
#         result = graph.invoke(_make_initial_state())

#     assert result["answer"]   != ""
#     assert result["decision"] == "PASS"
#     assert result["retry_count"] == 0


# def test_graph_retry_then_pass():
#     """Pehle FAIL phir PASS — 1 retry hona chahiye"""

#     with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
#          patch("app.nodes.retrieve._get_reranker")   as mock_rer, \
#          patch("app.nodes.retrieve._get_collection") as mock_col, \
#          patch("app.nodes.generate._get_llm")        as mock_gen, \
#          patch("app.nodes.critic._get_llm")          as mock_crit, \
#          patch("app.nodes.rewrite._get_llm")         as mock_rew:

#         _mock_retrieve(mock_hf, mock_rer, mock_col)

#         gen_response         = MagicMock()
#         gen_response.content = "Some answer."
#         mock_gen.return_value.invoke.return_value = gen_response

#         # Pehli call FAIL, doosri call PASS
#         fail_response         = MagicMock()
#         fail_response.content = "DECISION: FAIL\nCONFIDENCE: 0.2\nREASON: Not grounded."

#         pass_response         = MagicMock()
#         pass_response.content = "DECISION: PASS\nCONFIDENCE: 0.85\nREASON: Grounded."

#         mock_crit.return_value.invoke.side_effect = [fail_response, pass_response]

#         rew_response         = MagicMock()
#         rew_response.content = "More specific question about architecture."
#         mock_rew.return_value.invoke.return_value = rew_response

#         from app.graph import graph
#         result = graph.invoke(_make_initial_state())

#     assert result["decision"]    == "PASS"
#     assert result["retry_count"] >= 1


# def test_graph_max_retries():
#     """Max retries hit hone pe FAIL ke saath exit hona chahiye"""

#     with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
#          patch("app.nodes.retrieve._get_reranker")   as mock_rer, \
#          patch("app.nodes.retrieve._get_collection") as mock_col, \
#          patch("app.nodes.generate._get_llm")        as mock_gen, \
#          patch("app.nodes.critic._get_llm")          as mock_crit, \
#          patch("app.nodes.rewrite._get_llm")         as mock_rew:

#         _mock_retrieve(mock_hf, mock_rer, mock_col)

#         gen_response         = MagicMock()
#         gen_response.content = "Some answer."
#         mock_gen.return_value.invoke.return_value = gen_response

#         # Hamesha FAIL
#         fail_response         = MagicMock()
#         fail_response.content = "DECISION: FAIL\nCONFIDENCE: 0.2\nREASON: Not grounded."
#         mock_crit.return_value.invoke.return_value = fail_response

#         rew_response         = MagicMock()
#         rew_response.content = "Rewritten question attempt."
#         mock_rew.return_value.invoke.return_value = rew_response

#         from app.graph import graph
#         result = graph.invoke(_make_initial_state())

#     assert result["decision"]    == "FAIL"
#     assert result["retry_count"] == 3

# for deployment
def _mock_retrieve(mock_hf, mock_col):
    mock_hf.return_value.feature_extraction.return_value = \
        np.array([0.1, 0.2, 0.3])
    mock_col.return_value.count.return_value = 1
    mock_col.return_value.query.return_value = {
        "documents": [["Some context about the system."]],
        "distances": [[0.1]]
    }


def test_graph_full_pass():
    with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
         patch("app.nodes.retrieve._get_collection") as mock_col, \
         patch("app.nodes.generate._get_llm")        as mock_gen, \
         patch("app.nodes.critic._get_llm")          as mock_crit:

        _mock_retrieve(mock_hf, mock_col)

        gen_response         = MagicMock()
        gen_response.content = "The system uses a layered architecture."
        mock_gen.return_value.invoke.return_value = gen_response

        crit_response         = MagicMock()
        crit_response.content = "DECISION: PASS\nCONFIDENCE: 0.9\nREASON: Grounded."
        mock_crit.return_value.invoke.return_value = crit_response

        from app.graph import graph
        result = graph.invoke(_make_initial_state())

    assert result["answer"]      != ""
    assert result["decision"]    == "PASS"
    assert result["retry_count"] == 0


def test_graph_retry_then_pass():
    with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
         patch("app.nodes.retrieve._get_collection") as mock_col, \
         patch("app.nodes.generate._get_llm")        as mock_gen, \
         patch("app.nodes.critic._get_llm")          as mock_crit, \
         patch("app.nodes.rewrite._get_llm")         as mock_rew:

        _mock_retrieve(mock_hf, mock_col)

        gen_response         = MagicMock()
        gen_response.content = "Some answer."
        mock_gen.return_value.invoke.return_value = gen_response

        fail_response         = MagicMock()
        fail_response.content = "DECISION: FAIL\nCONFIDENCE: 0.2\nREASON: Not grounded."
        pass_response         = MagicMock()
        pass_response.content = "DECISION: PASS\nCONFIDENCE: 0.85\nREASON: Grounded."
        mock_crit.return_value.invoke.side_effect = [fail_response, pass_response]

        rew_response         = MagicMock()
        rew_response.content = "More specific question."
        mock_rew.return_value.invoke.return_value = rew_response

        from app.graph import graph
        result = graph.invoke(_make_initial_state())

    assert result["decision"]    == "PASS"
    assert result["retry_count"] >= 1


def test_graph_max_retries():
    with patch("app.nodes.retrieve._get_hf_client") as mock_hf, \
         patch("app.nodes.retrieve._get_collection") as mock_col, \
         patch("app.nodes.generate._get_llm")        as mock_gen, \
         patch("app.nodes.critic._get_llm")          as mock_crit, \
         patch("app.nodes.rewrite._get_llm")         as mock_rew:

        _mock_retrieve(mock_hf, mock_col)

        gen_response         = MagicMock()
        gen_response.content = "Some answer."
        mock_gen.return_value.invoke.return_value = gen_response

        fail_response         = MagicMock()
        fail_response.content = "DECISION: FAIL\nCONFIDENCE: 0.2\nREASON: Not grounded."
        mock_crit.return_value.invoke.return_value = fail_response

        rew_response         = MagicMock()
        rew_response.content = "Rewritten question."
        mock_rew.return_value.invoke.return_value = rew_response

        from app.graph import graph
        result = graph.invoke(_make_initial_state())

    assert result["decision"]    == "FAIL"
    assert result["retry_count"] == 3