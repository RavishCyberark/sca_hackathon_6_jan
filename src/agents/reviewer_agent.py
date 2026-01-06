"""Reviewer Agent - Validates and improves generated API test code."""

from crewai import Agent, LLM

from src.config.settings import get_settings


def create_reviewer_agent() -> Agent:
    """Create the Reviewer Agent that validates generated API test code.
    
    This agent is responsible for:
    - Reviewing generated API test code for quality
    - Checking authentication implementation
    - Validating assertion completeness
    - Ensuring proper error handling
    - Verifying SSL/TLS configuration
    """
    settings = get_settings()
    
    llm = LLM(
        model=settings.ollama.get_model_string(),
        base_url=settings.ollama.base_url,
        temperature=settings.ollama.temperature,
    )
    
    return Agent(
        role="API Test Code Reviewer & Quality Assurance",
        goal="""Review generated API test code for quality, completeness, 
        and best practices. Ensure authentication is properly implemented, 
        assertions are comprehensive, and error handling is robust.""",
        backstory="""You are a senior QA engineer and code reviewer with 
        extensive experience in API test automation. You have a keen eye for 
        code quality, security issues, and API testing best practices. You 
        ensure that all generated tests have proper authentication, handle 
        SSL certificates correctly, include meaningful assertions, and follow 
        Python coding standards. You verify that tests are production-ready 
        with proper error handling and debug output.""",
        llm=llm,
        verbose=settings.verbose,
        allow_delegation=False,
        memory=True,
    )


# Review guidelines for the agent
REVIEWER_GUIDELINES = """
## API Test Review Checklist

### 1. Imports and Dependencies
- [ ] `import pytest` present
- [ ] `import requests` present
- [ ] `import json` present
- [ ] `import urllib3` for SSL warning suppression

### 2. Authentication
- [ ] Token URL is correct
- [ ] Credentials are properly configured
- [ ] Token extraction handles errors
- [ ] Bearer token format is correct
- [ ] Auth header included in requests

### 3. SSL/TLS Configuration
- [ ] `verify=False` for self-signed certificates
- [ ] SSL warnings suppressed
- [ ] Applied to ALL requests (token + API)

### 4. Request Configuration
- [ ] Correct HTTP method used
- [ ] Proper Content-Type header
- [ ] Payload structure matches API spec
- [ ] URL construction is correct

### 5. Assertions
- [ ] Status code assertion present
- [ ] Response body validation
- [ ] Error message validation for negative tests
- [ ] Descriptive assertion messages

### 6. Code Quality
- [ ] PEP 8 style compliance
- [ ] Meaningful variable names
- [ ] Proper docstrings with Given-When-Then
- [ ] Debug print statements for troubleshooting
- [ ] Proper error handling

### 7. Test Structure
- [ ] Class name starts with "Test"
- [ ] Method names start with "test_"
- [ ] Setup fixture with autouse=True
- [ ] Proper cleanup in yield fixture

## Common Issues to Fix

1. **Missing SSL Config**: Add `verify=False` to all requests
2. **Missing Auth Header**: Ensure Authorization header is set
3. **Wrong Content-Type**: Should be "application/json"
4. **Missing Assertions**: Add response validation
5. **No Error Handling**: Add try-except for token retrieval

## Review Output Format

```json
{
  "is_valid": true|false,
  "review_notes": ["observation 1", "observation 2"],
  "improvements_made": ["fix 1", "fix 2"],
  "final_code": "complete corrected Python code"
}
```
"""
