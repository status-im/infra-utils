#!/usr/bin/env bash

# This script was used to recover a lost Ansible/Terraform/Consul inventory

STAGE=$(cat .terraform/environment)
ENV="eth"

cf_record() {
    ~/work/infra-utils/cloudflare/fqdns.py -d statusim.net | grep "$@" | cut -d' ' -f1
}

do_instance() {
    doctl compute droplet list | grep "$@" | cut -d' ' -f1
}

do_firewall() {
    doctl compute firewall list | grep "$@" | cut -d' ' -f1
}

do_eip() {
    doctl compute floating-ip list | grep "$@" | cut -d' ' -f1
}

gc_filter() {
    echo "${@}" | sed 's/\\\./-/g'
}

gc_instance_json() {
    gcloud compute instances list --filter="name=$(gc_filter ${@})" --format=json
}

gc_instance() {
    NAME=$(gc_instance_json "${@}" | jq -r '.[0].name')
    echo "russia-servers/us-central1-a/${NAME}"
}

gc_firewall_json() {
    FILTER=$(gc_filter ${@})
    FILTER=$(echo "${FILTER}" | sed 's/gc-//g')
    gcloud compute firewall-rules list --filter="name=allow-${FILTER}" --format=json
}

gc_firewall() {
    gc_firewall_json "${@}" | jq -r '.[0].name'
}

gc_eip_json() {
    gcloud compute addresses list --filter="name=$(gc_filter ${@})" --format=json
}

gc_eip() {
    gc_eip_json "${@}" | jq -r '.[0].name'
}

ac_instance_json() {
    aliyun ecs DescribeInstances --InstanceName="${@}"
}

ac_instance() {
    ac_instance_json "$@" | jq -r '.Instances.Instance[0].InstanceId'
}

ac_eip() {
    ac_instance_json "$@" | jq -r '.Instances.Instance[0].EipAddress.AllocationId'
}

ac_secgroup() {
    ac_instance_json "$@" | jq -r '.Instances.Instance[0].SecurityGroupIds.SecurityGroupId[0]'
}

key() {
    NODE=$(echo "$@" | awk -F'.' '{print $2}')
    DC=$(echo "$@" | awk -F'.' '{print $4}')
    NUM=$(echo "$@" | grep -o -P '\[\K\d+')
    if [[ -z "$NUM" ]]; then
        NUM=0
    fi

    if [[ "$DC" == "do-eu-amsterdam3" ]]; then
        DC="do-ams3"
    fi

    if [[ "$NODE" == "whisper" ]]; then
        NODE="node"
    fi

    if [[ "$@" =~ .*hosts$ ]]; then
        echo "${NODE}s\.${DC}\.${ENV}\.${STAGE}"
    elif [[ "$@" =~ .*firewall.* ]]; then
        echo "${NODE}\.${DC}\.${ENV}\.${STAGE}"
    else
        echo "${NODE}-0$((NUM+1))\.${DC}\.${ENV}\.${STAGE}"
    fi
}

echo " |============================================================"
while read -r TARGET; do
    KEY=$(key $TARGET)
    echo " | * $TARGET"
    echo " | + $KEY"
    if [[ "$TARGET" =~ .*digitalocean_droplet.* ]]; then
        ID=$(do_instance $KEY)
    elif [[ "$TARGET" =~ .*digitalocean_firewall.* ]]; then
        ID=$(do_firewall $KEY)
    elif [[ "$TARGET" =~ .*digitalocean_floating_ip.* ]]; then
        ID=$(do_eip $KEY)
    elif [[ "$TARGET" =~ .*alicloud_instance.* ]]; then
        ID=$(ac_instance $KEY)
    elif [[ "$TARGET" =~ .*alicloud_eip.* ]]; then
        ID=$(ac_eip $KEY)
    elif [[ "$TARGET" =~ .*alicloud_security_group.* ]]; then
        ID=$(ac_secgroup $KEY)
    elif [[ "$TARGET" =~ .*google_compute_instance.* ]]; then
        ID=$(gc_instance $KEY)
    elif [[ "$TARGET" =~ .*google_compute_firewall.* ]]; then
        ID=$(gc_firewall $KEY)
    elif [[ "$TARGET" =~ .*google_compute_address.* ]]; then
        ID=$(gc_eip $KEY)
    elif [[ "$TARGET" =~ .*cloudflare_record.* ]]; then
        ID="statusim.net/$(cf_record $KEY)"
    fi
    
    if [[ -n "$ID" ]]; then
        echo " | @ $ID"
        if [[ "$RUN" == true ]]; then
            echo " |------------------------------------------------------------"
            terraform import "$TARGET" "$ID"
        fi
    else
        echo " | @ -----XXX-----"
        exit 1
    fi
    echo " |============================================================"
done <<< $(cat plan.log | grep "$@")
