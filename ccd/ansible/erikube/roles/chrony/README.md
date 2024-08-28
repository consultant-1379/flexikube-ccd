---
# Jedi Role: Chrony

Installs a simple chrony service for RHEL/CentOS or Debian/Ubunty systems.

After the role is run, a `chronyd` init service will be available on the server, this will be used for ntp. You can use `service chronyd [start|stop|restart|status]` to control the service.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

    chrony_pkg_state: 'present'
    chrony_service_state: 'started'
    chrony_service_enabled: 'yes'

    chrony_config_server: [ '0.pool.ntp.org', '1.pool.ntp.org', '2.pool.ntp.org', '3.pool.ntp.org' ]
    chrony_config_logdir: '/var/log/chrony'

## Dependencies

None.

## Example Playbook

    - hosts: server
      vars_files:
        - vars/main.yml
      roles:
        - { role: jedi.chrony }

*Inside `vars/main.yml`*:

    chrony_service_name: chronyd
    chrony_config_location: /etc/chrony.conf
    chrony_config_driftfile: /var/lib/chrony/drift
    chrony_config_keyfile: /etc/chrony.keys
