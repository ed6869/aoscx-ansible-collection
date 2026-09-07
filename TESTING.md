# Testing the `arubanetworks.aoscx` collection (integration branch)

> **Note:** `testing/all` is a throwaway **integration/testing** branch that
> combines every in-progress feature into a single tree so it can be exercised
> end to end. It is **not** intended for production or for upstream merge. Each
> feature is submitted upstream as its own scoped pull request.

## Prerequisites

- Python 3.9+
- `ansible-core >= 2.19.10`
- Network reachability to the switch REST API (HTTPS)

## Installation

Both the collection and the matching `pyaoscx` SDK are installed from Git:

```bash
# 1) pyaoscx SDK (all resource classes + REST v10.13 / v10.16 version modules)
pip install "git+https://github.com/ed6869/pyaoscx.git@testing/all"

# 2) the Ansible collection
ansible-galaxy collection install \
  "git+https://github.com/ed6869/aoscx-ansible-collection.git,testing/all" --force
```

> The collection calls the `pyaoscx` SDK, so the two `testing/all` branches must
> be installed together.

## Example inventory (`inventory.ini`)

```ini
[aoscx]
switch ansible_host=10.0.0.1

[aoscx:vars]
ansible_connection=arubanetworks.aoscx.aoscx
ansible_network_os=arubanetworks.aoscx.aoscx
ansible_user=admin
ansible_password=CHANGE_ME
ansible_aoscx_validate_certs=false
ansible_aoscx_rest_version=10.09
```

## REST API version

- `10.09` is a safe default and covers most modules.
- Some newer features require a more recent REST API version. To reach them,
  set the version **in the inventory** (`ansible_aoscx_rest_version=10.16`) or
  pass it as an **extra variable** on the command line
  (`-e ansible_aoscx_rest_version=10.16`).

  > The `aoscx` connection plugin reads this value from the inventory/extra
  > vars; setting it in a play-level `vars:` block does **not** override it.

  REST v10.16 is required to reach, for example:
  - client probe profiles, IP-SLA track objects, DHCP snooping client event log
  - IPFIX, Traffic Insight, MACsec/MKA policies, SNMP community/view
- The switch must support the requested version (visible at `https://<switch>/rest`).

## Example playbook (`demo.yml`)

```yaml
---
- name: aoscx demo
  hosts: aoscx
  gather_facts: false
  tasks:
    - name: Gather facts (including VSF stacking)
      arubanetworks.aoscx.aoscx_facts:
        gather_subset:
          - host_name
          - software_version
          - stacking
      register: facts

    - name: Show facts
      ansible.builtin.debug:
        var: facts.ansible_facts

    - name: Create a test VLAN
      arubanetworks.aoscx.aoscx_vlan:
        vlan_id: 400
        name: DEMO
        state: create

    - name: Delete the test VLAN
      arubanetworks.aoscx.aoscx_vlan:
        vlan_id: 400
        state: delete
```

Run it:

```bash
export ANSIBLE_COLLECTIONS_PATH=~/.ansible/collections
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.ini demo.yml
```

## Modules available in this branch

`testing/all` stacks every in-progress feature into one tree, so it adds many
new modules on top of the released collection. They are grouped by domain
below. The **Feature branch** column is the scoped branch (a future upstream
pull request) each module comes from, so you can trace a module back to its
source. Modules marked *(modified)* extend an existing collection module.

### AAA / RADIUS / TACACS

| Module | Feature branch |
| --- | --- |
| `aoscx_aaa` | `feature/aaa-global` |
| `aoscx_aaa_accounting` | `feature/aaa-accounting` |
| `aoscx_aaa_server_group` | `feature/aaa` |
| `aoscx_aaa_server_group_prio` | `feature/aaa-server-group-prio` |
| `aoscx_tacacs_server` | `feature/aaa` |
| `aoscx_radius_server` | `feature/aaa` |
| `aoscx_radius_config_attribute` | `feature/radius-config-attribute` |
| `aoscx_radius_dynamic_authorization` | `feature/radius-dynauth` |
| `aoscx_radius_dynamic_authorization_client` | `feature/radius-dynauth` |
| `aoscx_radius_dynauth_proxy_client_group` | `feature/radius-dynauth-proxy` |
| `aoscx_radius_dynauth_proxy_profile` | `feature/radius-dynauth-proxy` |
| `aoscx_radius_dynauth_proxy_server` | `feature/radius-dynauth-proxy` |
| `aoscx_radius_proxy_client_group` | `feature/radius-proxy` |
| `aoscx_radius_proxy_profile` | `feature/radius-proxy` |

### Port access / NAC / 802.1X

| Module | Feature branch |
| --- | --- |
| `aoscx_port_access` | `feature/port-access-global` |
| `aoscx_port_access_interface` | `feature/port-access-interface` |
| `aoscx_port_access_auth` | `feature/port-access-auth` |
| `aoscx_port_access_role` | `feature/port-access` |
| `aoscx_port_access_policy` | `feature/port-access` |
| `aoscx_port_access_abp` | `feature/port-access` |
| `aoscx_port_access_gbp` | `feature/port-access` |
| `aoscx_port_access_cdp_group` | `feature/port-access-device-groups` |
| `aoscx_port_access_lldp_group` | `feature/port-access-device-groups` |
| `aoscx_port_access_vlan_group` | `feature/port-access` |
| `aoscx_captive_portal_profile` | `feature/port-access` |
| `aoscx_class` | `feature/port-access` |

### Persona

| Module | Feature branch |
| --- | --- |
| `aoscx_persona` (create/delete the definition) | `feature/interface-persona` |
| `aoscx_interface_persona` (apply to a port) | `feature/interface-persona` |

The persona definition is a regular interface object, so its template
(VLANs, description, STP, port-access/802.1X, ...) is configured with the
existing interface modules by targeting it with its name.

### Interface / STP

| Module | Feature branch |
| --- | --- |
| `aoscx_stp` | `feature/stp` |
| `aoscx_interface_stp` | `feature/interface-stp` |
| `aoscx_interface_ipfix` | `feature/interface-ipfix` |
| `aoscx_interface` *(modified)* | `feature/interface-physical`, `feature/client-probe`, `feature/pvlan` |

### VLAN / L2 security

| Module | Feature branch |
| --- | --- |
| `aoscx_dhcp_snooping` | `feature/dhcp-snooping` |
| `aoscx_dhcpv4_snooping_guard` | `feature/dhcp-snooping-guard` |
| `aoscx_dhcpv6_snooping_guard` | `feature/dhcp-snooping-guard` |
| `aoscx_ipv6_destination_guard` | `feature/dhcp-snooping-guard` |
| `aoscx_static_ip_binding` | `feature/dhcp-snooping-guard` |
| `aoscx_vlan` *(modified)* | `feature/arp-inspection`, `feature/dhcp-snooping`, `feature/pvlan` |

### Routing / policy

| Module | Feature branch |
| --- | --- |
| `aoscx_bgp_aspath_list` | `feature/aoscx_bgp_aspath_list` |
| `aoscx_bgp_community_list` | `feature/aoscx_bgp_community_list` |
| `aoscx_prefix_list` | `feature/aoscx_prefix_list` |
| `aoscx_route_map` | `feature/aoscx_route_map` |
| `aoscx_pbr_action_list` | `feature/aoscx_pbr_action_list` |

### EVPN / VXLAN

| Module | Feature branch |
| --- | --- |
| `aoscx_evpn` | `feature/evpn` |
| `aoscx_evpn_vlan` | `feature/evpn` |
| `aoscx_evpn_vlan_aware_bundle` | `feature/evpn-vlan-aware-bundle` |
| `aoscx_vni` | `feature/aoscx_vni`, `feature/vni-vtep-peers` |
| `aoscx_vxlan_interface` | `feature/vxlan-interface` |

### Telemetry / monitoring

| Module | Feature branch |
| --- | --- |
| `aoscx_ipfix_flow_exporter` | `feature/ipfix` |
| `aoscx_ipfix_flow_monitor` | `feature/ipfix` |
| `aoscx_ipfix_flow_record` | `feature/ipfix` |
| `aoscx_sflow` | `feature/sflow` |
| `aoscx_sflow_collector` | `feature/sflow` |
| `aoscx_traffic_insight` | `feature/traffic-insight` |
| `aoscx_traffic_insight_monitor` | `feature/traffic-insight` |
| `aoscx_mirror` | `feature/mirror` |
| `aoscx_mirror_endpoint` | `feature/mirror` |
| `aoscx_snmp_community` | `feature/snmp` |
| `aoscx_snmp_trap` | `feature/snmp` |
| `aoscx_snmp_view` | `feature/snmp` |
| `aoscx_snmpv3_user` | `feature/snmp` |

### IP-SLA

| Module | Feature branch |
| --- | --- |
| `aoscx_ipsla_responder` | `feature/ipsla` |
| `aoscx_ipsla_source` | `feature/ipsla` |
| `aoscx_ipsla_track_object` | `feature/ipsla` |

### MACsec

| Module | Feature branch |
| --- | --- |
| `aoscx_keychain` | `feature/macsec` |
| `aoscx_macsec_policy` | `feature/macsec` |
| `aoscx_mka_policy` | `feature/macsec` |

### Services / system

| Module | Feature branch |
| --- | --- |
| `aoscx_ntp_key` | `feature/ntp` |
| `aoscx_ntp_server` | `feature/ntp` |
| `aoscx_syslog_remote` | `feature/syslog` |
| `aoscx_user` | `feature/users` |
| `aoscx_dhcp_relay` | `feature/aoscx_dhcp_relay` |
| `aoscx_udp_bcast_forwarder` | `feature/aoscx_udp_bcast_forwarder` |
| `aoscx_app_recognition` | `feature/app-recognition` |
| `aoscx_client_probe` | `feature/client-probe` |
| `aoscx_facts` *(modified: VSF stacking)* | `feature/facts-vsf` |
| `aoscx_checkpoint` *(modified: auto checkpoint)* | `feature/checkpoint-auto` |

> Some modules appear in more than one feature branch because those branches
> are stacked (built on top of each other). The table lists the branch that
> owns each module's scoped pull request.

## Feedback

Issues and feedback are welcome. Please include the switch platform, firmware
version and the `ansible_aoscx_rest_version` used.
