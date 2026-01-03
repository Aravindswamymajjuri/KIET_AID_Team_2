#!/usr/bin/env python3
"""
Quick MongoDB Status Check
Shows current connection status and document counts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_status():
    """Quick MongoDB status check"""
    print("\n" + "="*50)
    print("  MONGODB STATUS CHECK")
    print("="*50 + "\n")
    
    try:
        from database import mongodb, init_mongodb
        
        # Try to connect if not connected
        if not mongodb.is_connected:
            print("🔄 Connecting to MongoDB...")
            init_mongodb()
        
        # Get status
        status = mongodb.check_connection()
        
        if status['connected']:
            print("✅ Status: CONNECTED")
            print(f"📊 Database: {status.get('database', 'N/A')}")
            print(f"💾 Size: {status.get('database_size', 'N/A')}")
            print()
            print("📈 Document Counts:")
            for coll, count in status.get('document_counts', {}).items():
                print(f"   • {coll}: {count}")
            print()
            print("🎉 MongoDB is working properly!")
        else:
            print("❌ Status: NOT CONNECTED")
            print(f"📝 Message: {status.get('message', 'Unknown error')}")
            print()
            print("💡 The backend will use JSON file storage as fallback.")
        
    except ImportError:
        print("❌ MongoDB module not found")
        print("💡 Install dependencies: pip install pymongo dnspython")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Run 'python test_mongodb.py' for detailed diagnostics")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    quick_status()
