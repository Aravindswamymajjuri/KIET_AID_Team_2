#!/usr/bin/env python3
"""
MongoDB Connection Test Script
Tests the connection to MongoDB Atlas and displays status
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import mongodb, init_mongodb

def test_mongodb_connection():
    """Test MongoDB connection and display detailed status"""
    
    print("=" * 60)
    print("🔍 MONGODB CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Attempt connection
    print("📡 Attempting to connect to MongoDB Atlas...")
    success = init_mongodb()
    print()
    
    if not success:
        print("❌ CONNECTION FAILED!")
        print()
        print("Possible reasons:")
        print("  1. Internet connection issue")
        print("  2. MongoDB Atlas credentials incorrect")
        print("  3. IP address not whitelisted in MongoDB Atlas")
        print("  4. Network firewall blocking connection")
        print()
        print("💡 Please check:")
        print("  - Your internet connection")
        print("  - MongoDB Atlas dashboard: https://cloud.mongodb.com/")
        print("  - Network Access settings to allow your IP")
        return False
    
    print("✅ CONNECTION SUCCESSFUL!")
    print()
    
    # Get detailed status
    status = mongodb.check_connection()
    
    print("=" * 60)
    print("📊 DATABASE STATUS")
    print("=" * 60)
    print()
    print(f"🔗 Connected: {status['connected']}")
    print(f"💾 Database: {status.get('database', 'N/A')}")
    print(f"📦 Collections: {', '.join(status.get('collections', [])) or 'None yet'}")
    print()
    print(f"📈 Document Counts:")
    for collection, count in status.get('document_counts', {}).items():
        print(f"   - {collection}: {count} documents")
    print()
    print(f"💿 Database Size: {status.get('database_size', 'N/A')}")
    print()
    
    # Test operations
    print("=" * 60)
    print("🧪 TESTING OPERATIONS")
    print("=" * 60)
    print()
    
    try:
        from database import get_users_collection, get_sessions_collection, get_chat_logs_collection
        
        # Test users collection
        users = get_users_collection()
        user_count = users.count_documents({})
        print(f"✅ Users collection accessible: {user_count} users")
        
        # Test sessions collection
        sessions = get_sessions_collection()
        session_count = sessions.count_documents({})
        print(f"✅ Sessions collection accessible: {session_count} sessions")
        
        # Test chat logs collection
        chat_logs = get_chat_logs_collection()
        log_count = chat_logs.count_documents({})
        print(f"✅ Chat logs collection accessible: {log_count} logs")
        
        print()
        print("🎉 All collections are working properly!")
        
    except Exception as e:
        print(f"❌ Error testing operations: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✅ MONGODB IS READY TO USE!")
    print("=" * 60)
    print()
    print("Your backend is now configured to use MongoDB Atlas for:")
    print("  ✓ User authentication (signup/login)")
    print("  ✓ Session management")
    print("  ✓ Chat history storage")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = test_mongodb_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        try:
            mongodb.disconnect()
        except:
            pass
