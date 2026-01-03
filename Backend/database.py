# ===================== MONGODB CONFIGURATION =====================
# MongoDB Atlas connection and database management

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ===================== CONFIGURATION =====================
# MongoDB Atlas connection string
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://Healthcare:Healthcare@healthcare.v60erxm.mongodb.net/"
)
DATABASE_NAME = "healthcare_db"

# ===================== MONGODB MANAGER =====================

class MongoDB:
    """MongoDB connection and database manager"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.is_connected = False
        
    def connect(self):
        """Establish connection to MongoDB Atlas"""
        try:
            logger.info("🔄 Connecting to MongoDB Atlas...")
            
            # Create MongoDB client
            self.client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test the connection
            self.client.admin.command('ping')
            
            # Get database
            self.db = self.client[DATABASE_NAME]
            self.is_connected = True
            
            logger.info(f"✅ Successfully connected to MongoDB Atlas!")
            logger.info(f"📊 Database: {DATABASE_NAME}")
            
            # Create indexes for better performance
            self._create_indexes()
            
            return True
            
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.is_connected = False
            return False
            
        except ServerSelectionTimeoutError as e:
            logger.error(f"❌ MongoDB server selection timeout: {e}")
            logger.error("💡 Check your internet connection and MongoDB Atlas configuration")
            self.is_connected = False
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            self.is_connected = False
            return False
    
    def _create_indexes(self):
        """Create database indexes for optimized queries"""
        try:
            # Users collection indexes
            # username unique (case-insensitive if supported via collation)
            try:
                from pymongo.collation import Collation
                self.db.users.create_index("username", unique=True, collation=Collation(locale='en', strength=2))
            except Exception:
                # Fallback to a normal unique index (case-sensitive) if collation not supported
                try:
                    self.db.users.create_index("username", unique=True)
                except Exception as e:
                    logger.warning(f"⚠️ Could not create username unique index: {e}")
            # email unique only when present (partial index) to allow users without email
            try:
                # Inspect existing indexes and replace any problematic non-partial/non-sparse email unique index
                try:
                    existing_indexes = list(self.db.users.list_indexes())
                    email_index = None
                    for idx in existing_indexes:
                        key = dict(idx.get('key', {}))
                        if 'email' in key:
                            email_index = idx
                            break
                    if email_index:
                        is_partial = 'partialFilterExpression' in email_index and email_index.get('partialFilterExpression')
                        is_sparse = email_index.get('sparse', False)
                        if not is_partial and not is_sparse:
                            index_name = email_index.get('name')
                            try:
                                self.db.users.drop_index(index_name)
                                logger.info(f"ℹ️ Dropped existing non-partial email index: {index_name}")
                            except Exception as e:
                                logger.warning(f"⚠️ Could not drop existing email index {index_name}: {e}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to inspect existing indexes for users collection: {e}")

                # Prefer a partial index that only indexes documents where email is present
                try:
                    self.db.users.create_index(
                        "email",
                        unique=True,
                        partialFilterExpression={"email": {"$exists": True, "$type": "string"}}
                    )
                except Exception:
                    # Fall back to sparse index if partialFilterExpression unsupported
                    try:
                        self.db.users.create_index("email", unique=True, sparse=True)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not create email unique index: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Error handling email index creation: {e}")
            # user_id unique
            self.db.users.create_index("user_id", unique=True)
            
            # Sessions collection indexes
            self.db.sessions.create_index("token", unique=True)
            self.db.sessions.create_index("user_id")
            self.db.sessions.create_index("expires_at")
            
            # Chat logs collection indexes
            self.db.chat_logs.create_index("user_id")
            self.db.chat_logs.create_index("timestamp")
            self.db.chat_logs.create_index([("user_id", 1), ("timestamp", -1)])
            # Conversation-level indexes for fast retrieval of conversation threads
            try:
                self.db.chat_logs.create_index("conversation_id")
                self.db.chat_logs.create_index([("conversation_id", 1), ("timestamp", 1)])
            except Exception as e:
                logger.warning(f"⚠️ Could not create conversation indexes: {e}")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Error creating indexes: {e}")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self.is_connected or self.db is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.db[collection_name]
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("🔌 MongoDB connection closed")
    
    def check_connection(self) -> dict:
        """Check MongoDB connection status and return details"""
        if not self.is_connected:
            return {
                "connected": False,
                "message": "Not connected to MongoDB",
                "database": None
            }
        
        try:
            # Ping the server
            self.client.admin.command('ping')
            
            # Get database stats
            stats = self.db.command("dbStats")
            
            # Get collections
            collections = self.db.list_collection_names()
            
            # Count documents in each collection
            collection_counts = {}
            for coll_name in ["users", "sessions", "chat_logs"]:
                if coll_name in collections:
                    collection_counts[coll_name] = self.db[coll_name].count_documents({})
                else:
                    collection_counts[coll_name] = 0
            
            return {
                "connected": True,
                "message": "Successfully connected to MongoDB Atlas",
                "database": DATABASE_NAME,
                "collections": collections,
                "document_counts": collection_counts,
                "database_size": f"{stats.get('dataSize', 0) / (1024 * 1024):.2f} MB"
            }
            
        except Exception as e:
            logger.error(f"Error checking connection: {e}")
            return {
                "connected": False,
                "message": f"Connection check failed: {str(e)}",
                "database": DATABASE_NAME
            }

# ===================== GLOBAL INSTANCE =====================
mongodb = MongoDB()

# ===================== INITIALIZATION =====================
def init_mongodb():
    """Initialize MongoDB connection"""
    return mongodb.connect()

# ===================== HELPER FUNCTIONS =====================
def get_users_collection():
    """Get users collection"""
    return mongodb.get_collection("users")

def get_sessions_collection():
    """Get sessions collection"""
    return mongodb.get_collection("sessions")

def get_chat_logs_collection():
    """Get chat logs collection"""
    return mongodb.get_collection("chat_logs")
