ARG NIX_VERSION
FROM nixos/nix:${NIX_VERSION}

ARG JENKINS_UID
ARG JENKINS_GID

RUN apk add --no-cache file strace

RUN chown ${JENKINS_UID}:${JENKINS_GID} -R /nix

RUN addgroup -g ${JENKINS_GID} jenkins
RUN adduser -D -g jenkins -u ${JENKINS_UID} -G jenkins jenkins -s /bin/bash

# this special wrapper script runs sh inside of nix-shell
ADD bash.sh /bin/bash

WORKDIR /home/jenkins
USER jenkins

ADD nix.conf /home/jenkins/.config/nix/nix.conf
ADD default.nix /home/jenkins/default.nix
ADD default.nix /bin/default.nix

RUN ls -l /nix/var/nix/profiles/
RUN ln -s /nix/var/nix/profiles/default ~/.nix-profile
RUN nix-channel --add https://nixos.org/channels/nixos-19.03-small
RUN nix-channel --update
RUN nix-shell --run 'echo'

MAINTAINER Jakub Sokolowski "jakub@status.im"
LABEL description="Adjusted Nix Docker image for use with Jenkins"
ENTRYPOINT ["/bin/bash"]
