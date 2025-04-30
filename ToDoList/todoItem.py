from datetime import datetime

# Class đại diện cho 1 nhiệm vụ
class TodoItem:
    def __init__(self, title, description="", completed=False, completed_at = None):
        self.title = title
        self.description = description
        self.completed = completed
        self.completed_at = completed_at


    def to_dict(self):
        return {"title": self.title,
                "description": self.description,
                "completed": self.completed,
                "completed_at": self.completed_at
                }