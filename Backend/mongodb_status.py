#!/usr/bin/env python3
"""
Visual MongoDB Connection Status Display
Run this anytime to see if MongoDB is connected
"""

import sys
import os

# Try to use venv if available
venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'Scripts', 'python.exe')
if os.path.exists(venv_python) and sys.executable != venv_python:
    import subprocess
    subprocess.run([venv_python, __file__])
    sys.exit(0)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show_status():
    """Display MongoDB connection status with visual indicators"""
    
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*15 + "MONGODB CONNECTION STATUS" + " "*18 + "║")
    print("╚" + "═"*58 + "╝\n")
    
    try:
        from database import mongodb, init_mongodb
        
        # Connect if not already connected
        if not mongodb.is_connected:
            print("🔄 Connecting to MongoDB Atlas...\n")
            success = init_mongodb()
            if not success:
                raise Exception("Connection failed")
        
        # Get detailed status
        status = mongodb.check_connection()
        
        if status['connected']:
            print("┌" + "─"*58 + "┐")
            print("│ " + "✅ CONNECTION: SUCCESSFUL".ljust(57) + "│")
            print("├" + "─"*58 + "┤")
            print(f"│ 🌐 Database: {status.get('database', 'N/A')}".ljust(59) + "│")
            print(f"│ 💾 Size: {status.get('database_size', 'N/A')}".ljust(59) + "│")
            print("├" + "─"*58 + "┤")
            print("│ " + "📊 COLLECTIONS & DOCUMENTS".ljust(57) + "│")
            print("├" + "─"*58 + "┤")
            
            counts = status.get('document_counts', {})
            print(f"│   👥 users: {counts.get('users', 0)} documents".ljust(59) + "│")
            print(f"│   🔐 sessions: {counts.get('sessions', 0)} documents".ljust(59) + "│")
            print(f"│   💬 chat_logs: {counts.get('chat_logs', 0)} documents".ljust(59) + "│")
            print("└" + "─"*58 + "┘")
            
            print("\n✨ Your backend is ready to store data in MongoDB Atlas!\n")
            print("📍 Test it:")
            print("   • Start server: python -m uvicorn app:app --reload")
            print("   • Health check: http://localhost:8000/api/health")
            print("   • API docs: http://localhost:8000/docs")
            
        else:
            print("┌" + "─"*58 + "┐")
            print("│ " + "❌ CONNECTION: FAILED".ljust(57) + "│")
            print("├" + "─"*58 + "┤")
            print(f"│ Message: {status.get('message', 'Unknown')}"[:56].ljust(57) + "│")
            print("└" + "─"*58 + "┘")
            
            print("\n⚠️  MongoDB is not connected")
            print("💡 But don't worry! The backend will use JSON files as backup.\n")
            print("🔧 Troubleshooting:")
            print("   • Check internet connection")
            print("   • Verify MongoDB Atlas is accessible")
            print("   • Run: python test_mongodb.py (for detailed diagnostics)")
        
    except ImportError:
        print("┌" + "─"*58 + "┐")
        print("│ " + "❌ MONGODB MODULE NOT FOUND".ljust(57) + "│")
        print("└" + "─"*58 + "┘")
        print("\n📦 Please install MongoDB drivers:")
        print("   pip install pymongo dnspython")
    
    except Exception as e:
        print("┌" + "─"*58 + "┐")
        print("│ " + "❌ ERROR".ljust(57) + "│")
        print("└" + "─"*58 + "┘")
        print(f"\n⚠️  {str(e)}")
        print("\n🔧 Run detailed diagnostics: python test_mongodb.py")
    
    print()

if __name__ == "__main__":
    show_status()
