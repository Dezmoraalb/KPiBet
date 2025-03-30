from aiogram import Dispatcher

from fluent_loader import get_fluent_localization
from middlewares import L10nMiddleware, UserActivityMiddleware

# init locale
locale = get_fluent_localization()

# init dispatcher
dp = Dispatcher()

# Apply middlewares
dp.message.outer_middleware(L10nMiddleware(locale))
dp.message.outer_middleware(UserActivityMiddleware())

dp.pre_checkout_query.outer_middleware(L10nMiddleware(locale))

dp.callback_query.outer_middleware(L10nMiddleware(locale))
dp.callback_query.outer_middleware(UserActivityMiddleware())

dp.my_chat_member.outer_middleware(L10nMiddleware(locale))
