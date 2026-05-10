#!/usr/bin/env python3
"""
AI Translation Script for Sports2D-Web i18n locales.

Usage:
  1. Install openai (or another AI SDK): pip install openai
  2. Set your OPENAI_API_KEY environment variable.
  3. Run: python translate_locales.py --source en --target fr --input src/i18n/locales/en.json --output src/i18n/locales/fr.json

This script reads a source JSON locale file, sends the content to an AI model for translation,
and writes the translated JSON to the target file. It preserves the nested structure.
"""

import argparse
import json
import os
from pathlib import Path

# Example using OpenAI API. Replace with your preferred AI provider.
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def translate_text(text: str, target_lang: str, client: OpenAI) -> str:
    """Translate a single string using an AI model."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a professional translator for a sports biomechanics web application. "
                    f"Translate the following UI text to {target_lang}. "
                    f"Keep placeholders like {{size}}, {{duration}}, {{index}} exactly as they are. "
                    f"Keep technical terms like 'Inverse Kinematics', 'OpenSim', 'Butterworth' in English if there is no common translation. "
                    f"Reply with ONLY the translated text, no explanations."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def translate_dict(obj, target_lang: str, client: OpenAI):
    """Recursively translate all string values in a nested dict."""
    if isinstance(obj, dict):
        return {k: translate_dict(v, target_lang, client) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [translate_dict(item, target_lang, client) for item in obj]
    elif isinstance(obj, str):
        return translate_text(obj, target_lang, client)
    else:
        return obj

def main():
    parser = argparse.ArgumentParser(description="Translate i18n locale files via AI")
    parser.add_argument("--source", required=True, help="Source language code (e.g. en)")
    parser.add_argument("--target", required=True, help="Target language code (e.g. fr)")
    parser.add_argument("--input", required=True, help="Path to source JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    args = parser.parse_args()

    if OpenAI is None:
        print("Error: openai package not installed. Run: pip install openai")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return

    client = OpenAI(api_key=api_key)

    source_path = Path(args.input)
    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}")
        return

    with open(source_path, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    print(f"Translating from {args.source} to {args.target}...")
    translated = translate_dict(source_data, args.target, client)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    print(f"Done. Translated file saved to: {output_path}")

if __name__ == "__main__":
    main()
