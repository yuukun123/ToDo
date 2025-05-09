class user:
    def __init__(self, username, password, confirm_password, mail, role):
        self.username = username
        self.password = password
        self.confirm_password = confirm_password
        self.mail = mail
        self.role = role

    def __str__(self):
        return f'username: {self.username}, password: {self.password}, confirm_password: {self.confirm_password}, mail: {self.mail}, role: {self.role}'
