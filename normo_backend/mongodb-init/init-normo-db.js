// MongoDB initialization script for Normo database
db = db.getSiblingDB('normo_db');

// Create collections
db.createCollection('conversations');
db.createCollection('messages');

// Create indexes for better performance
db.conversations.createIndex({ "conversation_id": 1 }, { unique: true });
db.conversations.createIndex({ "user_id": 1 });
db.conversations.createIndex({ "created_at": 1 });
db.conversations.createIndex({ "updated_at": 1 });

db.messages.createIndex({ "conversation_id": 1 });
db.messages.createIndex({ "role": 1 });
db.messages.createIndex({ "timestamp": 1 });

print('Normo database initialized successfully');
