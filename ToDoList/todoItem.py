# Class đại diện cho 1 nhiệm vụ
class TodoItem:
    def __init__(self, title, description="", completed=False):
        self.title = title
        self.description = description
        self.completed = completed

    def to_dict(self):
        return {"title": self.title, "completed": self.completed}