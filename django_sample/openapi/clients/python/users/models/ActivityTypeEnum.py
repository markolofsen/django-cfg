from enum import Enum


class ActivityTypeEnum(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    POST_CREATED = "post_created"
    COMMENT_CREATED = "comment_created"
    ORDER_PLACED = "order_placed"
    PROFILE_UPDATED = "profile_updated"
