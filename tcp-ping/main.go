package main

import (
	"errors"
	"log"
	"net"
	"os"
	"time"

	"golang.org/x/sys/unix"
)

var addresses = []string{
	"8.8.8.8:53", // will succeed
	//"8.8.8.8:88", // will fail
}

const timeout time.Duration = 2000 * time.Millisecond

func parseSockAddr(addr string) (unix.Sockaddr, error) {
	tAddr, err := net.ResolveTCPAddr("tcp", addr)
	if err != nil {
		return nil, err
	}
	var addr4 [4]byte
	if tAddr.IP != nil {
		copy(addr4[:], tAddr.IP.To4()) // copy last 4 bytes of slice to array
	}
	return &unix.SockaddrInet4{Port: tAddr.Port, Addr: addr4}, nil
}

func Ping(address string, timeout time.Duration) error {
	fd, err := unix.Socket(unix.AF_INET, unix.SOCK_STREAM, 0)
	if err != nil {
		return os.NewSyscallError("socket", err)
	}
	unix.CloseOnExec(fd)
	log.Println("Socket FD:", fd)

	err = unix.SetsockoptInt(fd, unix.IPPROTO_TCP, unix.TCP_QUICKACK, 0)
	if err != nil {
		return os.NewSyscallError("setsockopt", err)
	}

	var zeroLinger = unix.Linger{Onoff: 1, Linger: 0}
	err = unix.SetsockoptLinger(fd, unix.SOL_SOCKET, unix.SO_LINGER, &zeroLinger)
	if err != nil {
		return os.NewSyscallError("setsockoptlinger", err)
	}

	rAddr, err := parseSockAddr(address)
	if err != nil {
		return errors.New("failed to parse address")
	}

	err = unix.Connect(fd, rAddr)
	if err != nil {
		return os.NewSyscallError("connect", err)
	}

	epfd, err := unix.EpollCreate1(unix.EPOLL_CLOEXEC)
	if err != nil {
		return os.NewSyscallError("epoll_create1", err)
	}
	log.Println("Epoll FD:", epfd)

	var event unix.EpollEvent
	event.Events = (unix.EPOLLOUT | unix.EPOLLIN | unix.EPOLLET)
	event.Fd = int32(fd)

	err = unix.EpollCtl(epfd, unix.EPOLL_CTL_ADD, fd, &event)
	if err != nil {
		return os.NewSyscallError("epoll_ctl", err)
	}

	var epollEvents [1]unix.EpollEvent
	var nEvents int
	nEvents, err = unix.EpollWait(epfd, epollEvents[:], int(timeout.Milliseconds()))

	log.Println("EpollWait #:", nEvents)
	if nEvents == 0 {
		return errors.New("no events found")
	}

	errCode, err := unix.GetsockoptInt(fd, unix.SOL_SOCKET, unix.SO_ERROR)
	if err != nil {
		return os.NewSyscallError("getsockoptint", err)
	}
	log.Println("SO_ERROR:", errCode)

	log.Println("EpollEvent:", epollEvents[0])
	if epollEvents[0].Events&unix.EPOLLOUT != 0 {
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
