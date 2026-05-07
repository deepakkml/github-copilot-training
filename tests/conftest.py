"""Pytest configuration and shared fixtures for the test suite."""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import create_app, DEFAULT_ACTIVITIES


@pytest.fixture
def test_activities():
    """Provide a fresh copy of activities database for each test.
    
    This ensures test isolation - each test gets its own independent copy
    of the activities data with no pollution from other tests.
    
    Yields:
        A deep copy of the default activities dictionary.
    """
    # Arrange: Create a fresh copy of activities for this test
    return deepcopy(DEFAULT_ACTIVITIES)


@pytest.fixture
def client(test_activities):
    """Provide a TestClient with a custom activities database.
    
    This fixture combines the test_activities fixture to provide isolation
    and returns a TestClient that can be used to make requests to the app.
    
    Args:
        test_activities: Fresh activities database from test_activities fixture.
    
    Returns:
        A TestClient instance connected to an app with isolated test data.
    """
    # Arrange: Create app instance with test data
    app = create_app(activities=test_activities)
    
    # Return a test client for this app
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Provide a consistent test email for use in tests.
    
    Returns:
        A sample student email address.
    """
    return "test.student@mergington.edu"


@pytest.fixture
def sample_activity_name():
    """Provide a consistent test activity name that exists in default data.
    
    Returns:
        A valid activity name that exists in DEFAULT_ACTIVITIES.
    """
    return "Chess Club"
