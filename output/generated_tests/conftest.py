"""Pytest configuration and fixtures for API tests.

This file provides common fixtures for API testing.
"""

import pytest
import requests
from requests.auth import HTTPBasicAuth
from typing import Generator
import os


# API Configuration
API_BASE_URL = os.getenv(
    "API_BASE_URL", 
    "https://uapautomation-uap.cyberark-everest-pre-prod.cloud/api"
)
API_USERNAME = os.getenv("API_USERNAME", "adi_moldavski_1@cyberark.cloud.296894")
API_PASSWORD = os.getenv("API_PASSWORD", "Cyber123")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Fixture for the API base URL."""
    return API_BASE_URL


@pytest.fixture(scope="session")
def api_credentials() -> tuple:
    """Fixture for API credentials."""
    return (API_USERNAME, API_PASSWORD)


@pytest.fixture(scope="session")
def api_auth() -> HTTPBasicAuth:
    """Fixture for HTTP Basic Auth."""
    return HTTPBasicAuth(API_USERNAME, API_PASSWORD)


@pytest.fixture(scope="function")
def api_session(api_auth) -> Generator[requests.Session, None, None]:
    """Fixture for API session with authentication.
    
    Yields:
        Configured requests session
    """
    session = requests.Session()
    session.auth = api_auth
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    
    yield session
    
    session.close()


@pytest.fixture
def base_policy_payload() -> dict:
    """Fixture for base policy payload.
    
    Returns:
        Base policy payload dictionary
    """
    return {
        "metadata": {
            "policyId": None,
            "name": "test",
            "description": "test",
            "status": {
                "status": "Active",
                "statusCode": None,
                "statusDescription": None
            },
            "timeFrame": {
                "fromTime": None,
                "toTime": None
            },
            "policyEntitlement": {
                "targetCategory": "Cloud console",
                "locationType": "Azure",
                "policyType": "Recurring"
            },
            "policyTags": ["test"],
            "timeZone": "Asia/Calcutta"
        },
        "conditions": {
            "accessWindow": {
                "timeZone": "Asia/Calcutta",
                "daysOfTheWeek": [0, 1, 2, 3, 4, 5, 6]
            },
            "maxSessionDuration": 1
        },
        "targets": {
            "targets": [
                {
                    "roleId": "/providers/Microsoft.Authorization/roleDefinitions/c2f4ef07-c644-48eb-af81-4b1b4947fb11",
                    "workspaceId": "providers/Microsoft.Management/managementGroups/c5a5de91-6a2f-467e-aefa-b3f62876ec6a",
                    "roleName": "AcrDelete",
                    "workspaceName": "Tenant Root Group",
                    "description": "acr delete",
                    "orgId": "c5a5de91-6a2f-467e-aefa-b3f62876ec6a",
                    "workspaceType": "management_group",
                    "roleType": 0
                }
            ]
        },
        "principals": [
            {
                "id": "c2c7bcc6-9560-44e0-8dff-5be221cd37ee",
                "name": "adi_moldavski@cyberark.cloud.296894",
                "displayName": "adi_moldavski",
                "sourceDirectoryName": "CyberArk Cloud Directory",
                "sourceDirectoryId": "09B9A9B0-6CE8-465F-AB03-65766D33B05E",
                "type": "USER",
                "role": 1
            }
        ],
        "delegation_classification": "Unrestricted"
    }


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "positive: mark test as positive test case")
    config.addinivalue_line("markers", "negative: mark test as negative test case")
    config.addinivalue_line("markers", "boundary: mark test as boundary test case")
    config.addinivalue_line("markers", "validation: mark test as validation test case")
    config.addinivalue_line("markers", "type_validation: mark test as type validation test case")
    config.addinivalue_line("markers", "edge_case: mark test as edge case test")
