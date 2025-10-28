# Django CFG API - Go Client

Auto-generated Go client for Django CFG API (v1.0.0).

Generated at: 2025-10-28T07:47:34.573413

## Installation

```bash
go get cfg
```

## Usage

```go
package main

import (
	"context"
	"fmt"
	"log"

	"cfg"
)

func main() {
	// Create client
	client := cfg.NewClient(
		"https://api.example.com",
		cfg.WithToken("your-api-token"),
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