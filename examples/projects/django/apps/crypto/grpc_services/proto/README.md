# Proto Files

This directory contains Protocol Buffer definitions for the Crypto gRPC service.

## Files

- `crypto_service.proto` - Complete service definition with 14 RPC methods

## Generating Python Code

To generate Python code from proto files:

```bash
# From the grpc_services directory
./generate_proto.sh

# Or manually
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./generated \
    --grpc_python_out=./generated \
    ./proto/*.proto
```

## Service Definition

The `crypto_service.proto` file defines:

### Services
- **CryptoService** - Main service with 14 RPC methods

### RPC Methods
- Coin Operations: GetCoin, ListCoins, SearchCoins, GetTopCoins, StreamPrices (streaming)
- Wallet Operations: GetWallet, ListWallets, GetPortfolio, Deposit, Withdraw, Transfer
- Market Statistics: GetMarketStats, GetTrendingCoins

### Message Types
- 30+ message types for requests/responses
- Reserved field ranges for future compatibility
- Decimal precision using strings

See the proto file for complete API documentation.
