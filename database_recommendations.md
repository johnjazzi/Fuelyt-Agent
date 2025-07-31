# Database Recommendations for Fuelyt Agent

## Lightweight Local Testing Options (Ranked by Simplicity)

### 1. **TinyDB** (Recommended for MVP/Testing)
- **Type**: Pure Python, document-oriented NoSQL database
- **File size**: Single Python file (~100KB)
- **Storage**: JSON files on disk
- **Pros**: 
  - Zero configuration
  - Pure Python (no external dependencies)
  - Perfect for single-user JSON documents
  - Easy to inspect data (plain JSON files)
  - Excellent for prototyping
- **Cons**: Not suitable for production scale
- **Setup**: `pip install tinydb`

```python
from tinydb import TinyDB, Query
db = TinyDB('fuelyt_users.json')
users_table = db.table('users')
```

### 2. **SQLite with JSON Support** (Good balance)
- **Type**: Embedded relational database with JSON1 extension
- **Storage**: Single .db file
- **Pros**:
  - Built into Python standard library
  - Excellent JSON support with JSON1 extension
  - ACID transactions
  - Can scale to production
- **Cons**: Requires SQL knowledge
- **Setup**: No installation needed (built-in)

```python
import sqlite3
import json

conn = sqlite3.connect('fuelyt.db')
conn.execute('''CREATE TABLE users (
    id TEXT PRIMARY KEY,
    data JSON
)''')
```

### 3. **Shelve** (Python Built-in)
- **Type**: Python's built-in persistent dictionary
- **Storage**: Binary files
- **Pros**: 
  - Built into Python
  - Dictionary-like interface
  - No external dependencies
- **Cons**: 
  - Binary format (not human-readable)
  - No concurrent access
- **Setup**: No installation needed

```python
import shelve
db = shelve.open('fuelyt_data.db')
db['user_123'] = user_data_dict
```

### 4. **PickleDB** (Simple key-value)
- **Type**: Lightweight key-value store
- **Storage**: JSON or binary files
- **Pros**: Simple API, human-readable JSON option
- **Cons**: Limited querying capabilities
- **Setup**: `pip install pickledb`

## Production Considerations

For production deployment, consider:
- **MongoDB Atlas** (serverless MongoDB)
- **DynamoDB** (if using AWS Lambda)
- **Firestore** (if using Google Cloud Functions)
- **PlanetScale** (MySQL with JSON support)

## Recommendation

**Start with TinyDB** for development and testing. It perfectly matches your requirements:
- Single JSON document per user
- Zero configuration
- Easy to inspect and debug
- Seamless transition to production databases later
- Perfect for serverless function environments