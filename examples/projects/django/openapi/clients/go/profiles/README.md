# Django CFG API - Go Client

Auto-generated Go client for Django CFG API (v1.0.0).

Generated at: 2025-10-27T19:13:23.824142

## Installation

```bash
go get profiles
```

## Usage

```go
package main

import (
	"context"
	"fmt"
	"log"

	"profiles"
)

func main() {
	// Create client
	client := profiles.NewClient(
		"https://api.example.com",
		profiles.WithToken("your-api-token"),
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