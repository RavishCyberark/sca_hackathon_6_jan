"""Parser Agent - Interprets and normalizes API test scenarios."""

from crewai import Agent, LLM

from src.config.settings import get_settings


def create_parser_agent() -> Agent:
    """Create the Parser Agent that interprets API test scenarios.
    
    This agent is responsible for:
    - Parsing Gherkin/BDD format API scenarios
    - Interpreting plain English API test descriptions
    - Processing user stories with API acceptance criteria
    - Extracting API endpoint, method, headers, and payload information
    - Normalizing all formats into structured API test steps
    """
    settings = get_settings()
    
    llm = LLM(
        model=settings.ollama.get_model_string(),
        base_url=settings.ollama.base_url,
        temperature=settings.ollama.temperature,
    )
    
    return Agent(
        role="API Test Scenario Parser",
        goal="""Parse and normalize API test scenarios from various formats 
        (Gherkin, plain English, user stories) into a structured format 
        with clearly defined API endpoints, HTTP methods, request payloads, 
        headers, authentication requirements, and expected responses.""",
        backstory="""You are an expert in API testing and Behavior-Driven 
        Development (BDD). You have years of experience reading and writing 
        API test specifications including REST API documentation, OpenAPI/Swagger 
        specs, and test scenarios. You excel at extracting essential API test 
        details like endpoints, HTTP methods (GET, POST, PUT, DELETE), request 
        bodies, headers, authentication flows (OAuth2, Basic Auth, API Keys), 
        and expected response codes and payloads. You understand both positive 
        and negative test cases for API validation.""",
        llm=llm,
        verbose=settings.verbose,
        allow_delegation=False,
        memory=True,
    )


# Parsing guidelines for the agent
PARSER_GUIDELINES = """
## Input Format Detection

Detect and handle these formats for API testing:

### 1. Gherkin/BDD Format for API
```
Feature: Create Policy API
  Scenario: Successfully create policy
    Given the user obtains OAuth2 token
    And the API endpoint is "/policies"
    When the user sends a POST request with valid payload
    Then the response status code should be 200 or 201
```

### 2. Plain English Format for API
```
Test the Create Policy API:
1. Authenticate using OAuth2 token
2. Send POST request to /policies endpoint
3. Include valid JSON payload
4. Verify response is 200/201
5. Verify response contains policy ID
```

### 3. API Test Specification Format
```
API: POST /policies
Auth: OAuth2 Bearer Token
Payload: { "name": "test", "description": "test policy" }
Expected: 201 Created
Validation: Response contains policyId
```

## Output Structure

For each API scenario, extract:
1. Feature/API Name
2. Test Scenario Name
3. API Details:
   - HTTP Method (GET, POST, PUT, DELETE, PATCH)
   - Endpoint URL
   - Authentication type and credentials
   - Request headers
   - Request payload/body
4. Expected Response:
   - Status code(s)
   - Response body validation
   - Error messages for negative cases

## Example Output

```json
{
  "feature_name": "Create Policy API",
  "scenario_name": "Successfully create policy with valid description",
  "api_details": {
    "method": "POST",
    "endpoint": "/policies",
    "auth_type": "oauth2",
    "content_type": "application/json"
  },
  "steps": [
    {
      "step_type": "given",
      "description": "obtain OAuth2 token",
      "action": "authenticate"
    },
    {
      "step_type": "when",
      "description": "send POST request with valid payload",
      "action": "api_call",
      "method": "POST",
      "endpoint": "/policies"
    },
    {
      "step_type": "then",
      "description": "response status is 200 or 201",
      "action": "assert_status",
      "expected": [200, 201]
    }
  ]
}
```
"""
