package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/ethereum/go-ethereum/crypto"
	"github.com/status-im/status-go/extkeys"
)

func main() {
	// read the seed phrase from stdin
	reader := bufio.NewReader(os.Stdin)
	readPhrase, err := reader.ReadString('\n')
	if err != nil {
		fmt.Printf("failed to read seed phrase from stdin\n")
		os.Exit(1)
	}
	// trim whitespace
	seedPhrase := strings.TrimSpace(readPhrase)
	// convert the seed phrase to a private key
	mnemonic := extkeys.NewMnemonic()
	masterKey, err := extkeys.NewMaster(mnemonic.MnemonicSeed(seedPhrase, ""))
	if err != nil {
		fmt.Printf("cannot create master extended key: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Depth: %d\n", masterKey.Depth)
	// extract chat key from the master key
	chatKey, err := masterKey.ChildForPurpose(extkeys.KeyPurposeWallet, 0)
	if err != nil {
		fmt.Printf("cannot extract chat key from master key: %v\n", err)
		os.Exit(1)
	}
	// print the private key
	fmt.Printf("%#x\n", crypto.FromECDSA(chatKey.ToECDSA()))
}
