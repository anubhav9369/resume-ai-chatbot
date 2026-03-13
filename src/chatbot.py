# src/chatbot.py
import os
import time
import tiktoken
import openai
from dataclasses import dataclass, field
from typing import Optional
from src.loader import ResumeLoader
from src.prompts import STRATEGIES


@dataclass
class CallLog:
    """Records metadata for every LLM call — used by benchmark harness."""
    strategy: str
    question: str
    answer: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    cost_usd: float


class ResumeChatbot:
    """
    Multi-turn resume Q&A chatbot with:
    - Sliding window conversation memory
    - Pluggable prompt strategies
    - Per-call cost and latency logging
    """

    # GPT-4o-mini pricing (per 1M tokens, as of mid-2024)
    PRICE_IN = 0.15 / 1_000_000   # $0.15 per 1M input tokens
    PRICE_OUT = 0.60 / 1_000_000  # $0.60 per 1M output tokens

    def __init__(
        self,
        resume_path: str,
        model: str = "llama-3.1-8b-instant",
        strategy: str = "few_shot",
        max_context_tokens: int = 4000,
    ):
        self.model = model
        self.strategy = strategy
        self.max_context_tokens = max_context_tokens
        self.resume = ResumeLoader(resume_path)
        self.client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.enc = tiktoken.get_encoding("cl100k_base")
        self.history: list[dict] = []  # Full conversation history
        self.logs: list[CallLog] = []  # All call logs

    def count_tokens(self, text: str) -> int:
        """Count tokens in a string."""
        return len(self.enc.encode(text))

    def _trim_history(self) -> list[dict]:
        """
        Return a trimmed version of history that fits within token budget.
        Always keeps the most recent turns — drops oldest first.
        """
        if not self.history:
            return []

        # Count from most recent to oldest, keep what fits
        kept = []
        token_count = 0
        budget = self.max_context_tokens - 800  # Reserve 800 for system + context

        for msg in reversed(self.history):
            msg_tokens = self.count_tokens(msg['content'])
            if token_count + msg_tokens > budget:
                break
            kept.insert(0, msg)
            token_count += msg_tokens

        return kept

    def chat(self, question: str) -> tuple[str, CallLog]:
        """
        Send a message and get a response.
        Returns (answer, log) — log has all metadata.
        """
        # Get smart context for this question
        context = self.resume.get_context_for_question(question)

        # Build prompt using the chosen strategy
        prompt_fn = STRATEGIES[self.strategy]
        messages = prompt_fn(context, question)

        # Inject trimmed conversation history AFTER system message
        trimmed_history = self._trim_history()
        if trimmed_history:
            messages = [messages[0]] + trimmed_history + [messages[-1]]

        # Count input tokens
        full_prompt = ' '.join(m['content'] for m in messages)
        tokens_in = self.count_tokens(full_prompt)

        # Call the API
        start = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,  # Low temperature = more consistent, factual
            max_tokens=500,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        answer = response.choices[0].message.content
        tokens_out = response.usage.completion_tokens

        # Calculate cost
        cost = (tokens_in * self.PRICE_IN) + (tokens_out * self.PRICE_OUT)

        # Update history
        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": answer})

        # Log the call
        log = CallLog(
            strategy=self.strategy,
            question=question,
            answer=answer,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            cost_usd=cost
        )
        self.logs.append(log)

        return answer, log

    def reset_history(self):
        """Clear conversation history (start fresh)."""
        self.history = []

    def get_stats(self) -> dict:
        """Return aggregate stats for all calls this session."""
        if not self.logs:
            return {}
        return {
            "total_calls": len(self.logs),
            "total_tokens_in": sum(l.tokens_in for l in self.logs),
            "total_tokens_out": sum(l.tokens_out for l in self.logs),
            "avg_latency_ms": sum(l.latency_ms for l in self.logs) / len(self.logs),
            "total_cost_usd": sum(l.cost_usd for l in self.logs),
        }
