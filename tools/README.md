# Tools

This directory contains automation tools for the project. Add scripts and utilities here to support workflows, automation, and blog content creation.

## Current Tools

- **ollama_query.py**: Python script to query Ollama with prompts and file contents. Useful for generating content, automating tasks, and integrating AI into blog workflows.

## Adding More Tools

Add new scripts to this folder as needed. Document their purpose and usage in this README.


## Example Usages

Below are example commands using `ollama_query.py` for common automation tasks:

### 1. Create a Logo Based on a Prompt

```sh
python ollama_query.py "Create a fancy and elaborate logo for a tech blog about automation. Have some gears and a robot fixing them. Describe the logo in correct SVG format with propper namespace, usabel directly in browsers." --model llama3.1
```

### 2. Generate a Docker Compose YAML Based on a Prompt

```sh
python ollama_query.py "Generate a docker-compose.yaml for a web app with a Python backend and a PostgreSQL database." --model llama3.1
```

### 3. Translate Text Based on a Prompt

```sh
python ollama_query.py "Translate the following text to German: Hello, welcome to my blog!" --model llama3.1
```

### 4. Transcribe an Audio File into Markdown Text

```sh
python ollama_query.py "Transcribe the following audio file into markdown text." --file path/to/audiofile.wav --model llama3.1
```

You can adjust the prompt and model as needed for your workflow.
