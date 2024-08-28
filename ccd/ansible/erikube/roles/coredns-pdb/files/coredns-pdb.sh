#!/usr/bin/env bash

_add_coredns_pdb()
{
    # Check if coredns PDB is already configured
    local pdb=$(/usr/local/bin/kubectl --kubeconfig /etc/kubernetes/admin.conf get pdb coredns-pdb -n kube-system 2>&1 | grep -v "not found")

    echo ${pdb} > /var/log/eccd/coredns.log
    [[ ${pdb}X == "X" ]] || return 0

    cat <<EOF > /var/lib/eccd/coredns-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: coredns-pdb
  namespace: kube-system 
spec:
  maxUnavailable: 2
  selector:
    matchLabels:
      k8s-app: kube-dns
EOF
chmod 0644 /var/lib/eccd/coredns-pdb.yaml

    pdb=$(/usr/local/bin/kubectl --kubeconfig /etc/kubernetes/admin.conf apply -f /var/lib/eccd/coredns-pdb.yaml)
    echo ${pdb} > /var/log/eccd/coredns.log
}

_add_coredns_pdb
