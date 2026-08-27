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

## Feedback

Issues and feedback are welcome. Please include the switch platform, firmware
version and the `ansible_aoscx_rest_version` used.
