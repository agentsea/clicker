import json
from datetime import datetime


def convert_jsonl_to_markdown(input_file: str, output_file: str = None):
    """Convert JSONL file with image queries to markdown format"""

    if output_file is None:
        # Create default output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"browsing_data_{timestamp}.md"

    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        # Write markdown header
        f_out.write("# Browser Interaction Dataset\n\n")
        f_out.write("Generated from JSONL data\n\n")
        f_out.write("---\n\n")

        # Process each line
        for idx, line in enumerate(f_in, 1):
            data = json.loads(line.strip())

            # Write entry header
            f_out.write(f"## Entry {idx}\n\n")

            # Write query
            f_out.write(f"**Query:** {data['query'].replace('<image>', '')}\n\n")

            # Write images
            for image_url in data["images"]:
                f_out.write(f"![Screenshot]({image_url})\n\n")

            # Write response (parse the JSON string)
            response = json.loads(data["response"])
            f_out.write("**Mouse Coordinates:**\n")
            f_out.write(f"- X: {response['x']}\n")
            f_out.write(f"- Y: {response['y']}\n\n")

            # Add separator
            f_out.write("---\n\n")

    print(f"Markdown file created: {output_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python convert_to_markdown.py <input_jsonl_file> [output_markdown_file]"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_jsonl_to_markdown(input_file, output_file)
