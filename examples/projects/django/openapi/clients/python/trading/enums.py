from enum import IntEnum, StrEnum


class OrderOrderType(StrEnum):
    """
    * `market` - Market
    * `limit` - Limit
    * `stop_loss` - Stop Loss
    """

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"



class OrderSide(StrEnum):
    """
    * `buy` - Buy
    * `sell` - Sell
    """

    BUY = "buy"
    SELL = "sell"



class OrderStatus(StrEnum):
    """
    * `pending` - Pending
    * `filled` - Filled
    * `cancelled` - Cancelled
    """

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"



class OrderCreateOrderType(StrEnum):
    """
    * `market` - Market
    * `limit` - Limit
    * `stop_loss` - Stop Loss
    """

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"



class OrderCreateSide(StrEnum):
    """
    * `buy` - Buy
    * `sell` - Sell
    """

    BUY = "buy"
    SELL = "sell"



class OrderCreateRequestOrderType(StrEnum):
    """
    * `market` - Market
    * `limit` - Limit
    * `stop_loss` - Stop Loss
    """

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"



class OrderCreateRequestSide(StrEnum):
    """
    * `buy` - Buy
    * `sell` - Sell
    """

    BUY = "buy"
    SELL = "sell"



class OrderRequestOrderType(StrEnum):
    """
    * `market` - Market
    * `limit` - Limit
    * `stop_loss` - Stop Loss
    """

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"



class OrderRequestSide(StrEnum):
    """
    * `buy` - Buy
    * `sell` - Sell
    """

    BUY = "buy"
    SELL = "sell"



class PatchedOrderRequestOrderType(StrEnum):
    """
    * `market` - Market
    * `limit` - Limit
    * `stop_loss` - Stop Loss
    """

    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"



class PatchedOrderRequestSide(StrEnum):
    """
    * `buy` - Buy
    * `sell` - Sell
    """

    BUY = "buy"
    SELL = "sell"



