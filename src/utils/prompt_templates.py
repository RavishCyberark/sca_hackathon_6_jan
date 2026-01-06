"""Reusable prompt templates for agents."""


class PromptTemplates:
    """Collection of prompt templates for agent tasks."""
    
    @staticmethod
    def parse_scenario_prompt(scenario_text: str) -> str:
        """Generate prompt for parsing a test scenario.
        
        Args:
            scenario_text: Raw scenario text
            
        Returns:
            Formatted prompt
        """
        return f"""
Parse the following test scenario and extract structured information.

## Input Scenario
```
{scenario_text}
```

## Instructions
1. Identify the format (Gherkin, plain English, or user story)
2. Extract the feature name and scenario name
3. Break down into individual steps
4. For each step, identify:
   - Step type (Given/When/Then/And)
   - The action being described
   - Any target element or URL
   - Any value being entered or verified

## Output Format
Provide the parsed scenario as a JSON object with this structure:
```json
{{
  "feature_name": "string",
  "scenario_name": "string",
  "steps": [
    {{
      "step_type": "given|when|then|and",
      "description": "original step text",
      "action": "navigate|click|fill|select|verify|etc",
      "target": "element or URL",
      "value": "value if applicable"
    }}
  ]
}}
```
"""

    @staticmethod
    def analyze_test_prompt(parsed_scenario: str) -> str:
        """Generate prompt for analyzing a parsed scenario.
        
        Args:
            parsed_scenario: JSON string of parsed scenario
            
        Returns:
            Formatted prompt
        """
        return f"""
Analyze the following parsed test scenario and create a test blueprint.

## Parsed Scenario
```json
{parsed_scenario}
```

## Instructions
1. For each step, determine the appropriate Playwright action or assertion
2. Suggest realistic selectors for UI elements (prefer data-testid)
3. Map actions to Playwright methods
4. Map assertions to Playwright expect() calls

## Selector Strategy
- Prefer: `[data-testid="element-name"]`
- Alternative: `role=button[name="Submit"]`
- Fallback: `.class-name` or `#element-id`

## Output Format
Provide a test blueprint as JSON:
```json
{{
  "class_name": "TestClassName",
  "method_name": "test_method_name",
  "docstring": "Test description",
  "actions": [
    {{
      "action_type": "navigate|click|fill|etc",
      "element": {{
        "name": "element_name",
        "selector": "[data-testid='...']"
      }},
      "value": "value if needed"
    }}
  ],
  "assertions": [
    {{
      "assertion_type": "visible|text_contains|url_equals|etc",
      "element": {{ "selector": "..." }},
      "expected_value": "..."
    }}
  ],
  "page_elements": [
    {{
      "name": "element_name",
      "selector": "[data-testid='...']",
      "description": "what this element is"
    }}
  ]
}}
```
"""

    @staticmethod
    def generate_test_prompt(blueprint: str) -> str:
        """Generate prompt for creating Playwright test code.
        
        Args:
            blueprint: JSON string of test blueprint
            
        Returns:
            Formatted prompt
        """
        return f"""
Generate a complete Playwright Python test file from the following blueprint.

## Test Blueprint
```json
{blueprint}
```

## Requirements
1. Use pytest with Playwright
2. Include all necessary imports
3. Create a test class with the specified name
4. Implement the test method with proper docstring
5. Add Given/When/Then comments to organize the code
6. Use Playwright's expect() for all assertions
7. Follow PEP 8 style guidelines

## Template Structure
```python
\"\"\"Test module for [Feature].\"\"\"

import pytest
from playwright.sync_api import Page, expect


class TestClassName:
    \"\"\"Test cases for [Feature].\"\"\"
    
    def test_method_name(self, page: Page):
        \"\"\"[Docstring from blueprint]\"\"\"
        # Given - Setup
        ...
        
        # When - Actions
        ...
        
        # Then - Assertions
        ...
```

## Output
Provide ONLY the complete Python code, no explanations.
The code should be ready to run with pytest.
"""

    @staticmethod
    def review_code_prompt(code: str) -> str:
        """Generate prompt for reviewing generated test code.
        
        Args:
            code: Generated Python test code
            
        Returns:
            Formatted prompt
        """
        return f"""
Review the following Playwright test code for quality and correctness.

## Code to Review
```python
{code}
```

## Review Checklist
1. **Imports**: Are all necessary imports present?
2. **Syntax**: Is the code syntactically correct?
3. **Best Practices**: Does it follow Playwright best practices?
4. **Assertions**: Are expect() assertions used correctly?
5. **Selectors**: Are selectors properly formatted?
6. **Documentation**: Are docstrings and comments adequate?
7. **Style**: Does it follow PEP 8?

## Instructions
- If the code is good, return it as-is with is_valid=true
- If there are issues, fix them and return the corrected code
- Add any missing imports
- Fix any syntax errors
- Improve selectors if needed

## Output Format
```json
{{
  "is_valid": true|false,
  "review_notes": ["note1", "note2"],
  "improvements_made": ["improvement1", "improvement2"],
  "final_code": "the complete reviewed/fixed code"
}}
```
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
Create a Pull Request for the following auto-generated test files.

## Generated Files
{files_str}

## Context
- Feature: {feature_name}
- Number of scenarios: {scenarios_count}

## Instructions
1. Create a descriptive branch name
2. Commit the files with a meaningful message
3. Create a PR with:
   - Clear title describing what tests were added
   - Body explaining the generated tests
   - Instructions on how to run the tests

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

