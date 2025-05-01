from datetime import datetime

# Class đại diện cho 1 nhiệm vụ
class TodoItem:
    def __init__(self, title, hour=0, minute=0, deadline="",description="", completed=False, completed_at = None):
        self.title = title
        self.hour = hour
        self.minute = minute
        self.description = description
        self.deadline = deadline
        self.completed = completed
        self.completed_at = completed_at


    def to_dict(self):
        return {"title": self.title,
                "hour": self.hour,
                "minute": self.minute,
                "description": self.description,
                "deadline": self.deadline,
                "completed": self.completed,
                "completed_at": self.completed_at
                }