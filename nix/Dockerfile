FROM alpine:3.9

ARG NIX_VERSION
ARG JENKINS_UID
ARG JENKINS_GID

COPY --from=nixos/nix /nix /nix
ADD nix.sh /etc/profile.d/nix.sh

RUN chown ${JENKINS_UID}:${JENKINS_GID} -R /nix

RUN addgroup -g ${JENKINS_GID} jenkins
RUN adduser -D -g jenkins -u ${JENKINS_UID} -G jenkins jenkins

WORKDIR /home/jenkins
USER jenkins

ADD nix.conf /home/jenkins/.config/nix/nix.conf
ADD default.nix /home/jenkins/default.nix

RUN ln -s /nix/var/nix/profiles/default ~/.nix-profile
RUN echo $HOME
RUN echo $USER
RUN echo $PATH
RUN echo $SHELL
RUN nix-channel --add https://nixos.org/channels/nixos-19.03-small
RUN nix-channel --update
RUN nix-shell --run 'echo'

RUN echo 'exec /nix/var/nix/profiles/default/bin/nix-shell' > /etc/profile.d/nix-shell.sh

MAINTAINER Jakub Sokolowski "jakub@status.im"
LABEL description="Adjusted Nix Docker image for use with Jenkins"
