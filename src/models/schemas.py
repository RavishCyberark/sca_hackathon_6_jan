"""Pydantic models for data validation and structured output."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Types of test steps."""
    
    GIVEN = "given"
    WHEN = "when"
    THEN = "then"
    AND = "and"
    BUT = "but"


class ActionType(str, Enum):
    """Types of actions that can be performed."""
    
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    HOVER = "hover"
    WAIT = "wait"
    SCROLL = "scroll"
    PRESS = "press"
    UPLOAD = "upload"
    CUSTOM = "custom"


class AssertionType(str, Enum):
    """Types of assertions."""
    
    VISIBLE = "visible"
    HIDDEN = "hidden"
    TEXT_CONTAINS = "text_contains"
    TEXT_EQUALS = "text_equals"
    URL_CONTAINS = "url_contains"
    URL_EQUALS = "url_equals"
    ELEMENT_EXISTS = "element_exists"
    ATTRIBUTE_EQUALS = "attribute_equals"
    ENABLED = "enabled"
    DISABLED = "disabled"
    CHECKED = "checked"
    UNCHECKED = "unchecked"


class TestStep(BaseModel):
    """Represents a single step in a test scenario."""
    
    step_type: StepType = Field(description="Type of step (Given/When/Then/And)")
    description: str = Field(description="Original text description of the step")
    action: Optional[str] = Field(default=None, description="Inferred action to perform")
    target: Optional[str] = Field(default=None, description="Target element or URL")
    value: Optional[str] = Field(default=None, description="Value to input or verify")
    
    class Config:
        use_enum_values = True


class ParsedScenario(BaseModel):
    """Represents a parsed test scenario."""
    
    feature_name: str = Field(description="Name of the feature being tested")
    scenario_name: str = Field(description="Name of the specific scenario")
    description: Optional[str] = Field(default=None, description="Optional description")
    steps: list[TestStep] = Field(default_factory=list, description="List of test steps")
    tags: list[str] = Field(default_factory=list, description="Tags/labels for the scenario")
    
    def to_test_name(self) -> str:
        """Convert scenario name to a valid test method name."""
        # Convert to snake_case
        name = self.scenario_name.lower()
        name = name.replace(" ", "_")
        name = "".join(c if c.isalnum() or c == "_" else "" for c in name)
        return f"test_{name}"
    
    def to_class_name(self) -> str:
        """Convert feature name to a valid test class name."""
        # Convert to PascalCase
        words = self.feature_name.split()
        name = "".join(word.capitalize() for word in words)
        name = "".join(c if c.isalnum() else "" for c in name)
        return f"Test{name}"


class TestElement(BaseModel):
    """Represents a UI element identified for testing."""
    
    name: str = Field(description="Descriptive name of the element")
    selector: str = Field(description="Playwright selector for the element")
    selector_type: str = Field(
        default="css",
        description="Type of selector (css, xpath, text, role, testid)"
    )
    description: Optional[str] = Field(
        default=None,
        description="What this element is used for"
    )


class TestAction(BaseModel):
    """Represents an action to be performed in a test."""
    
    action_type: ActionType = Field(description="Type of action")
    element: Optional[TestElement] = Field(
        default=None,
        description="Element to interact with"
    )
    value: Optional[str] = Field(default=None, description="Value for the action")
    wait_after: int = Field(
        default=0,
        description="Milliseconds to wait after action"
    )
    
    class Config:
        use_enum_values = True


class TestAssertion(BaseModel):
    """Represents an assertion to verify."""
    
    assertion_type: AssertionType = Field(description="Type of assertion")
    element: Optional[TestElement] = Field(
        default=None,
        description="Element to assert on"
    )
    expected_value: Optional[str] = Field(
        default=None,
        description="Expected value for the assertion"
    )
    message: Optional[str] = Field(
        default=None,
        description="Custom error message if assertion fails"
    )
    
    class Config:
        use_enum_values = True


class TestBlueprint(BaseModel):
    """Blueprint for generating a test case."""
    
    class_name: str = Field(description="Test class name")
    method_name: str = Field(description="Test method name")
    docstring: str = Field(description="Test method docstring")
    
    # Setup
    base_url: Optional[str] = Field(default=None, description="Base URL for the test")
    setup_actions: list[TestAction] = Field(
        default_factory=list,
        description="Actions to perform before test"
    )
    
    # Main test flow
    actions: list[TestAction] = Field(
        default_factory=list,
        description="Main test actions"
    )
    assertions: list[TestAssertion] = Field(
        default_factory=list,
        description="Assertions to verify"
    )
    
    # Teardown
    teardown_actions: list[TestAction] = Field(
        default_factory=list,
        description="Cleanup actions"
    )
    
    # Page objects
    page_elements: list[TestElement] = Field(
        default_factory=list,
        description="Elements to include in page object"
    )


class GeneratedTest(BaseModel):
    """Represents a generated test file."""
    
    filename: str = Field(description="Name of the test file")
    content: str = Field(description="Generated test code")
    test_count: int = Field(default=1, description="Number of tests in the file")
    
    # Optional page object
    page_object_filename: Optional[str] = Field(
        default=None,
        description="Name of the page object file"
    )
    page_object_content: Optional[str] = Field(
        default=None,
        description="Generated page object code"
    )
    
    # Validation status
    is_valid: bool = Field(default=True, description="Whether the code passed review")
    review_notes: list[str] = Field(
        default_factory=list,
        description="Notes from the code review"
    )


class PRMetadata(BaseModel):
    """Metadata for a GitHub Pull Request."""
    
    branch_name: str = Field(description="Name of the feature branch")
    title: str = Field(description="PR title")
    body: str = Field(description="PR description/body")
    base_branch: str = Field(default="main", description="Target branch for the PR")
    
    # Files included
    files: list[str] = Field(default_factory=list, description="Files included in the PR")
    
    # Result
    pr_url: Optional[str] = Field(default=None, description="URL of the created PR")
    pr_number: Optional[int] = Field(default=None, description="PR number")
    
    # Status
    success: bool = Field(default=False, description="Whether PR creation succeeded")
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if PR creation failed"
    )


class WorkflowResult(BaseModel):
    """Result of the complete test generation workflow."""
    
    # Input info
    input_file: str = Field(description="Path to input scenario file")
    scenarios_count: int = Field(description="Number of scenarios processed")
    
    # Generated output
    generated_tests: list[GeneratedTest] = Field(
        default_factory=list,
        description="List of generated test files"
    )
    
    # GitHub PR (optional)
    pr_metadata: Optional[PRMetadata] = Field(
        default=None,
        description="PR information if --push-pr was used"
    )
    
    # Status
    success: bool = Field(default=True, description="Whether the workflow succeeded")
    errors: list[str] = Field(
        default_factory=list,
        description="Any errors encountered"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Any warnings"
    )

