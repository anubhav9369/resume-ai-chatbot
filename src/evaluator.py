# src/evaluator.py
import json
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table as RichTable
from src.chatbot import ResumeChatbot
from src.prompts import STRATEGIES

console = Console()


def load_test_questions(filepath: str) -> list[dict]:
    """Load Q&A benchmark pairs from JSON file."""
    return json.loads(Path(filepath).read_text())


def run_benchmark(
    resume_path: str,
    questions_path: str,
    model: str = "llama-3.1-8b-instant",
) -> pd.DataFrame:
    """
    Run all 3 strategies on all test questions.
    Returns a DataFrame with full results.
    """
    questions = load_test_questions(questions_path)
    records = []

    for strategy_name in STRATEGIES.keys():
        console.print(f'\n[bold cyan]Running strategy: {strategy_name}[/bold cyan]')

        bot = ResumeChatbot(resume_path, model=model, strategy=strategy_name)

        for item in questions:
            question = item['question']
            expected = item.get('expected_keywords', [])

            console.print(f'  Q: {question[:60]}...', style='dim')
            answer, log = bot.chat(question)

            # Simple keyword-based quality score (0–1)
            # In a real eval, you'd use an LLM-as-judge or human labels
            score = 0.0
            if expected:
                hits = sum(1 for kw in expected if kw.lower() in answer.lower())
                score = hits / len(expected)

            records.append({
                "strategy": strategy_name,
                "question": question,
                "answer": answer,
                "keyword_score": round(score, 2),
                "tokens_in": log.tokens_in,
                "tokens_out": log.tokens_out,
                "latency_ms": round(log.latency_ms, 1),
                "cost_usd": round(log.cost_usd, 6),
            })

    return pd.DataFrame(records)


def print_summary(df: pd.DataFrame):
    """Print a rich summary table to terminal."""
    summary = df.groupby('strategy').agg({
        "keyword_score": "mean",
        "tokens_in": "mean",
        "latency_ms": "mean",
        "cost_usd": "sum"
    }).round(4)

    table = RichTable(title='Prompt Strategy Benchmark Results', show_lines=True)
    table.add_column('Strategy', style='cyan')
    table.add_column('Avg Quality Score', style='green')
    table.add_column('Avg Input Tokens', style='yellow')
    table.add_column('Avg Latency (ms)', style='magenta')
    table.add_column('Total Cost (USD)', style='red')

    for strategy, row in summary.iterrows():
        table.add_row(
            strategy,
            str(row['keyword_score']),
            str(int(row['tokens_in'])),
            str(row['latency_ms']),
            f"${row['cost_usd']:.6f}"
        )

    console.print(table)


def save_results(df: pd.DataFrame, output_path: str = 'benchmark_results.csv'):
    df.to_csv(output_path, index=False)
    console.print(f'[green]Results saved to {output_path}[/green]')
