from openai import OpenAI
import json
import glob
import sys


if len(sys.argv) > 1:
    message = sys.argv[1]
else:
    message = "You are an expert translator. Please review and correct the following translations, which are firmware translations for a Bitcoin signing device. Please keep technical terms in English and ensure the translations are accurate and consistent. Only provide the corrected JSON content without any explanations."


def get_api_key(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


api_key_path = "/home/eduardo/open_ai.txt"
api_key = get_api_key(api_key_path)
client = OpenAI(api_key=api_key)

# Set up your OpenAI API key


# Function to read and correct translation files
def review_translation(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Constructing a message to ask for a review

    messages = [
        {"role": "system", "content": message},
        {"role": "user", "content": json.dumps(data, indent=2)},
    ]

    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1500,  # Adjust based on the size of your data
        temperature=0.5,
    )

    # Extracting the suggestions
    corrected_data = response.choices[0].message.content.strip()
    # Split the data into lines
    lines = corrected_data.splitlines()

    # Remove lines that start with the ``` prefix
    stripped_lines = [line for line in lines if not line.startswith("```")]

    corrected_data = "\n".join(stripped_lines)

    # Assuming corrected data is a valid JSON string
    try:
        corrected_data = json.loads(corrected_data)
    except json.JSONDecodeError as e:
        print(f"Error decoding corrected JSON data: {e}")
        print(f"Corrected data:\n{corrected_data}")
        return None

    return corrected_data


# Function to update the JSON file
def update_translation(file_path, corrected_data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)


# Loop through JSON translation files and correct them
for file_path in glob.glob(
    "translations/*.json"
):  # Assuming translation files are in a folder called 'translations'
    corrected_data = review_translation(file_path)
    if corrected_data:
        update_translation(file_path, corrected_data)
        print(f"Corrected and updated file: {file_path}")
    else:
        print(f"Failed to correct file: {file_path}")
