"""Integration tests for FastAPI endpoints using AAA (Arrange-Act-Assert) pattern.

These tests verify the complete behavior of API endpoints end-to-end,
including request handling, validation, and response formatting.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities.
        
        AAA Pattern:
        - Arrange: Client is ready with test database
        - Act: Make GET request to /activities endpoint
        - Assert: Verify response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Verify at least one expected activity exists
        assert "Chess Club" in activities
        # Verify activity has required fields
        assert "description" in activities["Chess Club"]
        assert "schedule" in activities["Chess Club"]
        assert "max_participants" in activities["Chess Club"]
        assert "participants" in activities["Chess Club"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_activity_success(self, client, sample_activity_name, sample_email):
        """Test successful signup for an activity.
        
        AAA Pattern:
        - Arrange: Client, activity name, and email are prepared
        - Act: Make POST request to signup endpoint with valid data
        - Assert: Verify success response and participant is added
        """
        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert sample_activity_name in data["message"]
        
        # Verify participant was actually added
        activities = client.get("/activities").json()
        assert sample_email in activities[sample_activity_name]["participants"]
    
    def test_signup_duplicate_email_fails(self, client, sample_activity_name, sample_email):
        """Test that duplicate signup for same activity is rejected.
        
        AAA Pattern:
        - Arrange: Sign up a student once for an activity
        - Act: Attempt to sign up the same student again
        - Assert: Verify the second signup is rejected with appropriate error
        """
        # Arrange
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client, sample_email):
        """Test that signup for nonexistent activity returns 404.
        
        AAA Pattern:
        - Arrange: Prepare request with invalid activity name
        - Act: Make POST request to signup endpoint with nonexistent activity
        - Assert: Verify 404 Not Found response is returned
        """
        # Act
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_multiple_different_students_success(self, client, sample_activity_name):
        """Test that multiple different students can sign up for the same activity.
        
        AAA Pattern:
        - Arrange: Prepare multiple different email addresses
        - Act: Sign up each student for the activity sequentially
        - Assert: Verify all signups succeed and all are recorded
        """
        # Arrange
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        
        # Act & Assert
        for email in emails:
            response = client.post(
                f"/activities/{sample_activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all students are in participants list
        activities = client.get("/activities").json()
        participants = activities[sample_activity_name]["participants"]
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_from_activity_success(self, client, sample_activity_name, sample_email):
        """Test successful unregistration from an activity.
        
        AAA Pattern:
        - Arrange: Sign up a student for an activity
        - Act: Make DELETE request to unregister endpoint
        - Assert: Verify success response and participant is removed
        """
        # Arrange
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        
        # Verify participant was actually removed
        activities = client.get("/activities").json()
        assert sample_email not in activities[sample_activity_name]["participants"]
    
    def test_unregister_not_registered_fails(self, client, sample_activity_name, sample_email):
        """Test that unregistering a student who is not registered returns 400.
        
        AAA Pattern:
        - Arrange: A student who is not signed up for the activity
        - Act: Make DELETE request to unregister endpoint
        - Assert: Verify 400 Bad Request response is returned
        """
        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity_fails(self, client, sample_email):
        """Test that unregistering from nonexistent activity returns 404.
        
        AAA Pattern:
        - Arrange: Prepare request with invalid activity name
        - Act: Make DELETE request to unregister endpoint with nonexistent activity
        - Assert: Verify 404 Not Found response is returned
        """
        # Act
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": sample_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestIntegrationSignupAndUnregister:
    """Integration tests combining signup and unregister operations."""
    
    def test_signup_then_unregister_flow(self, client, sample_activity_name, sample_email):
        """Test complete flow: signup, verify, unregister, verify.
        
        AAA Pattern:
        - Arrange: Prepare client and email
        - Act: Sign up, check participant list, unregister, check participant list
        - Assert: Verify each state is correct
        """
        # Act & Assert - Step 1: Verify initial state (not registered)
        activities = client.get("/activities").json()
        initial_count = len(activities[sample_activity_name]["participants"])
        assert sample_email not in activities[sample_activity_name]["participants"]
        
        # Act & Assert - Step 2: Sign up
        signup_response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )
        assert signup_response.status_code == 200
        activities = client.get("/activities").json()
        assert sample_email in activities[sample_activity_name]["participants"]
        assert len(activities[sample_activity_name]["participants"]) == initial_count + 1
        
        # Act & Assert - Step 3: Unregister
        unregister_response = client.delete(
            f"/activities/{sample_activity_name}/unregister",
            params={"email": sample_email}
        )
        assert unregister_response.status_code == 200
        activities = client.get("/activities").json()
        assert sample_email not in activities[sample_activity_name]["participants"]
        assert len(activities[sample_activity_name]["participants"]) == initial_count
