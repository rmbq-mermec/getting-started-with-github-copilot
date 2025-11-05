"""
Tests for FastAPI Activity Management System
"""
import sys
import os
from fastapi.testclient import TestClient
import pytest

# Add src to Python path for importing app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from app import app

# Create test client
client = TestClient(app)

def test_get_activities():
    """Test GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_for_activity():
    """Test POST /activities/{name}/signup adds participant"""
    activity_name = "Chess Club"
    test_email = "test.user@mergington.edu"
    
    # Get initial participants
    response = client.get("/activities")
    initial_participants = response.json()[activity_name]["participants"]
    
    # Try to signup
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert test_email in response.json()["message"]
    
    # Verify participant was added
    response = client.get("/activities")
    updated_participants = response.json()[activity_name]["participants"]
    assert len(updated_participants) == len(initial_participants) + 1
    assert test_email in updated_participants

def test_signup_duplicate_fails():
    """Test signing up same participant twice fails"""
    activity_name = "Programming Class"
    test_email = "duplicate.test@mergington.edu"
    
    # First signup should succeed
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_unregister_from_activity():
    """Test DELETE /activities/{name}/participants removes participant"""
    activity_name = "Chess Club"
    test_email = "remove.test@mergington.edu"
    
    # First sign up the test participant
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )
    
    # Now try to remove them
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": test_email}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert test_email in response.json()["message"]
    
    # Verify participant was removed
    response = client.get("/activities")
    current_participants = response.json()[activity_name]["participants"]
    assert test_email not in current_participants

def test_unregister_nonexistent_fails():
    """Test removing non-registered participant fails"""
    activity_name = "Chess Club"
    test_email = "nonexistent@mergington.edu"
    
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": test_email}
    )
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()

def test_invalid_activity_name():
    """Test operations with invalid activity name fail"""
    fake_activity = "Fake Activity Club"
    test_email = "test@mergington.edu"
    
    # Try to signup
    response = client.post(
        f"/activities/{fake_activity}/signup",
        params={"email": test_email}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    # Try to unregister
    response = client.delete(
        f"/activities/{fake_activity}/participants",
        params={"email": test_email}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()