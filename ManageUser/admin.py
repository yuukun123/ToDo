from ToDoList.user import user

class admin:
    def __init__(self, filename="users.json"):
        self.users = []
        self.filename = filename
        self.loadUser()
