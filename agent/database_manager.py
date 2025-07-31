from tinydb import TinyDB, Query
from typing import Optional, Dict, Any
from .data_models import User

class DatabaseManager:
    def __init__(self, db_path="fuelyt_data.json"):
        self.db = TinyDB(db_path)
        self.users_table = self.db.table('users')

    def get_user(self, user_id: str) -> Optional[User]:
        UserQuery = Query()
        user_data = self.users_table.get(UserQuery.user_id == user_id)
        if user_data:
            return User(**user_data)
        return None

    def create_user(self, user: User) -> User:
        self.users_table.insert(user.dict())
        return user

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        UserQuery = Query()
        self.users_table.update(updates, UserQuery.user_id == user_id)
        return self.get_user(user_id)

db_manager = DatabaseManager()
