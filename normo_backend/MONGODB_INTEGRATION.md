# MongoDB Integration for Normo Backend

This document describes the MongoDB integration implemented in the Normo backend for storing conversation data alongside the existing JSON file storage.

## Overview

The system now uses a **hybrid storage approach** that combines:
- **MongoDB**: Primary database for conversation storage with better performance and scalability
- **JSON Files**: Backup storage for redundancy and data portability

## Architecture

### Storage Components

1. **HybridConversationStorage**: Main storage class that manages both MongoDB and JSON storage
2. **MongoDBStorage**: Dedicated MongoDB storage implementation
3. **ConversationStorage**: Original JSON file storage (maintained for compatibility)

### Data Flow

```
API Request → HybridConversationStorage → MongoDB (Primary) + JSON (Backup)
```

## MongoDB Configuration

### Docker Compose Setup

The MongoDB service is configured in `docker-compose.yml`:

```yaml
mongodb:
  image: mongo:7.0
  container_name: normo-mongodb
  ports:
    - "27017:27017"
  environment:
    - MONGO_INITDB_ROOT_USERNAME=normo_user
    - MONGO_INITDB_ROOT_PASSWORD=normo_password
    - MONGO_INITDB_DATABASE=normo_db
  volumes:
    - mongodb_data:/data/db
    - ./normo_backend/mongodb-init:/docker-entrypoint-initdb.d
  networks:
    - normo-network
  restart: unless-stopped
```

### Database Structure

**Database**: `normo_db`

**Collections**:
- `conversations`: Stores conversation metadata
- `messages`: Stores individual messages with conversation references

### Indexes

The following indexes are created for optimal performance:

```javascript
// conversations collection
db.conversations.createIndex({ "conversation_id": 1 }, { unique: true });
db.conversations.createIndex({ "user_id": 1 });
db.conversations.createIndex({ "created_at": 1 });
db.conversations.createIndex({ "updated_at": 1 });

// messages collection
db.messages.createIndex({ "conversation_id": 1 });
db.messages.createIndex({ "role": 1 });
db.messages.createIndex({ "timestamp": 1 });
```

## Environment Variables

The system uses the following environment variable:

```bash
MONGODB_URL=mongodb://normo_user:normo_password@mongodb:27017/normo_db?authSource=admin
```

## API Endpoints

### New Endpoints

- `POST /sync-conversations`: Sync existing JSON conversations to MongoDB

### Existing Endpoints (Enhanced)

All existing conversation endpoints now work with both MongoDB and JSON storage:
- `POST /chat`: Create and manage conversations
- `GET /conversations`: List conversations
- `GET /conversations/{conversation_id}`: Get specific conversation
- `POST /conversations`: Create new conversation

## Data Models

### Conversation Document (MongoDB)

```javascript
{
  "_id": ObjectId,
  "conversation_id": "uuid-string",
  "user_id": "string-or-null",
  "created_at": ISODate,
  "updated_at": ISODate,
  "context": {}
}
```

### Message Document (MongoDB)

```javascript
{
  "_id": ObjectId,
  "conversation_id": "uuid-string",
  "role": "user|assistant",
  "content": "string",
  "timestamp": ISODate,
  "agent_steps": ["string"],
  "pdf_names": ["string"],
  "source_citations": [{}],
  "meta_data": {}
}
```

## Features

### 1. Redundancy

- **Primary**: MongoDB for fast queries and scalability
- **Backup**: JSON files for data portability and disaster recovery

### 2. Fallback Mechanism

If MongoDB is unavailable, the system automatically falls back to JSON storage:

```python
# Try MongoDB first
if self.mongodb_storage:
    try:
        result = self.mongodb_storage.get_conversation(conversation_id)
        if result:
            return result
    except Exception as e:
        print(f"⚠️ MongoDB unavailable: {e}")

# Fallback to JSON
return self.json_storage.get_conversation(conversation_id)
```

### 3. Data Synchronization

- All operations write to both MongoDB and JSON files
- Sync endpoint allows manual synchronization from JSON to MongoDB
- Automatic loading of existing conversations from MongoDB on startup

### 4. Performance Optimizations

- In-memory caching for frequently accessed conversations
- Database indexes for fast queries
- Connection pooling for MongoDB

## Usage

### Starting the System

1. **With Docker Compose** (Recommended):
   ```bash
   docker-compose up -d
   ```

2. **Local Development**:
   ```bash
   # Start MongoDB locally
   docker run -d -p 27017:27017 --name normo-mongodb \
     -e MONGO_INITDB_ROOT_USERNAME=normo_user \
     -e MONGO_INITDB_ROOT_PASSWORD=normo_password \
     -e MONGO_INITDB_DATABASE=normo_db \
     mongo:7.0

   # Start backend
   cd normo_backend
   MONGODB_URL="mongodb://normo_user:normo_password@localhost:27017/normo_db?authSource=admin" \
   uv run python -m src.normo_backend.api.app
   ```

### Syncing Existing Data

To sync existing JSON conversations to MongoDB:

```bash
curl -X POST "http://localhost:8000/sync-conversations"
```

### Monitoring

Check MongoDB status:

```bash
# Connect to MongoDB
docker exec -it normo-mongodb mongosh -u normo_user -p normo_password --authenticationDatabase admin

# Check collections
use normo_db
db.conversations.countDocuments()
db.messages.countDocuments()
```

## Error Handling

The system includes comprehensive error handling:

1. **MongoDB Connection Errors**: Automatically falls back to JSON storage
2. **Data Sync Errors**: Logs errors but continues operation
3. **Validation Errors**: Maintains data integrity across both storage systems

## Benefits

### 1. Scalability
- MongoDB can handle large volumes of conversation data
- Horizontal scaling capabilities
- Better performance for complex queries

### 2. Reliability
- Dual storage ensures data safety
- Automatic fallback mechanisms
- Data redundancy

### 3. Performance
- Faster queries with proper indexing
- In-memory caching
- Optimized data structures

### 4. Flexibility
- Easy migration between storage systems
- JSON files for data portability
- MongoDB for production scalability

## Migration Strategy

### From JSON-only to Hybrid

1. Deploy new version with MongoDB
2. Run sync endpoint to migrate existing data
3. Verify data integrity
4. Monitor performance improvements

### Rollback Plan

If issues arise:
1. Set `MONGODB_URL` to empty/null
2. System automatically uses JSON-only storage
3. No data loss as JSON files are maintained

## Security Considerations

1. **Authentication**: MongoDB uses username/password authentication
2. **Network**: MongoDB is only accessible within Docker network
3. **Data Encryption**: Consider enabling MongoDB encryption at rest for production
4. **Access Control**: Implement proper user roles and permissions

## Monitoring and Maintenance

### Health Checks

- API health endpoint: `GET /health`
- MongoDB connection status in logs
- Storage system status indicators

### Backup Strategy

1. **MongoDB**: Regular database dumps
2. **JSON Files**: File system backups
3. **Both**: Cross-verification of data integrity

### Performance Monitoring

- Query performance metrics
- Storage usage monitoring
- Connection pool statistics

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**:
   - Check if MongoDB container is running
   - Verify connection string
   - Check network connectivity

2. **Sync Issues**:
   - Check file permissions
   - Verify JSON file format
   - Review error logs

3. **Performance Issues**:
   - Check MongoDB indexes
   - Monitor memory usage
   - Review query patterns

### Debug Commands

```bash
# Check MongoDB logs
docker logs normo-mongodb

# Check backend logs
docker logs normo-backend

# Test MongoDB connection
docker exec -it normo-mongodb mongosh -u normo_user -p normo_password --authenticationDatabase admin
```

## Future Enhancements

1. **Replica Sets**: For high availability
2. **Sharding**: For horizontal scaling
3. **Advanced Indexing**: For complex queries
4. **Data Archiving**: For long-term storage
5. **Analytics**: Conversation analytics and insights
