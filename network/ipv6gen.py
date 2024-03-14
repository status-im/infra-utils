#!/usr/bin/env python3
import sys
import random
import argparse
from ipaddress import ip_address, ip_network, summarize_address_range

HELP_DESCRIPTION = 'Simple tool to generate IPv6 address ranges.'
HELP_EXAMPLE = 'Example: ./ipv6gen.py --network F00D:CAFE::/64 --start F00D:CAFE::10 --end F00D:CAFE::ffff --count 20'


def parse_args():
    parser = argparse.ArgumentParser(
        description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE
    )
    parser.add_argument('-n', '--network', default='F00D:CAFE::0/32',
                      help='IPv6 Network address.')
    parser.add_argument('-s', '--start', default='F00D:CAFE::1',
                      help='Start of addresses to list.')
    parser.add_argument('-e', '--end', default='F00D:CAFE::F',
                      help='Start of addresses to list.')
    parser.add_argument('-c', '--count', type=int,
                      help='Number addresses to generate.')
    parser.add_argument('-f', '--full', action='store_true',
                      help='Print full, unabbreviated addresses.')

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    net = ip_network(args.network)
    start = ip_address(args.start)
    end = ip_address(args.end)

    print('Network:', net)
    print('Start:', start)
    print('End:', end)
    if args.count:
        print('Count:', args.count)
    print()

    if start not in net:
        print('Start beyond network range!')
        sys.exit(1)
    if end not in net:
        print('Start beyond network range!')
        sys.exit(1)

    if args.count:
        ip_range = [start+i for i in range(0, args.count)]
    else:
        ip_range = []
        ip = start
        while ip < end:
            ip_range.append(ip)
            ip += 1

    for ip in ip_range:
        if ip < start:
            print('Address beyond range:', ip)
            sys.exit(1)
        if ip >= end:
            print('Address beyond range:', ip)
            sys.exit(1)
        if args.full:
            print(ip.exploded)
        else:
            print(ip)


if __name__ == '__main__':
    main()
