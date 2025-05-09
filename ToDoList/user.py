class user:
    def __init__(self, username, password, mail, role):
        self.username = username
        self.password = password
        self.mail = mail
        self.role = role

    def __str__(self):
        return f'username: {self.username}, password: {self.password}, mail: {self.mail}, role: {self.role}'
