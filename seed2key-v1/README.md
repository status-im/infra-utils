# Description

This is a tiny utility for converting a Status V1 seed phrase into a private key.

I created it so I could use my normal Status account with the [status-console-client](https://github.com/status-im/status-console-client).

It is written in [GoLang](https://golang.org/), and requires the [Go compiler](https://golang.org/dl/).

# Usage

The utility receives the seed phrase via standard input:
```bash
 $ echo "this is my secret seed phrase" | go run main.go
0x334d5305f760c5767e25fd23480a46790ba9c6cc3519196a96675259515128fa
```

# WARNING

You might want to avoid using `echo` to not store your seed phrase in shell history.
