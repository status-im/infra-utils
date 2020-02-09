# Description

This is a tiny utility for converting a Status seed phrase into a private key.

I created it so I could use my normal Status account with the [status-console-client](https://github.com/status-im/status-console-client).

# Usage

```bash
 $ echo "this is my secret seed phrase" | go run main.go
0x334d5305f760c5767e25fd23480a46790ba9c6cc3519196a96675259515128fa
```

# Warning

The current values of `go.mod` and `go.sum` pull old versions of `status-protocol-go` and in result they only convert old Beta Status App seed phrase correctly.

For converting the seed phrase of current app version the simplest way would be to remove `go.mod` and `go.sum` and build with newest versions.
