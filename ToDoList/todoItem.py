from datetime import datetime

# Class đại diện cho 1 nhiệm vụ
class TodoItem:
    def __init__(self, title, hour=0, minute=0, deadline="",description="", completed=False, completed_at = None, music = ""):
        self.title = title
        self.hour = hour
        self.minute = minute
        self.description = description
        self.deadline = deadline
        self.completed = completed
        self.completed_at = completed_at
        self.music = music

    def to_dict(self):
        return {
            "title": self.title,
            "hour": self.hour,
            "minute": self.minute,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "music": self.music
        }
