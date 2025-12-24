"""
ollama_query.py
A utility script to query Ollama with files and prompts for automation and blog workflows.
"""
import requests
import sys
import os

OLLAMA_API_BASE = os.getenv('OLLAMA_API_BASE', 'http://dsk-001.fritz.box:11434')
OLLAMA_API_URL = f"{OLLAMA_API_BASE}/api/generate"


def is_model_installed(model):
    """
    Check if the specified model is installed on the Ollama server.
    Returns True if installed, False otherwise.
    """
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/api/tags")
        response.raise_for_status()
        tags = response.json().get('models', [])
        for m in tags:
            if m.get('name', '').split(':')[0] == model.split(':')[0]:
                return True
        return False
    except Exception as e:
        print(f"Error checking model: {e}")
        return False


def query_ollama(prompt, file_path=None, model='llama2'):
    """
    Query Ollama with a prompt and optional file content.
    Args:
        prompt (str): The prompt to send to Ollama.
        file_path (str, optional): Path to a file whose content will be appended to the prompt.
        model (str): The Ollama model to use.
    Returns:
        str: The response from Ollama.
    """
    if not is_model_installed(model):
        raise RuntimeError(f"Model '{model}' is not installed on the Ollama server.")
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        prompt = f"{prompt}\n\n---\nFile Content:\n{file_content}"

    payload = {
        'model': model,
        'prompt': prompt,
        'stream': False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    response.raise_for_status()
    return response.json().get('response', '')


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Query Ollama with a prompt and optional file.')
    parser.add_argument('prompt', type=str, help='Prompt to send to Ollama')
    parser.add_argument('--file', type=str, help='Path to file to include in prompt', default=None)
    parser.add_argument('--model', type=str, help='Ollama model to use', default='llama2')
    args = parser.parse_args()

    try:
        result = query_ollama(args.prompt, args.file, args.model)
        # Determine file type from prompt
        lower_prompt = args.prompt.lower()
        output_file = None
        if 'svg' in lower_prompt or 'logo' in lower_prompt:
            output_file = '../static/img/logo.svg'
        elif 'docker-compose' in lower_prompt or 'yaml' in lower_prompt:
            output_file = '../docker-compose.yaml'
        elif 'transcribe' in lower_prompt or 'markdown' in lower_prompt:
            output_file = '../transcription.md'
        elif 'translate' in lower_prompt:
            output_file = '../translation.txt'

        # Extract content between triple backticks if present
        def extract_code_block(text):
            import re
            matches = re.findall(r'```(?:[a-zA-Z0-9]+)?\n([\s\S]*?)```', text)
            if matches:
                return '\n'.join([m.strip() for m in matches])
            return text.strip()

        file_content = extract_code_block(result) if output_file else result

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(file_content)
            print(f"Response saved to {output_file}")
        else:
            print(file_content)
    except RuntimeError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
