class UsersModule:
    def __init__(self):
        self._users = {}

    def get_user(self, userid):
        if userid not in self._users:
            return None

        return self._users[userid]

    def add_user(self, userid, display_name):
        self._users[userid] = {
            "display_name": display_name,
            "sign": None,
            "card": None,
            "userid": userid,
        }

    def update_user(self, userid, **kwargs):
        user = self.get_user(userid)
        if not user:
            return

        # if any of the params is None, we should not update the user.
        # this is to avoid bad prediction from bugging the user cache
        if any(value is None for value in kwargs.values()):
            return

        for key, value in kwargs.items():
            user[key] = value
