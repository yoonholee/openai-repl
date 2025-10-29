import os
import urllib.request

from repl_agent import REPLAgent


def download_moby_dick():
    url = "https://www.gutenberg.org/files/2701/2701-0.txt"
    output_path = "/tmp/moby_dick.txt"

    if os.path.exists(output_path):
        print(f"✓ Moby Dick already cached at {output_path}")
    else:
        print("Downloading Moby Dick from Project Gutenberg...")
        urllib.request.urlretrieve(url, output_path)
        print(f"✓ Downloaded to {output_path}")

    with open(output_path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"✓ Loaded: {len(text):,} characters ({len(text) / 1024:.1f} KB)")
    return text


def main():
    print("=" * 80)
    print("Classic Literature Analysis Demo - Moby Dick")
    print("=" * 80)
    print("\nAnalyzing 1.2MB of text - too large to fit in context window")
    print()

    book_text = download_moby_dick()

    print("\nInitializing REPL agent...")
    agent = REPLAgent(model="gpt-4o-mini")
    agent.load_context(context_str=book_text)
    print("✓ Book loaded as 'context' variable")

    print("\n" + "=" * 80)
    print("PART 1: Direct Code Execution")
    print("=" * 80)

    solution_code = """import re

# Extract all chapter titles using regex
chapter_pattern = r'CHAPTER\\s+\\d+\\.\\s*([^\\n]+)'
all_titles = re.findall(chapter_pattern, context)

# Find titles containing "whale" (case-insensitive)
whale_chapters = [title.strip() for title in all_titles if 'whale' in title.lower()]

print(f"Total chapters: {len(all_titles)}")
print(f"\\nChapters with 'whale' in title: {len(whale_chapters)}")
print("\\nChapter titles containing 'whale':")
for i, title in enumerate(whale_chapters, 1):
    print(f"  {i}. {title}")

len(whale_chapters)"""

    result = agent.run(solution_code)
    print(result)

    print("\n" + "=" * 80)
    print("PART 2: LLM-Driven Discovery")
    print("=" * 80)

    query = """The variable 'context' contains the full text of Moby Dick (1.2MB).

Find ALL chapter titles that contain the word "whale" (case-insensitive). Output the result as a list of chapter titles in order. Your result must include ONLY chapter titles (lines formatted like "CHAPTER 42. The Whiteness of the Whale"), not ordinary text from the book body. At the end of your responese, print the total number of chapter titles that contain the word "whale"."""

    print("\nQuery:", query)
    print("\n" + "-" * 80)

    response = agent.chat(query, max_iterations=10, verbose=True)

    print("\n" + "=" * 80)
    print("Final Response:")
    print("=" * 80)
    print(response)


if __name__ == "__main__":
    main()
