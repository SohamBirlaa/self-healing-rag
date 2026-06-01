from typing import TypedDict, List


class GraphState(TypedDict):
    """
    Shared state object passed between every node in the LangGraph pipeline.

    Fields
    ------
    question              : Original user question (never mutated)
    rewritten_question    : Latest rewritten version used for retrieval
    previous_questions    : History of all rewrites — used to prevent loops
    documents             : Retrieved + reranked chunks
    answer                : LLM-generated answer
    decision              : Critic verdict — "PASS" or "FAIL"
    retry_count           : How many retry loops have run so far
    retrieval_score       : Average similarity score of retrieved docs (0–1)
    confidence_score      : Critic's confidence that the answer is grounded (0–1)
    """

    question:            str
    rewritten_question:  str
    previous_questions:  List[str]
    documents:           List[str]
    answer:              str
    decision:            str
    retry_count:         int
    retrieval_score:     float
    confidence_score:    float