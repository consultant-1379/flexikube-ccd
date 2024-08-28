#!/bin/bash
set -e
namespace=$1
pod_name=$2
image=$3
option_check_only_version=$4

if ! which kubectl ; then
  export PATH=/usr/local/bin:$PATH
fi >/dev/null 2>&1

username=$(whoami)
homedir=$(getent passwd "${username}" | cut -d: -f6)
if [[ "${username}" == "root" ]]; then
    export KUBECONFIG=/etc/kubernetes/admin.conf
elif [[ -z "${homedir// }" ]]; then
    echo "[`basename $0`][`date -R`] ERROR: Unable to determine home directory for user [${username}]."
    exit 1
else
    export KUBECONFIG="${homedir}"/.kube/config
fi

if [[ "$image"x == x ]] || [[ "${pod_name}"x == x ]] || [[ "$namespace"x == x ]];then
  echo "[`basename $0`][`date -R`] ERROR: Wrong parameter: container: ${pod_name}, image: $image, namespace: $namespace"
  exit 1
fi
# Consider only release version for coredns
if [[ "$pod_name" == "coredns" ]];then
    image=$(echo $image | awk -F'-' '{print $1}')
fi
echo "[`basename $0`][`date -R`] INFO: get pod ${namespace}/${pod_name} matching image ${image} [${option_check_only_version}] with user ${username} using KUBECONFIG=${KUBECONFIG}";

set +e;
pods=$(kubectl -n $namespace get pod 2>/dev/null |grep -E "^${pod_name}"|awk '{print $1}');
if [[ "$pods"x == x ]];then
  err=$(kubectl -n ${namespace} get pod 2>&1 >/dev/null);
  if [[ "$err" != "" && "$err" != "No resources found." ]]; then
      # provide details of connection errors
      echo "[`basename $0`][`date -R`] ERROR: error running 'kubectl -n ${namespace} get pod'"
      kubectl --v=4 get pod -n ${namespace} 2>&1 > /dev/null;
  else
      echo "[`basename $0`][`date -R`] ERROR: ${namespace}/${pod_name} not found"
  fi
  exit 1
fi
set -e;
missmatch="none"
for pod in $pods;do
  match=$(kubectl -n $namespace get pod $pod -o jsonpath={.spec.containers[0].image})
  if [[ "$option_check_only_version" == version ]];then
    # check only on version
    match=$(echo $match|rev |cut -d ':' -f1|rev)
  fi
  if [[ "$image" != "$match" ]];then
    echo "[`basename $0`][`date -R`] ERROR: Images do not match; expected($image) got($match) for pod: $pod"
    missmatch="yes"
  else
    echo "[`basename $0`][`date -R`] INFO: Images match; got($match) for pod: $pod"
  fi
  if [[ "$(kubectl -n $namespace get pod $pod -o jsonpath={.status.phase})" != Running ]];then
    echo "[`basename $0`][`date -R`] ERROR: $pod is not running"
    missmatch="yes"
  fi
done
if [[ $missmatch = "yes" ]];then
  exit 1
fi
