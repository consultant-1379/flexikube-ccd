import json
from ansible.plugins.lookup import LookupBase
try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

description = '''
This module parses the helm status output
and returns the overall status of that
helm chart.

Available options:
- expected_result:
    - over_all_status:
        Returns True if status of all resources is positive else False
    - pods:
        returns a list of pods with "Running" status

    Default expected_result is "over_all_status"
'''


class LookupModule(LookupBase):
    def run(self, raw_helm_status_output, variables=None, **kwargs):
        expected_result = kwargs.get('expected_result')
        if not expected_result:
            expected_result = 'over_all_status'
        status = self.parse(raw_helm_status_output, expected_result)
        if expected_result == 'over_all_status':
            over_all_status = True
            if not status:
                over_all_status = False
            else:
                for resource in status['RESOURCES']:
                    if not self.check_resource(resource):
                        over_all_status = False
                if status['STATUS'] != 'DEPLOYED':
                    over_all_status = False
            return [over_all_status]

        elif expected_result == 'pods':
            pods = []
            if not status:
                return []
            for resource in status['RESOURCES']:
                if 'v1/Pod' in resource['TYPE']:
                    pods.append(resource['NAME'])
            return pods

    def parse(self, raw_helm_status_output, expected_result):
        status = {}
        display.vvvv("Parsing helm status: \n%s" % raw_helm_status_output)
        keywords = ['LAST DEPLOYED', 'NAMESPACE', 'STATUS', 'RESOURCES']
        keyword_index = 0
        resource_separator = '==>'
        notes_begin_marker = 'NOTES:'
        lines = list(filter(None, raw_helm_status_output[0].split('\n')))
        i = 0
        current_keyword = None
        for line in lines:
            current_keyword = keywords[keyword_index]
            if (line.startswith(current_keyword) and
                    not current_keyword == 'RESOURCES'):
                status.update({current_keyword: line.replace(current_keyword +
                                                             ': ', '')})
                keyword_index += 1
                i += 1
            else:
                if current_keyword == 'RESOURCES':
                    i += 1
                    break

        if current_keyword is None or (current_keyword != 'RESOURCES' and
                                       status['STATUS'] != 'FAILED'):
            err_string = str('Was not able to check RESOURCES from: %s'
                             % raw_helm_status_output[0])
            raise Exception(err_string)
        elif current_keyword != 'RESOURCES' and status['STATUS'] == 'FAILED':
            return None

        status['RESOURCES'] = []
        keys = []
        while True:
            if not i >= len(lines) and lines[i].startswith(resource_separator):
                current_resource_type = lines[i].split(' ')[1]
                keys = list(filter(None, lines[i + 1].split(' ')))
                i += 2
                for res_index in range(i, len(lines)):
                    if lines[res_index].startswith(notes_begin_marker):
                        break
                    resource = {'TYPE': current_resource_type}
                    if lines[res_index].startswith(resource_separator):
                        i = res_index
                        break
                    arguments = list(filter(None, lines[res_index].split(' ')))
                    for key_index in range(0, len(keys)):
                        if key_index < (len(arguments) - 1):
                            resource[keys[key_index]] = arguments[key_index]
                        if key_index == (len(arguments) - 1):
                            if 'AGE' in keys:
                                resource['AGE'] = arguments[key_index]
                            else:
                                _key = keys[key_index]
                                resource[_key] = arguments[key_index]

                        if (key_index > (len(arguments) - 1)
                                and keys[key_index] != 'AGE'):

                            resource[keys[key_index]] = ''
                    status['RESOURCES'].append(resource)
            else:
                break

        return status

    def check_pod(pod):
        if pod['STATUS'] == 'Running' or pod['STATUS'] == 'Completed':
            return True
        return False

    def check_pvc(pvc):
        # TODO
        return True

    def check_deployment(deployment):
        if deployment['UP-TO-DATE'] == deployment['AVAILABLE']:
            return True
        return False

    resource_mapping = {'v1beta1/Deployment': check_deployment,
                        'v1beta2/Deployment': check_deployment,
                        'v1/PersistentVolumeClaim': check_pvc,
                        'v1/Pod': check_pod,
                        'v1/Pod(related)': check_pod}

    def check_resource(self, resource):
        if self.resource_mapping.get(resource['TYPE']):
            return self.resource_mapping.get(resource['TYPE'])(resource)
        return True


# For standalone running of script

sample_helm_status_1 = '''
LAST DEPLOYED: Thu Jul 27 14:39:17 2017
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/PersistentVolumeClaim
NAME                      STATUS   VOLUME                        CAPACITY  ACCESSMODES  STORAGECLASS  AGE
nexenta-stor-nfs-claim-3  Pending  nexenta-stor-nfs-provisioner  5s

==> v1/Pod
NAME        READY  STATUS   RESTARTS  AGE
test-pod-4  0/1    Pending  0         5s
'''

sample_helm_status_2 = '''
LAST DEPLOYED: Mon Aug 28 13:51:33 2017
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/ServiceAccount
NAME             SECRETS  AGE
nfs-provisioner  1        19h

==> v1beta1/ClusterRole
NAME                      AGE
nfs-provisioner-runner    19h
nfs-provisioner-runner-2  19h

==> v1beta1/ClusterRoleBinding
NAME             AGE
nfs-provisioner  19h

==> v1/Service
NAME             CLUSTER-IP    EXTERNAL-IP  PORT(S)                             AGE
nfs-provisioner  10.108.162.0  <none>       2049/TCP,20048/TCP,111/TCP,111/UDP  19h

==> v1beta1/Deployment
NAME             DESIRED  CURRENT  UP-TO-DATE  AVAILABLE  AGE
nfs-provisioner  1        1        1           1          19h

==> v1/StorageClass
NAME         TYPE
erikube-nfs  eccd.local/nfs
'''

sample_helm_status_3 = '''
LAST DEPLOYED: Thu Jul 27 14:39:17 2017
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Pod(related)
NAME        READY  STATUS   RESTARTS  AGE
test-pod-4  0/1    Pending  0         5s
test-pod-5  0/1    Running  0         5s
'''
sample_helm_status_4 = '''
LAST DEPLOYED: Thu Jul 27 14:39:17 2017
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Pod(related)
NAME        READY  STATUS   RESTARTS  AGE
test-pod-4  0/1    Running  0         5s
test-pod-5  0/1    Running  0         5s
'''

sample_helm_status_5 = '''
LAST DEPLOYED: Wed Jun 26 14:48:19 2019
NAMESPACE: k8s-registry
STATUS: DEPLOYED
RESOURCES:
==> v1/Secret
NAME                                  TYPE    DATA  AGE
eric-lcm-container-registry-registry  Opaque  4     1s

==> v1/ConfigMap
NAME                                  DATA  AGE
eric-lcm-container-registry-registry  1     1s

==> v1/Service
NAME                                  TYPE       CLUSTER-IP     EXTERNAL-IP  PORT(S)         AGE
eric-lcm-container-registry-registry  ClusterIP  10.97.237.219  <none>       80/TCP,443/TCP  1s

==> v1beta2/StatefulSet
NAME                                  DESIRED  CURRENT  AGE
eric-lcm-container-registry-registry  1        1        1s

==> v1/Pod(related)
NAME                                    READY  STATUS   RESTARTS  AGE
eric-lcm-container-registry-registry-0  0/1    Pending  0         1s


NOTES:

Add the Container Registry CA certificate to Docker by executing the following command:

  sudo mkdir -p /etc/docker/certs.d/eric-lcm-container-registry-registry.k8s-registry.svc.cluster.local
  sudo cp <external_CAcert.crt> /etc/docker/certs.d/eric-lcm-container-registry-registry.k8s-registry.svc.cluster.local/ca.crt

Get password by executing the following command:
  kubectl get secrets eric-lcm-container-registry-registry -n k8s-registry -o jsonpath="{.data.custom-pwd}" | base64 -d; echo

Login Conatiner Registry  with Docker CLI:\n  docker login eric-lcm-container-registry-registry.k8s-registry.svc.cluster.local
'''


if __name__ == "__main__":
    lm = LookupModule()

    print("Test 1:")
    rv = lm.run([sample_helm_status_1], expected_result='pods')
    if type(rv) is not list:
        print("Error: plugin should return a list")
    assert(len(rv) == 1)
    assert(rv[0] == 'test-pod-4')
    print('  OK')

    print("Test 2:")
    rv = lm.run([sample_helm_status_1], expected_result='over_all_status')
    if type(rv) is not list:
        print("Error: plugin should return a list")
    assert(rv == [False])
    print('  OK')

    print("Test 3:")
    rv = lm.run([sample_helm_status_2], expected_result='over_all_status')
    if type(rv) is not list:
        print("Error: plugin should return a list")
    assert(rv == [True])
    print('  OK')

    print("Test 4:")
    rv = lm.run([sample_helm_status_2])
    if type(rv) is not list:
        print("Error: plugin should return a list")
    assert(rv == [True])
    print('  OK')

    print("Test 5:")
    rv = lm.run([sample_helm_status_3])
    if type(rv) is not list:
        print("Error: plugin should return a list")
    assert(rv == [False])
    print('  OK')

    print("Test 6:")
    rv = lm.run([sample_helm_status_3], expected_result='pods')
    if type(rv) is not list:
        print("Error: plugin should return a list")
    assert(len(rv) == 2)
    print('  OK')

    print("Test 7:")
    rv = lm.run([sample_helm_status_4], expected_result='over_all_status')
    if type(rv) is not list:
        print("Error: plugin should return a list")
    assert(rv == [True])
    print('  OK')

    print("Test 8:")
    rv = lm.run([sample_helm_status_5], expected_result='over_all_status')
    if type(rv) is not list:
        print("Error: plugin should return a list")
    assert(rv == [False])
    print('  OK')
