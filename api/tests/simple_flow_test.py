import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

# Test data
user1_data = {
    "username": "Jack Casey",
    "email": "jackcasey614@gmail.com",
    "password": "TestPass",
    "legal_name": {
        "first_name": "Jack",
        "last_name": "Casey",
        "middle_name": "Bloom"
    },
    "date_of_birth": "2004-06-14",
    "address_line1": "Avoca",
    "city": "Dunboyne",
    "state": "Meath",
    "postal_code": "a86d586",
    "country": "IE",
    "phone_number": "+353858839191"
}

user2_data = {
    "username": "RyanMiller92",
    "email": "ryanmiller92@example.com",
    "password": "SecurePass123",
    "legal_name": {
        "first_name": "Ryan",
        "last_name": "Miller",
        "middle_name": "James"
    },
    "date_of_birth": "1992-11-25",
    "address_line1": "15 Oakwood Drive",
    "city": "Galway",
    "state": "Galway",
    "postal_code": "H91XY12",
    "country": "IE",
    "phone_number": "+353872345678"
}

def register_user(user_data):
    """Register a new user"""
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Register {user_data['username']}: {response.status_code}")
    return response.json() if response.status_code == 201 else None

def login_user(username, password):
    """Login and get access token"""
    data = {
        "username": username,  # FastAPI OAuth2 uses 'username' ... not 'email'
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/token", data=data)
    print(f"Login {username}: {response.status_code}")
    return response.json()["access_token"] if response.status_code == 200 else None

def add_real_card(token, user_data, card_number):
    """Add a real card for a user"""
    headers = {"Authorization": f"Bearer {token}"}
    card_data = {
        "card_number": card_number,
        "card_holder_name": f"{user_data['legal_name']['first_name']} {user_data['legal_name']['last_name']}",
        "expiry_date": "12/25",
        "cvc": "123"
    }
    response = requests.post(f"{BASE_URL}/real-cards/", json=card_data, headers=headers)
    print(f"Add real card for {user_data['username']}: {response.status_code}")
    return response.json() if response.status_code == 201 else None

def create_group(token, group_name):
    """Create a new group"""
    headers = {"Authorization": f"Bearer {token}"}
    group_data = {"name": group_name}
    response = requests.post(f"{BASE_URL}/groups/", json=group_data, headers=headers)
    print(f"Create group {group_name}: {response.status_code}")
    return response.json() if response.status_code == 201 else None

def join_group(token, group_id):
    """Join an existing group"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/groups/{group_id}/join", headers=headers)
    print(f"Join group {group_id}: {response.status_code}")
    return response.json() if response.status_code == 200 else None

def main():
    print("Starting test flow...")
    
    # Register users
    register_user(user1_data)
    register_user(user2_data)
    
    # # Login users
    user1_token = login_user(user1_data["username"], user1_data["password"])
    user2_token = login_user(user2_data["username"], user2_data["password"])
    
    if not user1_token or not user2_token:
        print("Failed to login users")
        return
    
    # Add real cards with unique numbers
    add_real_card(user1_token, user1_data, "4242424242424242")
    add_real_card(user2_token, user2_data, "4242424242424243")
    
    # Create group with first user
    group = create_group(user1_token, "Test Group")
    
    if not group:
        print("Failed to create group")
        return
    
    # Second user joins group
    join_result = join_group(user2_token, group["group_id"])
    if not join_result:
        print("Failed to join group")
        return
    
    print("Test flow completed successfully!")

if __name__ == "__main__":
    # Give the API server a moment to start up if needed
    # time.sleep(1)
    main()
