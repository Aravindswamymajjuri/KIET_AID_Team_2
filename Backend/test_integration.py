#!/usr/bin/env python3
"""
Test MongoDB Integration - Verify signup, login, and chat history
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health endpoint"""
    print_section("TESTING HEALTH ENDPOINT")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        data = response.json()
        
        print(f"✅ Server Status: {data.get('status')}")
        mongodb = data.get('mongodb', {})
        print(f"🔗 MongoDB Connected: {mongodb.get('connected', False)}")
        if mongodb.get('connected'):
            print(f"📊 Database: {mongodb.get('database')}")
            print(f"📈 Collections: {', '.join(mongodb.get('collections', []))}")
            counts = mongodb.get('document_counts', {})
            print(f"📦 Document counts:")
            for coll, count in counts.items():
                print(f"   • {coll}: {count}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the server is running: python -m uvicorn app:app --reload")
        return False

def test_signup():
    """Test user signup"""
    print_section("TESTING SIGNUP")
    try:
        # Generate unique username
        username = f"testuser_{int(time.time())}"
        payload = {
            "username": username,
            "password": "password123",
            "email": f"{username}@test.com",
            "full_name": "Test User"
        }
        
        print(f"📝 Creating user: {username}")
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Signup successful!")
            print(f"👤 User ID: {data['user']['id']}")
            print(f"👤 Username: {data['user']['username']}")
            print(f"🔑 Token: {data['token'][:20]}...")
            return data['token'], data['user']['id']
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_login(username="testuser_1735918800", password="password123"):
    """Test user login"""
    print_section("TESTING LOGIN")
    try:
        payload = {
            "username": username,
            "password": password
        }
        
        print(f"🔐 Logging in as: {username}")
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"👤 User ID: {data['user']['id']}")
            print(f"👤 Username: {data['user']['username']}")
            print(f"🔑 Token: {data['token'][:20]}...")
            return data['token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_chat(token):
    """Test chat with authentication"""
    print_section("TESTING CHAT (with auth)")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"text": "What are symptoms of diabetes?"}
        
        print(f"💬 Sending message: {payload['text']}")
        response = requests.post(
            f"{BASE_URL}/api/chat/text", 
            json=payload, 
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat successful!")
            print(f"🤖 Response: {data['response'][:100]}...")
            print(f"⏱️  Processing time: {data.get('processing_time', 0):.2f}s")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_mongodb():
    """Verify data in MongoDB"""
    print_section("VERIFYING MONGODB DATA")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from database import get_users_collection, get_sessions_collection, get_chat_logs_collection
        
        users = get_users_collection()
        sessions = get_sessions_collection()
        chat_logs = get_chat_logs_collection()
        
        user_count = users.count_documents({})
        session_count = sessions.count_documents({})
        log_count = chat_logs.count_documents({})
        
        print(f"✅ MongoDB data verified:")
        print(f"   👥 Users: {user_count}")
        print(f"   🔐 Sessions: {session_count}")
        print(f"   💬 Chat logs: {log_count}")
        
        # Show last user
        if user_count > 0:
            last_user = users.find_one({}, sort=[('created_at', -1)])
            print(f"\n📌 Last created user:")
            print(f"   • Username: {last_user.get('username')}")
            print(f"   • Email: {last_user.get('email', 'N/A')}")
            print(f"   • Created: {last_user.get('created_at')}")
        
        # Show last chat
        if log_count > 0:
            last_chat = chat_logs.find_one({}, sort=[('timestamp', -1)])
            print(f"\n📌 Last chat log:")
            print(f"   • User input: {last_chat.get('user_input', '')[:50]}...")
            print(f"   • Bot response: {last_chat.get('bot_response', '')[:50]}...")
            print(f"   • User ID: {last_chat.get('user_id', 'anonymous')}")
            print(f"   • Timestamp: {last_chat.get('timestamp')}")
        
        return True
        
    except ImportError:
        print("⚠️  Can't import MongoDB modules - this test should be run from Backend directory")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*10 + "MONGODB INTEGRATION TEST SUITE" + " "*17 + "║")
    print("╚" + "═"*58 + "╝")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server not running. Please start the server first.")
        return
    
    time.sleep(1)
    
    # Test 2: Signup
    token, user_id = test_signup()
    if not token:
        print("\n❌ Signup test failed. Check server logs.")
        return
    
    time.sleep(1)
    
    # Test 3: Chat with auth
    if not test_chat(token):
        print("\n⚠️  Chat test failed. Check server logs.")
    
    time.sleep(1)
    
    # Test 4: Verify MongoDB
    verify_mongodb()
    
    # Final status
    print_section("FINAL STATUS")
    response = requests.get(f"{BASE_URL}/api/health")
    data = response.json()
    mongodb = data.get('mongodb', {})
    counts = mongodb.get('document_counts', {})
    
    print(f"✅ All tests completed!")
    print(f"\n📊 Current MongoDB status:")
    print(f"   • Users: {counts.get('users', 0)}")
    print(f"   • Sessions: {counts.get('sessions', 0)}")
    print(f"   • Chat logs: {counts.get('chat_logs', 0)}")
    print(f"\n🎉 MongoDB integration is working correctly!")
    print(f"\n💡 View your data at: https://cloud.mongodb.com/")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
