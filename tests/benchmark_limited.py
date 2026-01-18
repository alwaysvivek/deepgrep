
import time
import tracemalloc
import random
import string
import os

# Mock spacy if needed, or just don't import semantic engine
from deepgrep.core.engine import find_matches
from deepgrep.core.history import SearchHistoryDB

def random_line(length=1000):
    return ''.join(random.choices(string.ascii_letters + " ", k=length))

def generate_lines(n=10000, length=1000):
    return [random_line(length) for _ in range(n)]

def complex_pattern():
    return r"(\w+)\s+\1|foo(bar)?|a.*b+"

def run_benchmark():
    lines = generate_lines(100, 500)
    pattern = complex_pattern()

    print("=== Engine/Matcher Benchmark ===")
    tracemalloc.start()
    start = time.time()
    match_count = sum(len(find_matches(line, pattern)) for line in lines)
    end = time.time()
    mem_current, mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Matches found: {match_count}")
    print(f"Time: {end - start:.2f}s")
    print(f"Peak Mem: {mem_peak/1e6:.2f}MB")
    print(f"Throughput: {1000 / (end - start):.2f} lines/sec")

    print("\n=== History DB Benchmark ===")
    # Use in-memory DB or temp file to avoid messing with real DB if configured
    # SearchHistoryDB uses config for path, so might need to patch or just use it (it uses ~/.grepify_history.db by default or env)
    # Let's set env var to use a temp db
    os.environ["DB_PATH"] = ":memory:" 
    
    db = SearchHistoryDB()
    start = time.time()
    for i in range(1000):
        db.log_search(pattern, random.randint(0, 10), ["file1", "file2"])
    end = time.time()
    print(f"Logged 1000 searches in {end - start:.2f}s")
    print(f"Write Throughput: {1000 / (end - start):.2f} ops/sec")

if __name__ == "__main__":
    run_benchmark()
