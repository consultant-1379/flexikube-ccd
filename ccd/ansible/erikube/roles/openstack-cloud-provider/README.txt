###################################
# Variables for cloud configuration
###################################

# Currently openstack_auth_url is used for enabling openstack cloud provider
# Cinder is also using the same variable as enabler

openstack_ca_cert: <string>
openstack_ca_cert_path: <string>

#All these variables are strings
# <Ansible_variable_name> # <os_provisioner_cloud_config_name>
#[Global]
openstack_auth_url      # auth-url
openstack_user_id       # user-id
openstack_username      # username
openstack_user_password # password
openstack_trust_id      # trust-id
openstack_project_id    # tenant-id
openstack_project_name  # tenant-name
openstack_domain_id     # domain-id
openstack_domain_name   # domain-name
openstack_region        # region
openstack_ca_cert       # ca-file

#[LoadBalancer]
openstack_lb_version              # lb-version
openstack_use_octavia             # use-octavia
openstack_subnet_id               # subnet-id
openstack_floating_network_id     # floating-network-id
openstack_lb_method               # lb-method
openstack_lb_provider             # lb-provider
openstack_create_monitor          # create-monitor
openstack_monitor_delay           # monitor-delay
openstack_monitor_timeout         # monitor-timeout
openstack_monitor_max_retries     # monitor-max-retries
openstack_manage_security_groups  # manage-security-groups


#[BlockStorage]
openstack_bs_version        # bs-version
openstack_trust_device_path # trust-device-path
openstack_ignore_volume_az  # ignore-volume-az
