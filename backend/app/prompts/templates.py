# ── Generation prompt ──────────────────────────────────────────────────────────
GENERATE_PROMPT = """You are a helpful assistant.
Use ONLY the context provided below to answer the question.
If the context does not contain enough information, say "I don't have enough information to answer this."

Context:
{context}

Question:
{question}

Answer:"""


# ── Critic prompt ──────────────────────────────────────────────────────────────
CRITIC_PROMPT = """You are a strict quality critic.

Context:
{context}

Question:
{question}

Answer:
{answer}

Reply in EXACTLY this format, nothing else, no extra text:
DECISION: PASS
CONFIDENCE: 0.85
REASON: Answer is grounded in context.

If answer is not grounded, reply:
DECISION: FAIL
CONFIDENCE: 0.2
REASON: Answer contains hallucinated facts."""


# ── Rewrite prompt ─────────────────────────────────────────────────────────────
REWRITE_PROMPT = """You are a query optimization expert.

The original question failed to retrieve good results.
Rewrite the question to be more specific and retrieve better documents.

Original question:
{question}

Previous rewrites (DO NOT repeat these):
{previous_questions}

Write ONE improved question. Output only the question, nothing else."""