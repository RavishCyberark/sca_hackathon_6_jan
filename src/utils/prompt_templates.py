"""Reusable prompt templates for API test generation agents."""


class PromptTemplates:
    """Collection of prompt templates for API test agent tasks."""
    
    @staticmethod
    def parse_scenario_prompt(scenario_text: str) -> str:
        """Generate prompt for parsing an API test scenario.
        
        Args:
            scenario_text: Raw scenario text
            
        Returns:
            Formatted prompt
        """
        return f"""
Parse the following API test scenario and extract structured information.

## Input Scenario
```
{scenario_text}
```

## Instructions
1. Identify the format (Gherkin, plain English, or user story)
2. Extract the feature name and scenario name
3. Identify the API endpoint URL and HTTP method
4. Extract authentication details (token URL, credentials)
5. Break down into individual steps
6. For each step, identify:
   - Step type (Given/When/Then/And)
   - The API action being described
   - Target endpoint or field
   - Expected status codes or values

## Output Format
Provide the parsed scenario as a JSON object:
```json
{{
  "feature_name": "string",
  "scenario_name": "string",
  "api_endpoint": "full URL",
  "http_method": "POST|GET|PUT|DELETE",
  "authentication": {{
    "token_url": "string",
    "username": "string",
    "password": "string"
  }},
  "steps": [
    {{
      "step_type": "given|when|then|and",
      "description": "original step text",
      "action": "get_token|send_request|verify_status|verify_response",
      "target": "endpoint or field",
      "value": "expected value"
    }}
  ]
}}
```
"""

    @staticmethod
    def analyze_test_prompt(parsed_scenario: str) -> str:
        """Generate prompt for analyzing a parsed API scenario.
        
        Args:
            parsed_scenario: JSON string of parsed scenario
            
        Returns:
            Formatted prompt
        """
        return f"""
Analyze the following parsed API test scenario and create a test blueprint.

## Parsed Scenario
```json
{parsed_scenario}
```

## Instructions
1. Determine the authentication flow (OAuth2, Basic Auth, API Key)
2. Map test steps to requests library methods
3. Identify expected status codes for positive/negative tests
4. Determine response field validations

## Action Mapping
- get_token → session.post() to token endpoint
- send_request → session.post/get/put/delete() to API endpoint
- verify_status → assert response.status_code == expected
- verify_response → assert on response.json() fields

## Output Format
Provide a test blueprint as JSON:
```json
{{
  "class_name": "TestAPIClassName",
  "test_methods": [
    {{
      "method_name": "test_scenario_name",
      "test_type": "positive|negative",
      "docstring": "Test description",
      "payload_modifications": [],
      "expected_status": 200|201|400,
      "assertions": []
    }}
  ],
  "authentication": {{
    "token_url": "...",
    "username": "...",
    "password": "..."
  }},
  "base_payload": {{}}
}}
```
"""

    @staticmethod
    def generate_test_prompt(blueprint: str) -> str:
        """Generate prompt for creating API test code.
        
        Args:
            blueprint: JSON string of test blueprint
            
        Returns:
            Formatted prompt
        """
        return f"""
Generate a complete pytest API test file from the following blueprint.

## Test Blueprint
```json
{blueprint}
```

## Requirements
1. Use pytest with requests library
2. Include imports: pytest, requests, json, urllib3
3. Suppress SSL warnings with urllib3.disable_warnings()
4. Create a test class with OAuth2 authentication fixture
5. Implement test methods with proper docstrings
6. Add Given/When/Then comments to organize the code
7. Use assert statements for all assertions
8. Include debug print statements

## Template Structure
```python
\"\"\"API Test module for [Feature].\"\"\"

import pytest
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TestClassName:
    \"\"\"API Test cases for [Feature].\"\"\"
    
    TOKEN_URL = "..."
    API_BASE_URL = "..."
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.verify = False
        self.access_token = self._get_access_token()
        self.headers = {{
            "Content-Type": "application/json",
            "Authorization": f"Bearer {{self.access_token}}"
        }}
        yield
        self.session.close()
    
    def _get_access_token(self) -> str:
        response = self.session.post(
            self.TOKEN_URL,
            data={{"grant_type": "client_credentials", "scope": "full"}},
            auth=("username", "password"),
            verify=False
        )
        return response.json().get("access_token")
    
    def get_base_payload(self) -> dict:
        return {{...}}
    
    @pytest.mark.positive
    def test_method_name(self):
        \"\"\"Given-When-Then docstring\"\"\"
        # Given
        payload = self.get_base_payload()
        
        # When
        response = self.session.post(
            f"{{self.API_BASE_URL}}/endpoint",
            json=payload,
            headers=self.headers,
            verify=False
        )
        
        # Then
        assert response.status_code in [200, 201]
```

## Output
Provide ONLY the complete Python code, no explanations.
The code should be ready to run with pytest.
"""

    @staticmethod
    def review_code_prompt(code: str) -> str:
        """Generate prompt for reviewing generated API test code.
        
        Args:
            code: Generated Python test code
            
        Returns:
            Formatted prompt
        """
        return f"""
Review the following API test code for quality and correctness.

## Code to Review
```python
{code}
```

## Review Checklist
1. **Imports**: Are pytest, requests, json, urllib3 present?
2. **Syntax**: Is the code syntactically correct Python?
3. **SSL Handling**: Is verify=False used and warnings suppressed?
4. **Authentication**: Is OAuth2 token flow implemented correctly?
5. **Assertions**: Are assert statements used properly?
6. **Headers**: Is Authorization Bearer token included?
7. **Documentation**: Are docstrings adequate?
8. **Style**: Does it follow PEP 8?

## Instructions
- If the code is good, return it as-is
- If there are issues, fix them and return the corrected code
- Add any missing imports
- Fix any syntax errors
- Ensure SSL handling is proper

## Output
Return ONLY the complete reviewed/fixed Python code.
No JSON wrapper, no markdown, just the code.
"""

    @staticmethod
    def github_pr_prompt(
        files: list[str],
        feature_name: str,
        scenarios_count: int
    ) -> str:
        """Generate prompt for creating PR description.
        
        Args:
            files: List of generated files
            feature_name: Name of the feature
            scenarios_count: Number of test scenarios
            
        Returns:
            Formatted prompt
        """
        files_str = "\n".join(f"- {f}" for f in files)
        
        return f"""
Create a Pull Request for the following auto-generated API test files.

## Generated Files
{files_str}

## Context
- Feature: {feature_name}
- Number of scenarios: {scenarios_count}

## Instructions
1. Create a descriptive branch name
2. Commit the files with a meaningful message
3. Create a PR with:
   - Clear title describing what API tests were added
   - Body explaining the generated tests
   - Instructions on how to run the tests with pytest

## Output
Provide the branch name and PR details:
```json
{{
  "branch_name": "test/...",
  "commit_message": "...",
  "pr_title": "...",
  "pr_body": "..."
}}
```
"""
