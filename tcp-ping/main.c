#include <stdio.h> 
#include <stdlib.h> 
#include <errno.h> 
#include <string.h> 
#include <netdb.h> 
#include <fcntl.h>
#include <sys/types.h> 
#include <netinet/in.h> 
#include <sys/socket.h> 
#include <netinet/tcp.h>
#include <sys/epoll.h>
#include <unistd.h>

#define MAXEVENTS 1

int guard(int n, char * err) { if (n == -1) { perror(err); exit(1); } return n; }

int main(int argc, char *argv[])
{
    int sfd, sockErr, numbytes;  
    int port = 53;
    char address[] = "8.8.8.8";

    struct hostent *he;
    struct sockaddr_in their_addr;
    struct epoll_event event;
    struct epoll_event *events;
    
    printf("PINGING: %s:%d\n", address, port);

    if ((he=gethostbyname(address)) == NULL) {
        herror("gethostbyname");
        exit(1);
    }

    if ((sfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket");
        exit(1);
    }

    int i = 1;
    guard(setsockopt(sfd, IPPROTO_TCP, TCP_QUICKACK, (void *)&i, sizeof(i)), "setsockopt");
    guard(fcntl(sfd, F_SETFL, O_NONBLOCK), "fcntl: failed to set non-blocking");

    their_addr.sin_family = AF_INET;      /* host byte order */
    their_addr.sin_port = htons(port);    /* short, network byte order */
    their_addr.sin_addr = *((struct in_addr *)he->h_addr);
    bzero(&(their_addr.sin_zero), 8);     /* zero the rest of the struct */

    connect(sfd, (struct sockaddr *)&their_addr, sizeof(struct sockaddr));

    int epfd = guard(epoll_create1(EPOLL_CLOEXEC), "epoll_create");

    event.data.fd = sfd;
    event.events = EPOLLOUT | EPOLLIN | EPOLLET;
    guard(epoll_ctl (epfd, EPOLL_CTL_ADD, sfd, &event), "epoll_ctl");

    /* Buffer where events are returned */
    events = calloc(MAXEVENTS, sizeof event);

    int nEvents = epoll_wait(epfd, events, MAXEVENTS, -1);
    if (nEvents == 0) {
        perror("epoll_wait");
        exit(1);
    }

    printf("epoll event flags: %d\n", events[0].events);
    printf("epoll event fd: %d\n", events[0].data.fd);
    
    int iSocketOption = 0;
    int iSocketOptionLen = sizeof(int);
    sockErr = getsockopt(sfd, SOL_SOCKET, SO_ERROR, (char *)&iSocketOption, &iSocketOptionLen);
    if (sockErr != 0) {
        perror("getsockopt");
        exit(1);
    }

    close(sfd);

    printf("SUCCESS\n");
    return 0;
}

