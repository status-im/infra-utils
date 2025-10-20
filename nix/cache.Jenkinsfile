#!/usr/bin/env groovy
library 'status-jenkins-lib@v1.9.24'

pipeline {
  agent {
    docker {
      label 'linuxcontainer'
      image 'harbor.status.im/infra/ci-build-containers:linux-base-1.0.0'
      args '--volume=/nix:/nix ' +
           '--volume=/etc/nix:/etc/nix '
    }
  }

  parameters {
    string(
      name: 'NIX_CACHE_HOST',
      description: 'FQDN of Nix binary cache host.',
      defaultValue: params.NIX_CACHE_HOST ?: 'cache-01.he-eu-hel1.ci.nix.status.im'
    )
    string(
      name: 'NIX_CACHE_USER',
      description: 'Username for Nix binary cache host.',
      defaultValue: params.NIX_CACHE_USER ?: 'nix-cache'
    )
  }

  environment {
    NIX_CONFIG = 'experimental-features = nix-command flakes'
    NIX_SSHOPTS = '-oStrictHostKeyChecking=accept-new'
    NIX_STORE_CMD = '/nix/var/nix/profiles/default/bin/nix-store'
    NIX_SSH_REMOTE = "ssh://${params.NIX_CACHE_USER}@${params.NIX_CACHE_HOST}?remote-program=${env.NIX_STORE_CMD}"
  }

  options {
    timestamps()
    disableConcurrentBuilds()
    /* Prevent Jenkins jobs from running forever */
    timeout(time: 120, unit: 'MINUTES')
    /* Limit builds retained */
    buildDiscarder(logRotator(
      numToKeepStr: '20',
      daysToKeepStr: '30',
      artifactNumToKeepStr: '1',
    ))
  }

  stages {
    stage('Collect') {
      steps { script {
        exitCode = nix.shell(
          """
            find /nix/store/ -mindepth 1 -maxdepth 1 \
              | grep -v -e '.*.links\$' -e '.*.lock\$' -e '.*.drv\$' -e '.*.drv\$' \
              | xargs nix path-info --recursive \
              > "${WORKSPACE_TMP}/store-paths.txt"
          """,
          packages: ['findutils'],
          pure: false,
          returnStatus: true
        )
        /* Some paths can throw 'path is not valid' errors, but it's not fatal. */
        if (exitCode != 0) {
          currentBuild.result = 'UNSTABLE'
        }
        if (lineCount("${WORKSPACE_TMP}/store-paths.txt") == 0) {
          throw new Exception("No Nix store paths found to copy.")
        }
      } }
    }

    stage('Upload') {
      steps { script {
        sshagent(credentials: ['nix-cache-ssh']) {
          nix.shell(
            """
              cat "${WORKSPACE_TMP}/store-paths.txt" \
                | nix copy --stdin --to "${NIX_SSH_REMOTE}"
            """,
            packages: ['openssh'],
            pure: false
          )
        }
      } }
    }
  }
  post {
    always { script {
      nix.shell(
        'nix-store --optimize',
        packages: ['nixVersions.nix_2_24'],
        pure: false
      )
    } }
  }
}

def lineCount(filePath) {
    return sh(
        script: "wc -l ${filePath}",
        returnStdout: true
    ).trim()
}
