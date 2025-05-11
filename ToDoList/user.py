class user:
    def __init__(self, username, password, confirm_password, mail, role = "customer", status="active", online = "online"):
        self.username = username
        self.password = password
        self.confirm_password = confirm_password
        self.mail = mail
        self.role = role
        self.status = status
        self.online = online

    def __str__(self):
        return f'username: {self.username}, password: {self.password}, confirm_password: {self.confirm_password}, mail: {self.mail}, role: {self.role}, status: {self.status}, online: {self.online}'
