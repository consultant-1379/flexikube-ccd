#!/usr/bin/env python


class FilterModule(object):
    def filters(self):
        return {
            'parse_port_addr': self.parse_port_addr,
            'parse_server_addr': self.parse_server_addr
        }

    def ip_kind(self, addr):
        """"
        Checks whether address is valid ipv4 or ipv6 address.
        This function uses standard library functions for
        both python2 and python3 compatibility.
        return values:
            "4" -- if addr is valid IPv4 address
            "6" -- if addr is valid IPv6 address
            "0" -- if addr is an invalid address
        """
        import socket
        try:
            socket.inet_aton(addr)
            return '4'
        except socket.error:
            pass
        try:
            socket.inet_pton(socket.AF_INET6, addr)
            return '6'
        except socket.error:
            pass
        return '0'

    def parse_port_addr(self, fixed_ips_str):
        """
        Function to convert openstack port fixed_ip field to a
        list of ip and subnet pairs.
        Returns: Example return value
            [
              {
                'ip': '10.1.2.3',
                'subnet': 'de6f2bca-321a-4d07-a247-8fd4a9e3a511',
                'ip_version': '4'
              },
              {
                'ip': '2001:db8::6',
                'subnet': '3d4018f2-3e6a-4114-9296-4fd49f690f18',
                'ip_version': '6'
              }
            ]
        Usage:
            From ansible it can be used just like any other filter
            like below:
            - set_fact:
                my_port_ips: >-
                    {{
                        port_show_output.fixed_ip
                        | parse_port_addr
                        | map(attribute='ip')
                    }}
        """
        subnet_list = fixed_ips_str.split('\n')

        result_list = []

        for line in subnet_list:
            ip_str, subnet_str = line.split(', ')
            ip_subnet_list = line.split(', ')

            # Get IP address
            ip_str = ""
            for section in ip_subnet_list:
                if "ip_address=" in section:
                    ip_str = section
                    break
            ip = ip_str.split('ip_address=')[1].strip('\'')

            # Get subnet
            subnet_str = ""
            for section in ip_subnet_list:
                if "subnet_id=" in section:
                    subnet_str = section
                    break
            subnet = subnet_str.split('subnet_id=')[1].strip('\'')

            ip_item = {
                        'ip': ip,
                        'subnet': subnet,
                        'ip_version': self.ip_kind(ip)
                      }

            result_list.append(ip_item)

        result = result_list
        return result

    def parse_server_addr(self, server_addr_str):
        """
        Function to convert openstack server adresses field to a
        list of ips and network pairs.
        Returns: Example return value
            [
              {
                'ip': '10.1.2.3',
                'network': 'de6f2bca-321a-4d07-a247-8fd4a9e3a511',
                'ip_version': '4'
              },
              {
                'ip': '10.100.10.3',
                'network': 'de6f2bca-321a-4d07-a247-8fd4a9e3a511',
                'ip_version': '4'
              },
              {
                'ip': '2001:db8::6',
                'network': '3d4018f2-3e6a-4114-9296-4fd49f690f18',
                'ip_version': '6'
              }
            ]
        Usage:
            From ansible it can be used just like any other filter
            like below:
            - set_fact:
                my_vm_ip4_ips: >-
                    {{
                        server_show_output.addresses
                        | parse_server_addr
                        | selectattr('ip_version', 'equalto', '4')
                        | map(attribute='ip')
                    }}

        """
        result_list = []
        network_list = server_addr_str.split(';')

        for line in network_list:
            net, ips_str = line.split('=')
            net = net.strip()
            ips_str = ips_str.strip()

            ips = ips_str.replace(" ", "").split(',')

            ip_item = [{
                        'ip': ip,
                        'network': net,
                        'ip_version': self.ip_kind(ip)
                       } for ip in ips]

            result_list = result_list + ip_item

        result = result_list
        return result

# ========================================================================
# ======================  Standalone Tests ===============================
# ========================================================================

# Description:
#   Here is a list of some basic tests for securing this ansible filter
#   interface. Make sure to run these tests when changing anything in this
#   filter. Also make sure that these tests are python version agnostic.
# How to run:
#   These tests can be executed by running this file using python2 or python3
#   from command line.
#   > python3 os_addr_parse.py
#   AND
#   > python2 os_addr_parse.py
#


def assert_equal_lists(list1, list2):
    set_list1 = set(tuple(sorted(d.items())) for d in list1)
    set_list2 = set(tuple(sorted(d.items())) for d in list2)
    set_difference = set_list1.symmetric_difference(set_list2)
    if len(set_difference) != 0:
        print(list1)
        print(list2)
    assert len(set_difference) == 0


_filters = FilterModule()

# TEST 1: parse server address: Two addresses on same net
server_addr_str = "oam-net-env-eccd-pioneers-02=10.100.10.18, 10.221.86.207"
real_value = _filters.parse_server_addr(server_addr_str)
expected_value = [
        {
            'ip': '10.100.10.18',
            'network': 'oam-net-env-eccd-pioneers-02',
            'ip_version': '4'
        },
        {
            'ip': '10.221.86.207',
            'network': 'oam-net-env-eccd-pioneers-02',
            'ip_version': '4'
        }
    ]
assert_equal_lists(expected_value, real_value)

# TEST 2: parse server address: Multiple networks with multiple addresses
server_addr_str = "oam-net-env-eccd-pioneers-02=10.100.10.18, 10.221.86.207; \
stack-internal-net=10.100.10.18"
real_value = _filters.parse_server_addr(server_addr_str)
expected_value = [
        {
            'ip': '10.100.10.18',
            'network': 'oam-net-env-eccd-pioneers-02',
            'ip_version': '4'
        },
        {
            'ip': '10.221.86.207',
            'network': 'oam-net-env-eccd-pioneers-02',
            'ip_version': '4'
        },
        {
            'ip': '10.100.10.18',
            'network': 'stack-internal-net',
            'ip_version': '4'
        }
    ]
assert_equal_lists(expected_value, real_value)

# TEST 3: parse server address: Multiple networks with multiple addresses
#                               with mixed ip address versions
server_addr_str = "oam-net-env-eccd-pioneers-02=10.100.10.18, 10.221.86.207,\
2001:db8::6; stack-internal-net=10.100.10.18"
real_value = _filters.parse_server_addr(server_addr_str)
expected_value = [
        {
            'ip': '10.100.10.18',
            'network': 'oam-net-env-eccd-pioneers-02',
            'ip_version': '4'
        },
        {
            'ip': '10.221.86.207',
            'network': 'oam-net-env-eccd-pioneers-02',
            'ip_version': '4'
        },
        {
            'ip': '2001:db8::6',
            'network': 'oam-net-env-eccd-pioneers-02',
            'ip_version': '6'
        },
        {
            'ip': '10.100.10.18',
            'network': 'stack-internal-net',
            'ip_version': '4'
        }
    ]
assert_equal_lists(expected_value, real_value)


# TEST 4: parse port address: Multiple subnets with different IP versions
port_addr_str = "ip_address='10.0.10.2', \
subnet_id='3d4018f2-3e6a-4114-9296-4fd49f690f18'\nip_address='2001:db8::6', \
subnet_id='de6f2bca-321a-4d07-a247-8fd4a9e3a511'"
real_value = _filters.parse_port_addr(port_addr_str)
expected_value = [
        {
            'ip': '10.0.10.2',
            'subnet': '3d4018f2-3e6a-4114-9296-4fd49f690f18',
            'ip_version': '4'
        },
        {
            'ip': '2001:db8::6',
            'subnet': 'de6f2bca-321a-4d07-a247-8fd4a9e3a511',
            'ip_version': '6'
        }
    ]
assert_equal_lists(expected_value, real_value)


# TEST 5: parse port address: Single subnet with single IP
port_addr_str = "ip_address='10.0.10.2', \
subnet_id='3d4018f2-3e6a-4114-9296-4fd49f690f18'"
real_value = _filters.parse_port_addr(port_addr_str)
expected_value = [
        {
            'ip': '10.0.10.2',
            'subnet': '3d4018f2-3e6a-4114-9296-4fd49f690f18',
            'ip_version': '4'
        }
    ]
assert_equal_lists(expected_value, real_value)

print("ALL TESTS PASSED")
