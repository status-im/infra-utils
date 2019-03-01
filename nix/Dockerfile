ARG NIX_VERSION
FROM nixos/nix:${NIX_VERSION}

ARG JENKINS_UID
ARG JENKINS_GID

RUN addgroup -g ${JENKINS_GID} jenkins \
 && adduser -D -u ${JENKINS_UID} -G jenkins jenkins \
      -s /nix/var/nix/profiles/default/bin/nix-shell \
 && chown jenkins:jenkins -R /nix

ADD nix.conf /home/jenkins/.config/nix/nix.conf
ADD default.nix home/jenkins/default.nix

WORKDIR /home/jenkins

USER jenkins

MAINTAINER Jakub Sokolowski "jakub@status.im"
LABEL description="Adjusted Nix Docker image for use with Jenkins"
