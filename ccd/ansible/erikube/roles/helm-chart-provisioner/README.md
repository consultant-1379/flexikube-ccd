This role is a generic helm chart provisioner. We tried to use:
https://github.com/ansible/ansible/blob/community-content-1/lib/ansible/modules/cloud/misc/helm.py
but pyhelm does not have tar balls installation included.

Input
----------------
::

{{ chart_name }}
    Must be unique
{{ tarball }} # Give url or dir
{{ state }} (installed/purged/update-installed)
(optional) {{ values }}
(optional) {{ kube_namespace }} # Default is 'default'

Example Playbook
----------------
::

- name: Install NAME chart
  include_role:
    name: jedi.helm-chart
  vars:
    - chart_name: NAME
    - tarball: URL # Give url or dir
    - state: update-installed
    - kube_namespace: kube-system
    - values:
      - foo: bar
      - bar: foo

License
-------

Author Information
------------------

Nikolas Hermanns enikher Nikolas.Hermanns@ericsson.com
