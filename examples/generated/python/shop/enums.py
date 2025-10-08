from enum import IntEnum, StrEnum


class OrderDetailStatus(StrEnum):
    """
    * `pending` - Pending
    * `processing` - Processing
    * `shipped` - Shipped
    * `delivered` - Delivered
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class OrderListStatus(StrEnum):
    """
    * `pending` - Pending
    * `processing` - Processing
    * `shipped` - Shipped
    * `delivered` - Delivered
    * `cancelled` - Cancelled
    * `refunded` - Refunded
    """

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PatchedPostUpdateRequestStatus(StrEnum):
    """
    * `draft` - Draft
    * `published` - Published
    * `archived` - Archived
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostCreateStatus(StrEnum):
    """
    * `draft` - Draft
    * `published` - Published
    * `archived` - Archived
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostCreateRequestStatus(StrEnum):
    """
    * `draft` - Draft
    * `published` - Published
    * `archived` - Archived
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostDetailStatus(StrEnum):
    """
    * `draft` - Draft
    * `published` - Published
    * `archived` - Archived
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostDetailRequestStatus(StrEnum):
    """
    * `draft` - Draft
    * `published` - Published
    * `archived` - Archived
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostLikeReaction(StrEnum):
    """
    * `like` - 👍
    * `love` - ❤️
    * `laugh` - 😂
    * `wow` - 😮
    * `sad` - 😢
    * `angry` - 😠
    """

    LIKE = "like"
    LOVE = "love"
    LAUGH = "laugh"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"



class PostListStatus(StrEnum):
    """
    * `draft` - Draft
    * `published` - Published
    * `archived` - Archived
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostUpdateStatus(StrEnum):
    """
    * `draft` - Draft
    * `published` - Published
    * `archived` - Archived
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostUpdateRequestStatus(StrEnum):
    """
    * `draft` - Draft
    * `published` - Published
    * `archived` - Archived
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class ProductDetailStatus(StrEnum):
    """
    * `active` - Active
    * `inactive` - Inactive
    * `out_of_stock` - Out of Stock
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"



class ProductListStatus(StrEnum):
    """
    * `active` - Active
    * `inactive` - Inactive
    * `out_of_stock` - Out of Stock
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"



