# Django CFG API - Go Client

Auto-generated Go client for Django CFG API (v1.0.0).

Generated at: 2025-10-28T07:47:33.585068

## Installation

```bash
go get crypto
```

## Usage

```go
package main

import (
	"context"
	"fmt"
	"log"

	"crypto"
)

func main() {
	// Create client
	client := crypto.NewClient(
		"https://api.example.com",
		crypto.WithToken("your-api-token"),
	)

	// Make requests
	ctx := context.Background()

	// Example: List users
	// users, err := client.UsersList(ctx, nil)
	// if err != nil {
	//     log.Fatal(err)
	// }
	// fmt.Printf("Users: %+v\n", users)
}
```

## Features

- ✅ Type-safe Go structs
- ✅ Context-aware requests
- ✅ Bearer token authentication
- ✅ Comprehensive error handling
- ✅ Auto-generated from OpenAPI spec

## Documentation

See the OpenAPI specification for full API documentation.