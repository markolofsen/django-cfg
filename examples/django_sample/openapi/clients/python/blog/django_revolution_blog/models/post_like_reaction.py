from typing import Literal, cast

PostLikeReaction = Literal["angry", "laugh", "like", "love", "sad", "wow"]

POST_LIKE_REACTION_VALUES: set[PostLikeReaction] = {
    "angry",
    "laugh",
    "like",
    "love",
    "sad",
    "wow",
}


def check_post_like_reaction(value: str) -> PostLikeReaction:
    if value in POST_LIKE_REACTION_VALUES:
        return cast(PostLikeReaction, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {POST_LIKE_REACTION_VALUES!r}")
