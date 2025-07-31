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
        
        # To handle nested updates correctly, we'll fetch the user, update the
        # specific fields, and then write the entire object back.
        user_data = self.users_table.get(UserQuery.user_id == user_id)
        if not user_data:
            return None
        
        for key, value in updates.items():
            # This logic can be expanded to handle deeper nesting if needed
            if '.' in key:
                # Handle nested keys like "profile.name"
                # This is a simple implementation and might need to be more robust
                # depending on the complexity of the updates.
                parts = key.split('.')
                d = user_data
                for part in parts[:-1]:
                    d = d.setdefault(part, {})
                d[parts[-1]] = value
            else:
                user_data[key] = value

        self.users_table.update(user_data, UserQuery.user_id == user_id)
        return self.get_user(user_id)

    def update_user_workouts(self, user_id: str, workouts: Dict[str, Any]) -> Optional[User]:
        """A dedicated method to update the workouts field."""
        return self.update_user(user_id, {"workouts": workouts})

db_manager = DatabaseManager()
