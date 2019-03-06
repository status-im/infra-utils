FROM ubuntu:16.04

ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

ARG NIX_VERSION
ARG JENKINS_UID
ARG JENKINS_GID

RUN apt-get update \
 && apt-get -q -y --no-install-recommends \
      install file locales curl strace jq bzip2 ca-certificates \
 && apt-get clean \
 && locale-gen ${LANG} \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man

ADD nix-install-${NIX_VERSION}.sh /tmp/nix-install.sh

RUN groupadd --gid ${JENKINS_GID} jenkins \
 && useradd --shell /bin/bash --create-home --password "" \
      --comment "jenkins" --groups root \
      --uid ${JENKINS_UID} --gid ${JENKINS_GID} jenkins

# this special wrapper script runs sh inside of nix-shell
#ADD bash.sh /bin/bash
ADD nix.conf /home/jenkins/.config/nix/nix.conf
ADD default.nix /home/jenkins/default.nix
ADD default.nix /bin/default.nix

RUN mkdir /nix

RUN chown ${JENKINS_UID}:${JENKINS_GID} -R /nix /home/jenkins

WORKDIR /home/jenkins
USER jenkins

RUN export USER=jenkins \
 && /tmp/nix-install.sh \
 && . ~/.nix-profile/etc/profile.d/nix.sh \
 && nix-shell --run 'echo'

# hack to avoid calling login
ENV USER=jenkins

MAINTAINER Jakub Sokolowski "jakub@status.im"
LABEL description="Adjusted Nix Docker image for use with Jenkins"
