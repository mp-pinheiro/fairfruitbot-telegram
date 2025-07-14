from unittest.mock import Mock

from commands import Tarot


def test_version():
    # This is just a placeholder test
    assert True


# def test_tarot_new_user():
#     tarot = Tarot()

#     update = Mock()
#     update.message.from_user.id = "123"
#     update.message.from_user.username = "test_user"
#     update.message.from_user.full_name = "Test User"
#     update.message.chat.id = "456"

#     context = Mock()
#     context.bot.send_message = Mock()
#     context.args = []  # assume daily command

#     tarot._process(update, context)

#     user = tarot._users["123"]
#     assert user["display_name"] == "test_user"
#     assert user["request_date"]
#     assert user["card"]


# def test_tarot_existing_user():
#     tarot = Tarot()

#     # mock bot and dispatcher
#     update = Mock()
#     update.message.from_user.id = '123'
#     update.message.from_user.username = 'test_user'
#     update.message.from_user.full_name = 'Test User'
#     update.message.chat.id = '456'

#     context = Mock()
#     context.bot.send_message = Mock()

#     # make request
#     tarot._process(update, context)

#     # assert response
#     user = tarot._users['123']
#     display_name = user['display_name']
#     card = user['card']
#     request_date = user['request_date']
#     assert display_name == 'test_user'
#     assert card
#     assert request_date

#     # make request again
#     tarot._process(update, context)

#     # assert that user and card are the same
#     user = tarot._users['123']
#     assert user['card'] == card
#     assert user['request_date'] == request_date
#     assert user['display_name'] == display_name

# def test_tarot_expired_date():
#     tarot = Tarot()

#     # mock bot and dispatcher
#     update = Mock()
#     update.message.from_user.id = '123'
#     update.message.from_user.username = 'test_user'
#     update.message.from_user.full_name = 'Test User'
#     update.message.chat.id = '456'

#     context = Mock()
#     context.bot.send_message = Mock()

#     # mock user and request date
#     user = {
#         'display_name': 'test_user',
#         'request_date': '2020-01-01',
#         'card': Mock()
#     }
#     tarot._users['123'] = user

#     # make request
#     card = user['card']
#     tarot._process(update, context)

#     # assert card is different
#     assert user['card'] != card
