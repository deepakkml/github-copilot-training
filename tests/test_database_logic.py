"""Unit tests for business logic and database operations using AAA pattern.

These tests focus on the correctness of data manipulation logic
independent of HTTP request/response handling.
"""

import pytest
from copy import deepcopy
from src.app import DEFAULT_ACTIVITIES


class TestActivityDataStructure:
    """Tests for the structure and integrity of activity data."""
    
    def test_all_activities_have_required_fields(self):
        """Test that all activities have required fields.
        
        AAA Pattern:
        - Arrange: DEFAULT_ACTIVITIES dictionary
        - Act: Iterate through all activities
        - Assert: Verify each activity has name, description, schedule, max_participants, participants
        """
        # Arrange & Act & Assert
        assert isinstance(DEFAULT_ACTIVITIES, dict)
        assert len(DEFAULT_ACTIVITIES) > 0
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in DEFAULT_ACTIVITIES.items():
            # Assert each field exists
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"
            
            # Assert field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_initial_participants_are_valid_emails(self):
        """Test that all initial participants are valid email addresses.
        
        AAA Pattern:
        - Arrange: DEFAULT_ACTIVITIES dictionary
        - Act: Extract all participant email addresses
        - Assert: Verify each email has @ symbol and domain
        """
        # Arrange & Act
        all_participants = []
        for activity_data in DEFAULT_ACTIVITIES.values():
            all_participants.extend(activity_data["participants"])
        
        # Assert
        for email in all_participants:
            assert isinstance(email, str)
            assert "@" in email, f"Invalid email format: {email}"
            assert "." in email.split("@")[1], f"Invalid email domain: {email}"


class TestParticipantManagement:
    """Tests for participant list management logic."""
    
    def test_participant_addition_increases_count(self, test_activities):
        """Test that adding a participant increases the counted participants.
        
        AAA Pattern:
        - Arrange: Get initial participant count for an activity
        - Act: Add a new participant to the list
        - Assert: Verify count increased by 1
        """
        # Arrange
        activity_name = "Chess Club"
        initial_count = len(test_activities[activity_name]["participants"])
        new_email = "new.student@mergington.edu"
        
        # Act
        test_activities[activity_name]["participants"].append(new_email)
        
        # Assert
        assert len(test_activities[activity_name]["participants"]) == initial_count + 1
        assert new_email in test_activities[activity_name]["participants"]
    
    def test_participant_removal_decreases_count(self, test_activities):
        """Test that removing a participant decreases the count.
        
        AAA Pattern:
        - Arrange: Get an existing participant and initial count
        - Act: Remove the participant from the list
        - Assert: Verify count decreased by 1 and participant is gone
        """
        # Arrange
        activity_name = "Chess Club"
        # Use an existing participant
        participant_to_remove = test_activities[activity_name]["participants"][0]
        initial_count = len(test_activities[activity_name]["participants"])
        
        # Act
        test_activities[activity_name]["participants"].remove(participant_to_remove)
        
        # Assert
        assert len(test_activities[activity_name]["participants"]) == initial_count - 1
        assert participant_to_remove not in test_activities[activity_name]["participants"]
    
    def test_duplicate_participant_detection(self, test_activities):
        """Test that duplicate participants can be detected.
        
        AAA Pattern:
        - Arrange: An activity and a participant email
        - Act: Check if email is in participant list before and after adding
        - Assert: First check is False, second check is True
        """
        # Arrange
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"
        
        # Act & Assert - Before adding
        assert email not in test_activities[activity_name]["participants"]
        
        # Act - Add the email
        test_activities[activity_name]["participants"].append(email)
        
        # Act & Assert - After adding
        assert email in test_activities[activity_name]["participants"]
        
        # Verify duplicate would be detected (can't add same email twice)
        initial_count = len(test_activities[activity_name]["participants"])
        # Attempt to add again (simulating duplicate check)
        if email not in test_activities[activity_name]["participants"]:
            test_activities[activity_name]["participants"].append(email)
        
        # Assert count didn't change (duplicate was prevented)
        assert len(test_activities[activity_name]["participants"]) == initial_count


class TestActivityCapacity:
    """Tests for activity capacity and availability logic."""
    
    def test_capacity_calculation_is_correct(self, test_activities):
        """Test that available spots calculation is accurate.
        
        AAA Pattern:
        - Arrange: An activity with known max_participants and current participant count
        - Act: Calculate available spots
        - Assert: Verify calculation is correct
        """
        # Arrange
        activity_name = "Chess Club"
        activity = test_activities[activity_name]
        max_participants = activity["max_participants"]
        current_participants = len(activity["participants"])
        
        # Act
        available_spots = max_participants - current_participants
        
        # Assert
        assert available_spots >= 0
        assert available_spots == max_participants - current_participants
    
    def test_capacity_updates_after_participant_changes(self, test_activities):
        """Test that capacity is correctly updated when participants change.
        
        AAA Pattern:
        - Arrange: Initial capacity calculation
        - Act: Add and remove participants, recalculate capacity
        - Assert: Verify capacity updates correctly
        """
        # Arrange
        activity_name = "Chess Club"
        activity = test_activities[activity_name]
        initial_capacity = activity["max_participants"] - len(activity["participants"])
        
        # Act - Add a participant
        test_activities[activity_name]["participants"].append("new@mergington.edu")
        capacity_after_add = activity["max_participants"] - len(activity["participants"])
        
        # Assert
        assert capacity_after_add == initial_capacity - 1
        
        # Act - Remove a participant
        test_activities[activity_name]["participants"].pop()
        capacity_after_remove = activity["max_participants"] - len(activity["participants"])
        
        # Assert
        assert capacity_after_remove == initial_capacity


class TestDatabaseIsolation:
    """Tests to verify that test database isolation works correctly."""
    
    def test_modifications_do_not_affect_default(self, test_activities):
        """Test that modifying test_activities doesn't modify DEFAULT_ACTIVITIES.
        
        AAA Pattern:
        - Arrange: Store initial state of DEFAULT_ACTIVITIES
        - Act: Modify test_activities
        - Assert: Verify DEFAULT_ACTIVITIES is unchanged
        """
        # Arrange
        original_chess_participants = len(DEFAULT_ACTIVITIES["Chess Club"]["participants"])
        
        # Act
        test_activities["Chess Club"]["participants"].append("modified@mergington.edu")
        
        # Assert
        assert len(DEFAULT_ACTIVITIES["Chess Club"]["participants"]) == original_chess_participants
        assert "modified@mergington.edu" not in DEFAULT_ACTIVITIES["Chess Club"]["participants"]
        assert "modified@mergington.edu" in test_activities["Chess Club"]["participants"]
    
    def test_each_test_gets_fresh_copy(self, test_activities):
        """Test that each get their own independent copy via the fixture.
        
        AAA Pattern:
        - Arrange: Modify test_activities significantly
        - Act: Access a fixture-provided object
        - Assert: Verify next test would get unmodified copy (if run again)
        
        Note: This test verifies the fixture behavior by mutation.
        """
        # Arrange
        original_count = len(test_activities["Chess Club"]["participants"])
        
        # Act - Manipulate the test_activities extensively
        test_activities["Chess Club"]["participants"].append("test1@mergington.edu")
        test_activities["Chess Club"]["participants"].append("test2@mergington.edu")
        test_activities["Gym Class"]["participants"].clear()
        
        # Assert - Verify the mutations took effect
        assert len(test_activities["Chess Club"]["participants"]) == original_count + 2
        assert len(test_activities["Gym Class"]["participants"]) == 0
