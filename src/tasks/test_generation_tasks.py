"""Task definitions for the test generation workflow."""

from crewai import Task, Agent

from src.utils.prompt_templates import PromptTemplates


def create_parse_task(
    agent: Agent,
    scenario_text: str
) -> Task:
    """Create a task for parsing test scenarios.
    
    Args:
        agent: The Parser Agent
        scenario_text: Raw scenario text to parse
        
    Returns:
        Configured Task
    """
    return Task(
        description=f"""
Parse the following test scenario and extract structured information.

## Scenario
{scenario_text}

## Your Task
1. Identify the input format (Gherkin, plain English, or user story)
2. Extract the feature name and scenario name
3. Break down into individual test steps
4. For each step, identify:
   - Step type (Given/When/Then/And)
   - Description of the step
   - Action to perform (navigate, click, fill, etc.)
   - Target element or URL
   - Value to input or verify

## Output
Provide a structured JSON response with:
- feature_name: Name of the feature being tested
- scenario_name: Name of the specific scenario
- steps: Array of step objects with step_type, description, action, target, value
""",
        expected_output="""A JSON object containing:
{
  "feature_name": "string",
  "scenario_name": "string", 
  "steps": [
    {
      "step_type": "given|when|then|and",
      "description": "step description",
      "action": "navigate|click|fill|verify|etc",
      "target": "element or URL",
      "value": "optional value"
    }
  ]
}""",
        agent=agent,
    )


def create_analyze_task(
    agent: Agent,
    context: list[Task]
) -> Task:
    """Create a task for analyzing parsed scenarios.
    
    Args:
        agent: The Analyzer Agent
        context: Previous tasks to use as context
        
    Returns:
        Configured Task
    """
    return Task(
        description="""
Analyze the parsed test scenario and create a detailed test blueprint.

## Your Task
Using the parsed scenario from the previous step:

1. Convert each step into specific Playwright actions
2. Determine appropriate selectors for UI elements
3. Map test steps to Playwright assertions
4. Identify page elements for potential page objects

## Selector Strategy (in order of preference)
1. data-testid: `[data-testid="element-name"]`
2. Role-based: `role=button[name="Submit"]`
3. Text-based: `text=Login`
4. CSS: `.class-name` or `#element-id`

## Action Mapping
- "navigate" → page.goto()
- "click" → page.click()
- "fill"/"enter"/"type" → page.fill()
- "select" → page.select_option()
- "verify visible" → expect(locator).to_be_visible()
- "verify text" → expect(locator).to_contain_text()
- "verify URL" → expect(page).to_have_url()

## Output
Provide a test blueprint with:
- class_name: PascalCase test class name
- method_name: snake_case test method name
- docstring: Description of what the test verifies
- actions: List of Playwright actions with element selectors
- assertions: List of assertions with expected values
- page_elements: Elements to include in page object
""",
        expected_output="""A JSON test blueprint containing:
{
  "class_name": "TestFeatureName",
  "method_name": "test_scenario_name",
  "docstring": "Verify that...",
  "actions": [
    {
      "action_type": "navigate|click|fill",
      "element": {"name": "...", "selector": "..."},
      "value": "optional"
    }
  ],
  "assertions": [
    {
      "assertion_type": "visible|text_contains|url_equals",
      "element": {"selector": "..."},
      "expected_value": "..."
    }
  ],
  "page_elements": [
    {"name": "...", "selector": "...", "description": "..."}
  ]
}""",
        agent=agent,
        context=context,
    )


def create_generate_task(
    agent: Agent,
    context: list[Task]
) -> Task:
    """Create a task for generating Playwright test code.
    
    Args:
        agent: The Generator Agent
        context: Previous tasks to use as context
        
    Returns:
        Configured Task
    """
    return Task(
        description="""
Generate a complete Playwright Python test file from the test blueprint.

## Your Task
Using the test blueprint from the previous step, generate:

1. A complete, runnable Python test file
2. All necessary imports (pytest, playwright)
3. A test class with proper naming
4. Test method(s) with docstrings
5. Given/When/Then comments to organize the code
6. Proper use of Playwright's expect() API

## Code Structure
```python
\"\"\"Test module for [Feature Name].\"\"\"

import pytest
from playwright.sync_api import Page, expect


class TestClassName:
    \"\"\"Test cases for [Feature Name].\"\"\"
    
    def test_method_name(self, page: Page):
        \"\"\"[Docstring describing what this test verifies]\"\"\"
        # Given - Setup/Preconditions
        page.goto("/path")
        
        # When - Actions
        page.fill("[data-testid='input']", "value")
        page.click("[data-testid='button']")
        
        # Then - Assertions
        expect(page).to_have_url("/expected")
        expect(page.locator(".message")).to_contain_text("Success")
```

## Requirements
- Use type hints (page: Page)
- Use expect() for assertions, not assert
- Use clear, descriptive variable names
- Follow PEP 8 style guidelines
- Make the code ready to run with pytest

## Output
Provide ONLY the complete Python code. No explanations or markdown.
""",
        expected_output="""Complete Python test code that:
- Has all necessary imports
- Contains a properly named test class
- Has test methods with docstrings
- Uses Playwright's expect() API
- Is properly formatted and ready to run""",
        agent=agent,
        context=context,
    )


def create_review_task(
    agent: Agent,
    context: list[Task]
) -> Task:
    """Create a task for reviewing generated test code.
    
    Args:
        agent: The Reviewer Agent
        context: Previous tasks to use as context
        
    Returns:
        Configured Task
    """
    return Task(
        description="""
Review the generated Playwright test code for quality and correctness.

## Your Task
1. Check that all imports are present and correct
2. Verify the code is syntactically correct
3. Ensure Playwright best practices are followed
4. Check that expect() assertions are used properly
5. Verify selectors are well-formed
6. Check for proper documentation

## Review Checklist
- [ ] `import pytest` present
- [ ] `from playwright.sync_api import Page, expect` present
- [ ] Class name starts with "Test"
- [ ] Method names start with "test_"
- [ ] `page: Page` type hint on test methods
- [ ] `expect()` used instead of `assert`
- [ ] Selectors are valid Playwright selectors
- [ ] Docstrings are present and descriptive
- [ ] Code follows PEP 8

## If Issues Found
- Fix any syntax errors
- Add missing imports
- Correct selector format
- Add missing type hints
- Improve documentation

## Output
Provide a JSON response with:
- is_valid: Whether the original code passed review
- review_notes: List of observations
- improvements_made: List of changes made
- final_code: The complete, corrected code (or original if no changes needed)
""",
        expected_output="""{
  "is_valid": true|false,
  "review_notes": ["observation 1", "observation 2"],
  "improvements_made": ["change 1", "change 2"],
  "final_code": "complete Python test code"
}""",
        agent=agent,
        context=context,
    )


def create_github_task(
    agent: Agent,
    files: list[str],
    feature_name: str,
    base_branch: str = "main"
) -> Task:
    """Create a task for pushing to GitHub and creating a PR.
    
    Args:
        agent: The GitHub Agent
        files: List of generated file paths
        feature_name: Name of the feature for the PR
        base_branch: Target branch for the PR
        
    Returns:
        Configured Task
    """
    files_str = ", ".join(files)
    
    return Task(
        description=f"""
Push the generated test files to GitHub and create a Pull Request.

## Files to Commit
{files_str}

## Feature Name
{feature_name}

## Target Branch
{base_branch}

## Your Task
1. Check the current Git status
2. Create a new branch with a descriptive name
3. Stage and commit the generated test files
4. Push the branch to origin
5. Create a Pull Request

## Branch Naming
Use format: test/auto-generated-[feature]-[timestamp]

## Commit Message
Use format: "Add auto-generated tests for [feature]"

## PR Details
- Title: "[Auto-Generated] Add tests for [feature]"
- Body: Include summary of tests, file list, and run instructions

## Output
Provide a summary of actions taken and the PR URL (if successful).
""",
        expected_output="""Summary of GitHub operations:
- Branch created: [branch name]
- Files committed: [count]
- Push status: success/failure
- PR URL: [url] or error message""",
        agent=agent,
    )

