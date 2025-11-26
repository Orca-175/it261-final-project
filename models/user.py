from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, active, role):
        self.id = id
        self.username = username
        self.active = active
        self.role = role

    @property
    def is_active(self):
        return self.active


    def get_id(self):
        return f'{self.role}.{self.id}'
