# AI Prompts Directory

This directory contains prompt templates and guidelines for using AI-assisted development tools in the Deployment Infrastructure blog series.

## Purpose

The prompts in this directory help maintain consistency when using local LLMs (Large Language Models) to:
- Generate boilerplate code and configurations
- Draft documentation
- Create architecture decision records
- Develop troubleshooting guides
- Generate test scenarios

## Structure

Each blog entry has a corresponding prompts file:
- `lab-baseline.md` - Prompts for Entry 01 (Lab Baseline)
- `terraform-hetzner.md` - Prompts for Entry 02 (Terraform Quickstart)
- `do-app.md` - Prompts for Entry 02b (DigitalOcean)
- _(Additional files as series progresses)_

## Workflow

### 1. Local LLM Setup

We recommend using [Ollama](https://ollama.ai) with models like:
- **CodeLlama** - Best for code generation
- **Mistral** - Good general-purpose model
- **Llama 2** - Good for documentation

Install Ollama:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull codellama
ollama pull mistral
```

### 2. Using Prompts

1. **Select appropriate prompt** from the entry-specific file
2. **Run prompt** through your local LLM
3. **Review output** critically
4. **Validate** in isolated environment
5. **Refine** as needed
6. **Document** any deviations

### 3. Safety Guidelines

⚠️ **Important Security Practices:**

- **Never share secrets** with AI models
- **Review all generated code** before use
- **Test in isolation** before deployment
- **Validate security-sensitive** configurations manually
- **Document changes** made to AI-generated content

## Best Practices

### Prompt Engineering

1. **Be Specific**: Include exact requirements
2. **Provide Context**: Mention environment and constraints
3. **Request Best Practices**: Ask for production-ready solutions
4. **Iterate**: Refine based on initial results
5. **Set Constraints**: Specify versions, limits, standards

### Code Review Checklist

Before accepting AI-generated code:
- [ ] Syntax is valid
- [ ] Follows project conventions
- [ ] Security best practices applied
- [ ] No hardcoded secrets
- [ ] Works in test environment
- [ ] Documentation is accurate
- [ ] Dependencies are appropriate

### Human-in-the-Loop

AI is a **tool to assist**, not replace human judgment:

1. **Generate** - Use AI for initial draft
2. **Review** - Critically examine output
3. **Test** - Validate in safe environment
4. **Refine** - Make necessary adjustments
5. **Verify** - Ensure it meets requirements
6. **Document** - Note changes and decisions

## Performance Expectations

### Hardware Requirements

| Configuration | Model Size | Performance |
|--------------|------------|-------------|
| Minimum | 7B params | 8GB RAM, slow inference |
| Recommended | 7B params | 16GB+ RAM, acceptable speed |
| Optimal | 13B params | 32GB RAM + GPU, fast |

### Response Times

- Small prompts (< 100 tokens): 5-15 seconds
- Medium prompts (100-500 tokens): 15-60 seconds  
- Large prompts (> 500 tokens): 1-3 minutes

## Alternative Tools

While we recommend Ollama for local LLM access, alternatives include:

- **LocalAI** - OpenAI-compatible API
- **LM Studio** - GUI-based local LLM runner
- **vLLM** - High-performance inference engine
- **OpenWebUI** - Web interface for Ollama

## Contributing Prompts

When adding new prompts:

1. **Create entry-specific file** (e.g., `entry-05-services.md`)
2. **Include prompt templates** with clear objectives
3. **Add usage examples** showing expected workflow
4. **Document caveats** and limitations
5. **Provide validation steps** for generated content

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [CodeLlama](https://ai.meta.com/blog/code-llama-large-language-model-coding/)
- [Mistral AI](https://mistral.ai/)

## Philosophy

AI-assisted development in this project follows these principles:

1. **Augmentation, not Replacement** - AI augments human capabilities
2. **Transparency** - Document AI usage and review process
3. **Safety First** - Security and correctness over speed
4. **Learning Focus** - Understand what AI generates
5. **Reproducibility** - Others can follow the same process

---

**Note**: This directory and workflow are part of the Deployment Infrastructure blog series. The goal is to demonstrate practical, safe, and effective use of AI tools in infrastructure development.
