from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SortBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_BY_UNSPECIFIED: _ClassVar[SortBy]
    RANK: _ClassVar[SortBy]
    PRICE: _ClassVar[SortBy]
    MARKET_CAP: _ClassVar[SortBy]
    VOLUME_24H: _ClassVar[SortBy]
    CHANGE_24H: _ClassVar[SortBy]
    NAME: _ClassVar[SortBy]
    SYMBOL: _ClassVar[SortBy]

class SortOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_ORDER_UNSPECIFIED: _ClassVar[SortOrder]
    ASC: _ClassVar[SortOrder]
    DESC: _ClassVar[SortOrder]

class TrendingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRENDING_TYPE_UNSPECIFIED: _ClassVar[TrendingType]
    TOP_GAINERS: _ClassVar[TrendingType]
    TOP_LOSERS: _ClassVar[TrendingType]
    MOST_TRADED: _ClassVar[TrendingType]
SORT_BY_UNSPECIFIED: SortBy
RANK: SortBy
PRICE: SortBy
MARKET_CAP: SortBy
VOLUME_24H: SortBy
CHANGE_24H: SortBy
NAME: SortBy
SYMBOL: SortBy
SORT_ORDER_UNSPECIFIED: SortOrder
ASC: SortOrder
DESC: SortOrder
TRENDING_TYPE_UNSPECIFIED: TrendingType
TOP_GAINERS: TrendingType
TOP_LOSERS: TrendingType
MOST_TRADED: TrendingType

class Coin(_message.Message):
    __slots__ = ("id", "symbol", "name", "slug", "current_price_usd", "market_cap_usd", "volume_24h_usd", "price_change_24h_percent", "price_change_7d_percent", "price_change_30d_percent", "logo_url", "description", "website", "whitepaper_url", "rank", "is_active", "is_tradeable", "is_price_up_24h", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_USD_FIELD_NUMBER: _ClassVar[int]
    MARKET_CAP_USD_FIELD_NUMBER: _ClassVar[int]
    VOLUME_24H_USD_FIELD_NUMBER: _ClassVar[int]
    PRICE_CHANGE_24H_PERCENT_FIELD_NUMBER: _ClassVar[int]
    PRICE_CHANGE_7D_PERCENT_FIELD_NUMBER: _ClassVar[int]
    PRICE_CHANGE_30D_PERCENT_FIELD_NUMBER: _ClassVar[int]
    LOGO_URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    WHITEPAPER_URL_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_TRADEABLE_FIELD_NUMBER: _ClassVar[int]
    IS_PRICE_UP_24H_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    symbol: str
    name: str
    slug: str
    current_price_usd: str
    market_cap_usd: str
    volume_24h_usd: str
    price_change_24h_percent: str
    price_change_7d_percent: str
    price_change_30d_percent: str
    logo_url: str
    description: str
    website: str
    whitepaper_url: str
    rank: int
    is_active: bool
    is_tradeable: bool
    is_price_up_24h: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., symbol: _Optional[str] = ..., name: _Optional[str] = ..., slug: _Optional[str] = ..., current_price_usd: _Optional[str] = ..., market_cap_usd: _Optional[str] = ..., volume_24h_usd: _Optional[str] = ..., price_change_24h_percent: _Optional[str] = ..., price_change_7d_percent: _Optional[str] = ..., price_change_30d_percent: _Optional[str] = ..., logo_url: _Optional[str] = ..., description: _Optional[str] = ..., website: _Optional[str] = ..., whitepaper_url: _Optional[str] = ..., rank: _Optional[int] = ..., is_active: bool = ..., is_tradeable: bool = ..., is_price_up_24h: bool = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetCoinRequest(_message.Message):
    __slots__ = ("id", "symbol", "slug")
    ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    id: int
    symbol: str
    slug: str
    def __init__(self, id: _Optional[int] = ..., symbol: _Optional[str] = ..., slug: _Optional[str] = ...) -> None: ...

class CoinResponse(_message.Message):
    __slots__ = ("success", "message", "coin")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COIN_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    coin: Coin
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., coin: _Optional[_Union[Coin, _Mapping]] = ...) -> None: ...

class ListCoinsRequest(_message.Message):
    __slots__ = ("page", "page_size", "active_only", "tradeable_only", "sort_by", "sort_order")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ONLY_FIELD_NUMBER: _ClassVar[int]
    TRADEABLE_ONLY_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    active_only: bool
    tradeable_only: bool
    sort_by: SortBy
    sort_order: SortOrder
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., active_only: bool = ..., tradeable_only: bool = ..., sort_by: _Optional[_Union[SortBy, str]] = ..., sort_order: _Optional[_Union[SortOrder, str]] = ...) -> None: ...

class SearchCoinsRequest(_message.Message):
    __slots__ = ("query", "limit")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    query: str
    limit: int
    def __init__(self, query: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class GetTopCoinsRequest(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    def __init__(self, limit: _Optional[int] = ...) -> None: ...

class ListCoinsResponse(_message.Message):
    __slots__ = ("success", "message", "coins", "total_count", "page", "page_size", "total_pages")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    COINS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    coins: _containers.RepeatedCompositeFieldContainer[Coin]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., coins: _Optional[_Iterable[_Union[Coin, _Mapping]]] = ..., total_count: _Optional[int] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ..., total_pages: _Optional[int] = ...) -> None: ...

class StreamPricesRequest(_message.Message):
    __slots__ = ("symbols", "interval_seconds")
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    interval_seconds: int
    def __init__(self, symbols: _Optional[_Iterable[str]] = ..., interval_seconds: _Optional[int] = ...) -> None: ...

class PriceUpdate(_message.Message):
    __slots__ = ("symbol", "price_usd", "change_24h_percent", "timestamp")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    PRICE_USD_FIELD_NUMBER: _ClassVar[int]
    CHANGE_24H_PERCENT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    price_usd: str
    change_24h_percent: str
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, symbol: _Optional[str] = ..., price_usd: _Optional[str] = ..., change_24h_percent: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Wallet(_message.Message):
    __slots__ = ("id", "user_id", "coin_id", "symbol", "coin_name", "balance", "locked_balance", "total_balance", "value_usd", "address", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    COIN_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    COIN_NAME_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    LOCKED_BALANCE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BALANCE_FIELD_NUMBER: _ClassVar[int]
    VALUE_USD_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_id: int
    coin_id: int
    symbol: str
    coin_name: str
    balance: str
    locked_balance: str
    total_balance: str
    value_usd: str
    address: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., user_id: _Optional[int] = ..., coin_id: _Optional[int] = ..., symbol: _Optional[str] = ..., coin_name: _Optional[str] = ..., balance: _Optional[str] = ..., locked_balance: _Optional[str] = ..., total_balance: _Optional[str] = ..., value_usd: _Optional[str] = ..., address: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetWalletRequest(_message.Message):
    __slots__ = ("user_id", "coin_id", "symbol")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    COIN_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    coin_id: int
    symbol: str
    def __init__(self, user_id: _Optional[int] = ..., coin_id: _Optional[int] = ..., symbol: _Optional[str] = ...) -> None: ...

class WalletResponse(_message.Message):
    __slots__ = ("success", "message", "wallet")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    WALLET_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    wallet: Wallet
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., wallet: _Optional[_Union[Wallet, _Mapping]] = ...) -> None: ...

class ListWalletsRequest(_message.Message):
    __slots__ = ("user_id", "exclude_zero_balance")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_ZERO_BALANCE_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    exclude_zero_balance: bool
    def __init__(self, user_id: _Optional[int] = ..., exclude_zero_balance: bool = ...) -> None: ...

class ListWalletsResponse(_message.Message):
    __slots__ = ("success", "message", "wallets", "total_value_usd")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    WALLETS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_USD_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    wallets: _containers.RepeatedCompositeFieldContainer[Wallet]
    total_value_usd: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., wallets: _Optional[_Iterable[_Union[Wallet, _Mapping]]] = ..., total_value_usd: _Optional[str] = ...) -> None: ...

class GetPortfolioRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...

class PortfolioResponse(_message.Message):
    __slots__ = ("success", "message", "total_value_usd", "total_change_24h_usd", "total_change_24h_percent", "coins_count", "holdings", "calculated_at")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_USD_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHANGE_24H_USD_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHANGE_24H_PERCENT_FIELD_NUMBER: _ClassVar[int]
    COINS_COUNT_FIELD_NUMBER: _ClassVar[int]
    HOLDINGS_FIELD_NUMBER: _ClassVar[int]
    CALCULATED_AT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    total_value_usd: str
    total_change_24h_usd: str
    total_change_24h_percent: str
    coins_count: int
    holdings: _containers.RepeatedCompositeFieldContainer[PortfolioHolding]
    calculated_at: _timestamp_pb2.Timestamp
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., total_value_usd: _Optional[str] = ..., total_change_24h_usd: _Optional[str] = ..., total_change_24h_percent: _Optional[str] = ..., coins_count: _Optional[int] = ..., holdings: _Optional[_Iterable[_Union[PortfolioHolding, _Mapping]]] = ..., calculated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PortfolioHolding(_message.Message):
    __slots__ = ("symbol", "coin_name", "balance", "value_usd", "percentage", "change_24h_percent")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    COIN_NAME_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    VALUE_USD_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_24H_PERCENT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    coin_name: str
    balance: str
    value_usd: str
    percentage: str
    change_24h_percent: str
    def __init__(self, symbol: _Optional[str] = ..., coin_name: _Optional[str] = ..., balance: _Optional[str] = ..., value_usd: _Optional[str] = ..., percentage: _Optional[str] = ..., change_24h_percent: _Optional[str] = ...) -> None: ...

class DepositRequest(_message.Message):
    __slots__ = ("user_id", "symbol", "amount", "transaction_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    symbol: str
    amount: str
    transaction_id: str
    def __init__(self, user_id: _Optional[int] = ..., symbol: _Optional[str] = ..., amount: _Optional[str] = ..., transaction_id: _Optional[str] = ...) -> None: ...

class WithdrawRequest(_message.Message):
    __slots__ = ("user_id", "symbol", "amount", "destination_address")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    symbol: str
    amount: str
    destination_address: str
    def __init__(self, user_id: _Optional[int] = ..., symbol: _Optional[str] = ..., amount: _Optional[str] = ..., destination_address: _Optional[str] = ...) -> None: ...

class TransferRequest(_message.Message):
    __slots__ = ("from_user_id", "to_user_id", "symbol", "amount", "note")
    FROM_USER_ID_FIELD_NUMBER: _ClassVar[int]
    TO_USER_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    from_user_id: int
    to_user_id: int
    symbol: str
    amount: str
    note: str
    def __init__(self, from_user_id: _Optional[int] = ..., to_user_id: _Optional[int] = ..., symbol: _Optional[str] = ..., amount: _Optional[str] = ..., note: _Optional[str] = ...) -> None: ...

class TransferResponse(_message.Message):
    __slots__ = ("success", "message", "from_wallet", "to_wallet", "transaction_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FROM_WALLET_FIELD_NUMBER: _ClassVar[int]
    TO_WALLET_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    from_wallet: Wallet
    to_wallet: Wallet
    transaction_id: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., from_wallet: _Optional[_Union[Wallet, _Mapping]] = ..., to_wallet: _Optional[_Union[Wallet, _Mapping]] = ..., transaction_id: _Optional[str] = ...) -> None: ...

class MarketStatsResponse(_message.Message):
    __slots__ = ("success", "message", "total_market_cap_usd", "total_volume_24h_usd", "active_coins_count", "coins_up_24h", "coins_down_24h", "average_change_24h", "calculated_at")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MARKET_CAP_USD_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VOLUME_24H_USD_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_COINS_COUNT_FIELD_NUMBER: _ClassVar[int]
    COINS_UP_24H_FIELD_NUMBER: _ClassVar[int]
    COINS_DOWN_24H_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_CHANGE_24H_FIELD_NUMBER: _ClassVar[int]
    CALCULATED_AT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    total_market_cap_usd: str
    total_volume_24h_usd: str
    active_coins_count: int
    coins_up_24h: int
    coins_down_24h: int
    average_change_24h: str
    calculated_at: _timestamp_pb2.Timestamp
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., total_market_cap_usd: _Optional[str] = ..., total_volume_24h_usd: _Optional[str] = ..., active_coins_count: _Optional[int] = ..., coins_up_24h: _Optional[int] = ..., coins_down_24h: _Optional[int] = ..., average_change_24h: _Optional[str] = ..., calculated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetTrendingCoinsRequest(_message.Message):
    __slots__ = ("type", "limit")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    type: TrendingType
    limit: int
    def __init__(self, type: _Optional[_Union[TrendingType, str]] = ..., limit: _Optional[int] = ...) -> None: ...

class TrendingCoinsResponse(_message.Message):
    __slots__ = ("success", "message", "type", "coins")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COINS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    type: TrendingType
    coins: _containers.RepeatedCompositeFieldContainer[Coin]
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., type: _Optional[_Union[TrendingType, str]] = ..., coins: _Optional[_Iterable[_Union[Coin, _Mapping]]] = ...) -> None: ...
