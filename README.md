# AI-Powered API Test Case Generator

A CrewAI multi-agent system that generates **API automation test cases** (pytest + requests) from text scenarios using Ollama with free, open-source LLMs. Optionally pushes generated tests to GitHub and creates Pull Requests.

## Features

- **Multi-Agent Architecture**: 5 specialized agents working together
  - **Parser Agent**: Interprets Gherkin/BDD, plain English, or user story formats
  - **Analyzer Agent**: Identifies API endpoints, authentication, and validation requirements
  - **Generator Agent**: Creates pytest + requests API test code
  - **Reviewer Agent**: Validates code quality, assertions, and best practices
  - **GitHub Agent**: Creates branches, commits, and Pull Requests (uses CrewAI task)

- **Zero Cost**: Uses Ollama (local LLM) + GitHub CLI (browser auth)
- **No API Keys Required**: Everything runs locally or uses browser authentication
- **API Testing Focus**: OAuth2 authentication, REST API testing, SSL handling
- **Multiple Input Formats**: Gherkin/BDD, plain English, user stories

## Prerequisites

### 1. Ollama (Local LLM)

```bash
# Install Ollama
brew install ollama

# Start the server
ollama serve

# Pull the recommended model
ollama pull qwen2.5-coder:7b
```

### 2. GitHub CLI (for PR feature)

```bash
# Install GitHub CLI
brew install gh

# Authenticate (opens browser)
gh auth login
```

## Installation

```bash
# Clone or navigate to the project
cd sca_hackathon_6_jan

# Run setup script (creates venv and installs dependencies)
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source .venv/bin/activate
```

## Usage

### Quick Start Commands

```bash
# Activate virtual environment first
source .venv/bin/activate
```

---

### Option 1: Generate Tests Only (No GitHub)

Generate API test cases from scenario file without pushing to GitHub:

```bash
python -m src.main --input input/api_scenario_create_policy.txt --output output/generated_tests/
```

**What this does:**
- ✅ Runs Parser Agent → Analyzer Agent → Generator Agent → Reviewer Agent
- ✅ Generates pytest API test code
- ✅ Saves to `output/generated_tests/`
- ❌ Does NOT push to GitHub

---

### Option 2: Generate Tests AND Create Pull Request

Generate tests and automatically push to GitHub with a new branch and PR:

```bash
python -m src.main --input input/api_scenario_create_policy.txt --push-pr
```

**What this does:**
- ✅ Runs Parser Agent → Analyzer Agent → Generator Agent → Reviewer Agent
- ✅ Generates pytest API test code
- ✅ Saves to `output/generated_tests/`
- ✅ Runs **GitHub Agent** (CrewAI task)
- ✅ Creates new branch (e.g., `test/auto-generated-<feature>`)
- ✅ Commits and pushes changes
- ✅ Creates Pull Request

---

### Option 3: Specify Base Branch for PR

Target a different branch (e.g., `develop`) for the Pull Request:

```bash
python -m src.main --input input/api_scenario_create_policy.txt --push-pr --base-branch develop
```

---

### Option 4: Use Different Ollama Model

```bash
python -m src.main --input input/api_scenario_create_policy.txt --model llama3.1:8b
```

---

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input`, `-i` | Input scenario file path | **Required** |
| `--output`, `-o` | Output directory for tests | `output/generated_tests/` |
| `--push-pr` | Push to GitHub and create PR | `False` |
| `--base-branch` | Target branch for PR | `main` |
| `--model` | Ollama model name | `qwen2.5-coder:7b` |
| `--verbose`, `-v` | Verbose output | `False` |

---

### Running Generated Tests

After tests are generated, run them with pytest:

```bash
# Run all generated tests
pytest output/generated_tests/ -v

# Run with detailed output
pytest output/generated_tests/ -v -s

# Run specific test file
pytest output/generated_tests/test_create_policy_api_description_field_validation.py -v -s
```

## Input Formats

The system accepts multiple input formats for API testing:

### Gherkin/BDD (Recommended for API)

```gherkin
Feature: Create Policy API Description Field Validation

Scenario: Successfully create policy with valid description (string, under 200 chars)
  Given the user obtains OAuth2 token from the token endpoint
  And the policy payload has description "Valid test policy description"
  When the user sends a POST request to "/policies" with valid payload
  Then the response status code should be 200 or 201
  And the response should contain the created policy details

Scenario: Policy creation fails with null description
  Given the user obtains OAuth2 token from the token endpoint
  And the policy payload has description set to null
  When the user sends a POST request to "/policies" with the payload
  Then the response status code should indicate a client error (e.g., 400)
  And the response body should contain an error message related to invalid description
```

### Plain English

```
Test Create Policy API:
1. Get OAuth2 token from authentication endpoint
2. Send POST request to /policies with valid payload
3. Verify response status is 200 or 201
4. Verify response contains policy data

Negative Test:
1. Get OAuth2 token
2. Send POST request with null description
3. Verify response status is 400
4. Verify error message in response
```

### User Story

```
As an API consumer
I want to create policies via REST API
So that I can automate policy management

Acceptance Criteria:
- API requires OAuth2 Bearer token
- Description field must be a string
- Description field max length is 200 characters
- Invalid description returns 400 error
```

## Project Structure

```
sca_hackathon_6_jan/
├── src/
│   ├── main.py                   # CLI entry point
│   ├── config/
│   │   └── settings.py           # Configuration
│   ├── agents/
│   │   ├── parser_agent.py       # Scenario parser
│   │   ├── analyzer_agent.py     # Test analyzer
│   │   ├── generator_agent.py    # Code generator
│   │   ├── reviewer_agent.py     # Code reviewer
│   │   └── github_agent.py       # GitHub operations
│   ├── tasks/
│   │   └── test_generation_tasks.py
│   ├── crew/
│   │   └── test_crew.py          # Agent orchestration
│   ├── models/
│   │   └── schemas.py            # Data models
│   ├── templates/
│   │   └── api_test.j2          # API test template
│   └── utils/
│       ├── file_handler.py
│       ├── prompt_templates.py
│       └── git_utils.py
├── input/
│   └── sample_scenarios.txt
├── output/
│   └── generated_tests/
├── requirements.txt
├── setup.sh
└── README.md
```

## Recommended Ollama Models

| Model | Size | RAM | Quality | Use Case |
|-------|------|-----|---------|----------|
| qwen2.5-coder:7b | 4.7GB | 8GB | Good | Default, fast |
| qwen2.5-coder:14b | 9GB | 16GB | Better | Higher quality |
| llama3.1:8b | 4.7GB | 8GB | Good | Alternative |
| codellama:13b | 7.4GB | 16GB | Good | Code-focused |

## Troubleshooting

### Ollama Connection Error

```bash
# Ensure Ollama is running
ollama serve

# Verify it's accessible
curl http://localhost:11434/api/tags
```

### GitHub CLI Not Authenticated

```bash
# Re-authenticate
gh auth login
gh auth status
```

### Model Not Found

```bash
# List available models
ollama list

# Pull the required model
ollama pull qwen2.5-coder:7b
```

## License

MIT License

