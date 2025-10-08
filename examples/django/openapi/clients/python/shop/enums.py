from enum import IntEnum, StrEnum


class OrderDetail.status(StrEnum):
    """* `pending` - Pending * `processing` - Processing * `shipped` - Shipped *
`delivered` - Delivered * `cancelled` - Cancelled * `refunded` - Refunded"""

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class OrderList.status(StrEnum):
    """* `pending` - Pending * `processing` - Processing * `shipped` - Shipped *
`delivered` - Delivered * `cancelled` - Cancelled * `refunded` - Refunded"""

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class PatchedPostUpdateRequest.status(StrEnum):
    """* `draft` - Draft * `published` - Published * `archived` - Archived"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostCreate.status(StrEnum):
    """* `draft` - Draft * `published` - Published * `archived` - Archived"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostCreateRequest.status(StrEnum):
    """* `draft` - Draft * `published` - Published * `archived` - Archived"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostDetail.status(StrEnum):
    """* `draft` - Draft * `published` - Published * `archived` - Archived"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostDetailRequest.status(StrEnum):
    """* `draft` - Draft * `published` - Published * `archived` - Archived"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostLike.reaction(StrEnum):
    """* `like` - 👍 * `love` - ❤️ * `laugh` - 😂 * `wow` - 😮 * `sad` - 😢 * `angry` -
😠"""

    LIKE = "like"
    LOVE = "love"
    LAUGH = "laugh"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"



class PostList.status(StrEnum):
    """* `draft` - Draft * `published` - Published * `archived` - Archived"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostUpdate.status(StrEnum):
    """* `draft` - Draft * `published` - Published * `archived` - Archived"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class PostUpdateRequest.status(StrEnum):
    """* `draft` - Draft * `published` - Published * `archived` - Archived"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"



class ProductDetail.status(StrEnum):
    """* `active` - Active * `inactive` - Inactive * `out_of_stock` - Out of Stock"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"



class ProductList.status(StrEnum):
    """* `active` - Active * `inactive` - Inactive * `out_of_stock` - Out of Stock"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"



