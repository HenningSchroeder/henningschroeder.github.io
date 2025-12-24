# AI Prompts for Lab Baseline

This document contains prompt templates used with local LLMs (Ollama with CodeLlama/Mistral) during the development of the Lab Baseline infrastructure.

## Setup

**Local LLM Requirements:**
- Ollama installed ([ollama.ai](https://ollama.ai))
- Model: CodeLlama, Mistral, or Llama 2
- Minimum 8GB RAM for 7B models, 16GB+ recommended

**Installation:**
```bash
# Install Ollama (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull codellama
ollama pull mistral
```

**Pull Models via API:**
```bash
# Pull CodeLlama model via API (assuming Ollama on dsk-001)
curl -X POST http://dsk-001:11434/api/pull -d '{
  "name": "codellama"
}'

# Pull Mistral model via API
curl -X POST http://dsk-001:11434/api/pull -d '{
  "name": "mistral"
}'

# Pull specific model version
curl -X POST http://dsk-001:11434/api/pull -d '{
  "name": "codellama:7b"
}'
```

## Prompt Templates

### 1. Dockerfile Generation

```
Generate a production-ready Dockerfile for a FastAPI application with the following requirements:
- Base image: Python 3.12 slim
- Application runs on port 8000 using uvicorn
- Includes health check endpoint
- Optimized for layer caching
- Non-root user execution
- Minimal image size

Include best practices for:
- Dependency installation
- Security hardening
- Multi-stage builds if beneficial
```

### 2. Docker Compose Configuration

```
Create a docker-compose.yml file for a development environment with:
- Nginx reverse proxy on port 80
- FastAPI backend service
- Proper networking between services
- Health checks for the API
- Volume mounts for configuration
- Environment variables for configuration
- Restart policies

Ensure the configuration is production-ready but suitable for local development.
```

### 3. Nginx Reverse Proxy Configuration

```
Generate an Nginx configuration file that:
- Serves static files from /usr/share/nginx/html on /
- Proxies /api/* to a backend service named 'api' on port 8000
- Includes proper proxy headers (X-Real-IP, X-Forwarded-For, etc.)
- Handles CORS if needed
- Uses minimal worker configuration suitable for development

Format as a complete nginx.conf file.
```

### 4. FastAPI Application Boilerplate

```
Create a minimal FastAPI application with the following endpoints:
- GET / - Returns basic info, timestamp, and hostname
- GET /health - Returns service health status
- GET /info - Returns service metadata

Include:
- Proper type hints
- Async handlers
- Environment variable reading for configuration
- Application title and version in FastAPI initialization
```

### 5. Makefile for Docker Operations

```
Create a Makefile with targets for common Docker Compose operations:
- up: Start services
- down: Stop services
- restart: Restart services
- logs: Show logs
- ps: Show container status
- build: Build images
- clean: Remove containers and prune system
- status: Show detailed status
- test: Test all service endpoints using curl

Include a help target that displays all available targets with descriptions.
```

### 6. System Setup Documentation

```
Write step-by-step instructions for installing Docker and Docker Compose on Ubuntu 24.04 LTS:
- Add Docker's official repository
- Install Docker Engine, CLI, and Compose plugin
- Configure user permissions
- Enable Docker service
- Verify installation

Format as a technical runbook with code blocks and verification steps.
```

### 7. Troubleshooting Guide

```
Generate a troubleshooting section for common Docker and Docker Compose issues:
- Containers won't start
- Port conflicts
- Permission denied errors
- Networking issues
- Resource constraints
- Differences between docker and podman

For each issue, provide:
- Symptoms
- Diagnostic commands
- Resolution steps
- create a minimal python script which gathers the info from a running system and pushes the data with matching prompt into the ollama  instance for analysis.
```

### 8. Architecture Decision Record (ADR)

```
Write an Architecture Decision Record for choosing:
- Virtual Machine vs Bare Metal for lab environment
- Docker Compose vs Kubernetes for container orchestration
- Ubuntu LTS vs other Linux distributions
- Resource allocation (2 vCPU, 4GB RAM, 20GB disk)

Format as a structured ADR with:
- Status
- Context
- Decision
- Rationale
- Consequences
- Alternatives considered
```

## Usage Examples

### Interactive CLI Usage

```bash
# Start interactive session
ollama run codellama

# Paste prompt, review output, iterate
```

### Ollama in Container (Podman Compose)

For environments using Podman instead of Docker, you can run Ollama in a container:

**podman-compose.yml:**
```yaml
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama-data:
```

**Usage:**
```bash
# Start Ollama service
podman-compose up -d

# Pull models into container
podman exec -it ollama ollama pull codellama
podman exec -it ollama ollama pull mistral

# Interactive session
podman exec -it ollama ollama run codellama

# API access (same as native install)
curl http://localhost:11434/api/generate -d '{
  "model": "codellama",
  "prompt": "Your prompt here",
  "stream": false
}'

# Stop service
podman-compose down
```

**Note**: Replace `podman-compose` with `docker-compose` if using Docker.

```bash
# Start interactive session
ollama run codellama

# Paste prompt, review output, iterate
```

### API Usage (Programmatic)

```bash
# Single prompt
curl http://localhost:11434/api/generate -d '{
  "model": "codellama",
  "prompt": "Generate a Dockerfile for FastAPI...",
  "stream": false
}'
```

### Python Script

```python
import requests
import json

def generate_with_llm(prompt, model="codellama"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]

# Example usage
dockerfile_prompt = "Generate a production-ready Dockerfile for FastAPI..."
dockerfile = generate_with_llm(dockerfile_prompt)
print(dockerfile)
```

## Best Practices

### Human-in-the-Loop Review

1. **Generate**: Use AI to create initial configuration
2. **Review**: Manually inspect all generated code
3. **Validate**: Test in isolated environment
4. **Refine**: Make necessary adjustments
5. **Document**: Note deviations from AI suggestions

### Security Considerations

- **Never share secrets** with AI models
- **Review security-sensitive** configurations manually
- **Validate** all generated Dockerfiles for vulnerabilities
- **Test** in isolated environment before production use

### Quality Checks

Before accepting AI-generated code:
- [ ] Syntax is valid
- [ ] Best practices are followed
- [ ] Security considerations are addressed
- [ ] Configuration works in test environment
- [ ] Documentation is accurate
- [ ] No hardcoded secrets or credentials

## Model Comparison

| Model | Use Case | Pros | Cons |
|-------|----------|------|------|
| CodeLlama | Code generation | Best for code, understands context | Larger model size |
| Mistral | General purpose | Fast, good balance | Less specialized for code |
| Llama 2 | Documentation | Good for text, explanations | Not code-focused |

**Recommendation:** Use CodeLlama for code generation, Mistral for mixed tasks, Llama 2 for documentation.

## Prompt Engineering Tips

1. **Be Specific**: Include exact requirements and constraints
2. **Provide Context**: Mention the environment and use case
3. **Request Best Practices**: Explicitly ask for production-ready code
4. **Iterate**: Refine prompts based on initial output
5. **Request Explanations**: Ask the model to explain its choices
6. **Set Constraints**: Specify versions, sizes, or other limits

## Performance Considerations

### Hardware Requirements

- **Minimum**: 8GB RAM, 4-core CPU for 7B models
- **Recommended**: 16GB+ RAM, 8-core CPU for faster inference
- **GPU**: Optional but significantly faster (CUDA-compatible)

### Response Time Expectations

- **Small prompts (< 100 tokens)**: 5-15 seconds
- **Medium prompts (100-500 tokens)**: 15-60 seconds
- **Large prompts (> 500 tokens)**: 1-3 minutes

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [CodeLlama Guide](https://ai.meta.com/blog/code-llama-large-language-model-coding/)
- [Mistral AI](https://mistral.ai/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

**Note**: This is a living document. Update as new prompts are developed and tested.
