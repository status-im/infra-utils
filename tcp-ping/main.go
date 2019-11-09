package main

import (
	"errors"
	"log"
	"net"
	"os"
	"syscall"
	"time"
)

var addresses = []string{
	"8.8.8.8:53", // will succeed
	//"8.8.8.8:88", // will fail
}

const timeout time.Duration = 2000 * time.Millisecond

const epollET = 1 << 31

func parseSockAddr(addr string) (syscall.Sockaddr, error) {
	tAddr, err := net.ResolveTCPAddr("tcp", addr)
	if err != nil {
		return nil, err
	}
	var addr4 [4]byte
	if tAddr.IP != nil {
		copy(addr4[:], tAddr.IP.To4()) // copy last 4 bytes of slice to array
	}
	return &syscall.SockaddrInet4{Port: tAddr.Port, Addr: addr4}, nil
}

func Ping(address string, timeout time.Duration) error {
	fd, err := syscall.Socket(syscall.AF_INET, syscall.SOCK_STREAM, 0)
	if err != nil {
		return os.NewSyscallError("socket", err)
	}
	syscall.CloseOnExec(fd)
	log.Println("Socket FD:", fd)

	err = syscall.SetsockoptInt(fd, syscall.SOL_TCP, syscall.TCP_QUICKACK, 0)
	if err != nil {
		return os.NewSyscallError("setsockopt", err)
	}

	var zeroLinger = syscall.Linger{Onoff: 1, Linger: 0}
	err = syscall.SetsockoptLinger(fd, syscall.SOL_SOCKET, syscall.SO_LINGER, &zeroLinger)
	if err != nil {
		return os.NewSyscallError("setsockoptlinger", err)
	}

	rAddr, err := parseSockAddr(address)
	if err != nil {
		return errors.New("failed to parse address")
	}

	err = syscall.Connect(fd, rAddr)
	if err != nil {
		return os.NewSyscallError("connect", err)
	}

	epfd, err := syscall.EpollCreate1(syscall.EPOLL_CLOEXEC)
	if err != nil {
		return os.NewSyscallError("epoll_create1", err)
	}
	log.Println("Epoll FD:", epfd)

	var event syscall.EpollEvent
	event.Events = (syscall.EPOLLOUT | syscall.EPOLLIN | epollET)
	event.Fd = int32(fd)

	err = syscall.EpollCtl(epfd, syscall.EPOLL_CTL_ADD, fd, &event)
	if err != nil {
		return os.NewSyscallError("epoll_ctl", err)
	}

	var epollEvents [1]syscall.EpollEvent
	var nEvents int
	nEvents, err = syscall.EpollWait(epfd, epollEvents[:], int(timeout.Milliseconds()))

	log.Println("EpollWait #:", nEvents)
	if nEvents == 0 {
		return errors.New("no events found")
	}

	errCode, err := syscall.GetsockoptInt(fd, syscall.SOL_SOCKET, syscall.SO_ERROR)
	if err != nil {
		return os.NewSyscallError("getsockoptint", err)
	}
	log.Println("SO_ERROR:", errCode)

	log.Println("EpollEvent:", epollEvents[0])
	if epollEvents[0].Events&syscall.EPOLLOUT != 0 {
		return nil
	}

	return errors.New("UNKNOWN ")
}

func main() {
	log.SetPrefix("TCP_PING:")

	for i := 0; i < len(addresses); i++ {
		log.Println("PINGING:", addresses[i])
		err := Ping(addresses[i], timeout)
		if err != nil {
			log.Println("FAILURE:", err)
		} else {
			log.Println("SUCCESS")
		}
	}
}
