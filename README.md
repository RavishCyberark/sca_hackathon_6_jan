# AI-Powered Test Case Generator

A CrewAI multi-agent system that generates Playwright Python test cases from text scenarios using Ollama with free, open-source LLMs. Optionally pushes generated tests to GitHub and creates Pull Requests.

## Features

- **Multi-Agent Architecture**: 5 specialized agents working together
  - Parser Agent: Interprets Gherkin, plain English, or user story formats
  - Analyzer Agent: Identifies page elements, actions, and assertions
  - Generator Agent: Creates Playwright Python test code
  - Reviewer Agent: Validates code quality and best practices
  - GitHub Agent: Creates branches, commits, and Pull Requests

- **Zero Cost**: Uses Ollama (local LLM) + GitHub CLI (browser auth)
- **No API Keys Required**: Everything runs locally or uses browser authentication
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

### Generate Tests Only

```bash
python -m src.main --input input/sample_scenarios.txt --output output/generated_tests/
```

### Generate Tests and Create Pull Request

```bash
python -m src.main --input input/sample_scenarios.txt --push-pr
```

### Specify Base Branch for PR

```bash
python -m src.main --input input/sample_scenarios.txt --push-pr --base-branch develop
```

### Use Different Ollama Model

```bash
python -m src.main --input input/sample_scenarios.txt --model llama3.1:8b
```

## Input Formats

The system accepts multiple input formats:

### Gherkin/BDD

```gherkin
Feature: User Login
  Scenario: Successful login
    Given the user is on the login page
    When the user enters username "test@example.com"
    And the user enters password "password123"
    And the user clicks the login button
    Then the user should see the dashboard
```

### Plain English

```
Test that a user can log in successfully:
1. Go to the login page
2. Enter email "test@example.com"
3. Enter password "password123"
4. Click the login button
5. Verify the dashboard is displayed
```

### User Story

```
As a registered user
I want to log into my account
So that I can access my dashboard

Acceptance Criteria:
- User can enter email and password
- Valid credentials redirect to dashboard
- Welcome message displays user's name
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
│   │   ├── playwright_test.j2
│   │   └── page_object.j2
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

