class ProductNotFoundError(Exception):
    def __init__(self, message='Product was not found.'):
        super().__init__(message)


class UserNotFoundError(Exception):
    def __init__(self, message='Username was not found.'):
        super().__init__(message)


class UsernameTakenError(Exception):
    def __init__(self, message='Username already exists.'):
        super().__init__(message)


class WrongPasswordError(Exception):
    def __init__(self, message='Wrong password. Please try again'):
        super().__init__(message)


class PasswordLengthError(Exception):
    def __init__(self, message='Password is of an invalid length.'):
        super().__init__(message)

class AccountAlreadyApprovedError(Exception):
    def __init__(self, message='Account is already approved.'):
        super().__init__(message)

class EmptyFieldsError(Exception):
    def __init__(self, message='Empty inputs detected. Please fill in all required fields.'):
        super().__init__(message)

