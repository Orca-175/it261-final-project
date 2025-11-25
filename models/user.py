from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, active, role):
        self.id = id
        self.username = username
        self.role = role
        self.active = active
    
    def get_id(self):
        return f'{self.role}.{self.id}'