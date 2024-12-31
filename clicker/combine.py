import glob
import json
from pathlib import Path


def combine_jsonl_files(input_pattern: str, output_file: str):
    """
    Combine multiple JSONL files into a single JSONL file.

    Args:
        input_pattern: Glob pattern to match input files (e.g., "browsing_queries_*.jsonl")
        output_file: Path to the output combined file
    """
    # Get all matching files
    input_files = glob.glob(input_pattern)

    if not input_files:
        print(f"No files found matching pattern: {input_pattern}")
        return

    total_examples = 0

    # Create output directory if it doesn't exist
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Combine files
    with open(output_file, "w") as outfile:
        for input_file in input_files:
            print(f"Processing: {input_file}")
            with open(input_file, "r") as infile:
                for line in infile:
                    # Verify it's valid JSON before writing
                    try:
                        json.loads(line.strip())
                        outfile.write(line)
                        total_examples += 1
                    except json.JSONDecodeError:
                        print(f"Skipping invalid JSON line in {input_file}")

    print(f"\nCombined {len(input_files)} files")
    print(f"Total examples: {total_examples}")
    print(f"Output saved to: {output_file}")


if __name__ == "__main__":
    # Example usage
    combine_jsonl_files(
        input_pattern="browsing_queries_*.jsonl",
        output_file="combined/all_browsing_queries.jsonl",
    )
