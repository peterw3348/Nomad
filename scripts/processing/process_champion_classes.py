"""
process_champion_classes.py - Champion Class Extraction and Processing.

This script extracts champion class data from a Markdown document and saves the processed data
as JSON files categorized by class.

Functions:
    - extract_headings(md_content): Extracts section headings from the Contents section.
    - extract_sections(md_content): Parses Markdown content and extracts named sections.
    - extract_ratings(section_content): Extracts champion ratings from section content.
    - process_champion_classes(): Reads and processes the Markdown file, extracts data, and saves JSON outputs.

Usage:
Run this script to process champion classes from the Markdown file and generate JSON files.

Example:
python
    python process_champion_classes.py
"""

import os
import json
import re
from src.utils import paths

INPUT_PATH = paths.BASE_DIR / "docs" / "champion_classes.md"
OUTPUT_PATH = paths.ASSETS_DIR / "classes"

SECTION_PATTERN = re.compile(
    r"^START (.*?) ===\n(.*?)\nEND \1 ===", re.DOTALL | re.MULTILINE
)
HEADINGS_PATTERN = re.compile(r"^(.*?)\n-+$", re.MULTILINE)
RATINGS_PATTERN = re.compile(r'"Ratings": \{(.*?)\}', re.DOTALL)


def extract_headings(md_content):
    """
    Extract section headings from the Contents section of the Markdown file.

    Args:
        md_content (str): Markdown content as a string.

    Returns:
        list: A list of extracted headings.
    """
    contents_section = re.search(
        r"START Contents ===(.*?)END Contents ===", md_content, re.DOTALL
    )
    if not contents_section:
        raise ValueError("Failed to locate Contents section in the document.")

    contents_text = contents_section.group(1).strip()
    headings = [
        line.strip()
        for line in contents_text.split("\n")
        if line.strip() and not line.startswith("Contents")
    ]

    if not headings:
        raise ValueError("Failed to extract headings from the Contents section.")

    return headings


def extract_sections(md_content):
    """
    Parse the Markdown content and extracts named sections.

    Args:
        md_content (str): Markdown content as a string.

    Returns:
        dict: A dictionary mapping section titles to their content.
    """
    return {match[0]: match[1] for match in SECTION_PATTERN.findall(md_content)}


def extract_ratings(section_content):
    """
    Extract champion ratings from the section content.

    Args:
        section_content (str): Markdown section content.

    Returns:
        dict or None: A dictionary of ratings if found, otherwise None.
    """
    match = RATINGS_PATTERN.search(section_content)
    if match:
        ratings_json = "{" + match.group(1) + "}"
        return json.loads(ratings_json.replace("\n", "").replace(" ", ""))
    return None


def process_champion_classes():
    """Read and processes the Markdown file, extracts champion class data, and saves JSON outputs."""
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        md_content = f.read()

    headings = extract_headings(md_content)
    sections = extract_sections(md_content)

    print("Extracted Headings from Contents:\n", headings)
    print("Extracted Section Titles:\n", list(sections.keys()))

    # Verify contents match sections
    section_keys = section_keys = [s for s in sections.keys() if s != "Contents"]
    if set(headings) != set(section_keys):
        raise ValueError(
            "Mismatch between Contents section and actual sections in the document."
        )

    for section, content in sections.items():
        ratings = extract_ratings(content)
        if ratings:
            section_code = section.split(" ")[0]  # extract "A0", "B1", etc.
            section_name = "_".join(section.split(" ")[1:])
            file_name = f"{section_code}_{section_name}.json"
            output_dir = os.path.join(OUTPUT_PATH, section_code[0])
            output_path = os.path.join(output_dir, file_name)

            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as json_file:
                json.dump(ratings, json_file, indent=4)
            print(f"Saved {output_path}")


if __name__ == "__main__":
    """Entry point for processing champion class data."""
    process_champion_classes()
