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
    """Types of API actions that can be performed."""
    
    GET_TOKEN = "get_token"
    SEND_REQUEST = "send_request"
    VERIFY_STATUS = "verify_status"
    VERIFY_RESPONSE = "verify_response"
    MODIFY_PAYLOAD = "modify_payload"
    CUSTOM = "custom"


class HTTPMethod(str, Enum):
    """HTTP methods for API requests."""
    
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class AssertionType(str, Enum):
    """Types of API response assertions."""
    
    STATUS_CODE = "status_code"
    RESPONSE_CONTAINS = "response_contains"
    RESPONSE_EQUALS = "response_equals"
    FIELD_EXISTS = "field_exists"
    FIELD_VALUE = "field_value"
    HEADER_EXISTS = "header_exists"
    HEADER_VALUE = "header_value"
    RESPONSE_TIME = "response_time"


class TestStep(BaseModel):
    """Represents a single step in a test scenario."""
    
    step_type: StepType = Field(description="Type of step (Given/When/Then/And)")
    description: str = Field(description="Original text description of the step")
    action: Optional[str] = Field(default=None, description="Inferred action to perform")
    target: Optional[str] = Field(default=None, description="Target endpoint or field")
    value: Optional[str] = Field(default=None, description="Value to input or verify")
    
    class Config:
        use_enum_values = True


class ParsedScenario(BaseModel):
    """Represents a parsed API test scenario."""
    
    feature_name: str = Field(description="Name of the API feature being tested")
    scenario_name: str = Field(description="Name of the specific scenario")
    description: Optional[str] = Field(default=None, description="Optional description")
    steps: list[TestStep] = Field(default_factory=list, description="List of test steps")
    tags: list[str] = Field(default_factory=list, description="Tags/labels for the scenario")
    
    def to_test_name(self) -> str:
        """Convert scenario name to a valid test method name."""
        name = self.scenario_name.lower()
        name = name.replace(" ", "_")
        name = "".join(c if c.isalnum() or c == "_" else "" for c in name)
        return f"test_{name}"
    
    def to_class_name(self) -> str:
        """Convert feature name to a valid test class name."""
        words = self.feature_name.split()
        name = "".join(word.capitalize() for word in words)
        name = "".join(c if c.isalnum() else "" for c in name)
        return f"Test{name}"


class APIEndpoint(BaseModel):
    """Represents an API endpoint configuration."""
    
    url: str = Field(description="Full URL of the API endpoint")
    method: HTTPMethod = Field(default=HTTPMethod.POST, description="HTTP method")
    headers: dict = Field(default_factory=dict, description="Request headers")
    
    class Config:
        use_enum_values = True


class AuthConfig(BaseModel):
    """Authentication configuration for API tests."""
    
    token_url: str = Field(description="OAuth2 token endpoint URL")
    username: str = Field(description="Username or client ID")
    password: str = Field(description="Password or client secret")
    grant_type: str = Field(default="client_credentials", description="OAuth2 grant type")
    scope: str = Field(default="full", description="OAuth2 scope")


class TestAction(BaseModel):
    """Represents an API action to be performed in a test."""
    
    action_type: ActionType = Field(description="Type of API action")
    endpoint: Optional[APIEndpoint] = Field(default=None, description="API endpoint")
    payload: Optional[dict] = Field(default=None, description="Request payload")
    expected_status: Optional[int] = Field(default=None, description="Expected status code")
    
    class Config:
        use_enum_values = True


class TestAssertion(BaseModel):
    """Represents an API response assertion."""
    
    assertion_type: AssertionType = Field(description="Type of assertion")
    field_path: Optional[str] = Field(default=None, description="JSON path to field")
    expected_value: Optional[str] = Field(default=None, description="Expected value")
    message: Optional[str] = Field(default=None, description="Error message if fails")
    
    class Config:
        use_enum_values = True


class TestBlueprint(BaseModel):
    """Blueprint for generating an API test case."""
    
    class_name: str = Field(description="Test class name")
    method_name: str = Field(description="Test method name")
    docstring: str = Field(description="Test method docstring")
    test_type: str = Field(default="positive", description="positive or negative")
    
    # API Configuration
    base_url: str = Field(description="Base URL for the API")
    endpoint: str = Field(description="API endpoint path")
    http_method: HTTPMethod = Field(default=HTTPMethod.POST, description="HTTP method")
    
    # Authentication
    auth_config: Optional[AuthConfig] = Field(default=None, description="Auth config")
    
    # Request
    base_payload: dict = Field(default_factory=dict, description="Base request payload")
    payload_modifications: list[str] = Field(
        default_factory=list,
        description="Payload modifications for this test"
    )
    
    # Assertions
    expected_status: int = Field(default=200, description="Expected status code")
    assertions: list[TestAssertion] = Field(
        default_factory=list,
        description="Response assertions"
    )
    
    class Config:
        use_enum_values = True


class GeneratedTest(BaseModel):
    """Represents a generated API test file."""
    
    filename: str = Field(description="Name of the test file")
    content: str = Field(description="Generated test code")
    test_count: int = Field(default=1, description="Number of tests in the file")
    
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
