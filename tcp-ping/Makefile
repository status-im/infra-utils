c-amd64:
	gcc main.c -o tcp-ping-amd64

c-arm:
	arm-linux-gnueabi-gcc -static main.c -o tcp-ping-arm64

c-arm64:
	aarch64-linux-gnu-gcc -static -Werror main.c -o tcp-ping-arm64

go-amd64:
	GOARCH=amd64 go build -o tcp-ping-amd64 main.go 

go-arm:
	GOARCH=arm go build -o tcp-ping-arm main.go

go-arm64:
	GOARCH=arm64 go build -o tcp-ping-arm64 main.go

