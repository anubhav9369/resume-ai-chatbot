# benchmark.py — Run from project root: python benchmark.py
import argparse
from dotenv import load_dotenv
from src.evaluator import run_benchmark, print_summary, save_results

load_dotenv()

parser = argparse.ArgumentParser(description='Benchmark prompt strategies')
parser.add_argument('--resume', default='data/sample_resume.txt')
parser.add_argument('--questions', default='data/test_questions.json')
parser.add_argument('--output', default='benchmark_results.csv')
args = parser.parse_args()

print('\n🚀 Running prompt strategy benchmark...')
print(f'  Resume: {args.resume}')
print(f'  Questions: {args.questions}')

df = run_benchmark(args.resume, args.questions)
print_summary(df)
save_results(df, args.output)

print('\n✅ Benchmark complete. Add results to your README!')
