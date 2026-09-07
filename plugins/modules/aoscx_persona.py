#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
---
module: aoscx_persona
version_added: "5.0.0"
short_description: Create or delete an AOS-CX interface persona definition.
description:
  - This module creates or deletes a persona definition on AOS-CX. A persona
    definition is the C(interface persona <name>) template object that a port
    can later follow through the M(arubanetworks.aoscx.aoscx_interface_persona)
    module. Once the definition exists, configure its template (VLANs,
    description, MTU, spanning-tree, and so on) with the regular interface
    modules by targeting it with its name.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the persona definition (for example C(iot-access)). This is the
      name referenced by C(persona custom <name>) on a physical interface.
    required: true
    type: str
  state:
    description: >
      Create the persona definition (C(create), idempotent) or delete it
      (C(delete)).
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a persona definition
  arubanetworks.aoscx.aoscx_persona:
    name: iot-access
    state: create

- name: Configure the persona template with the regular interface modules
  arubanetworks.aoscx.aoscx_l2_interface:
    interface: iot-access
    vlan_mode: access
    vlan_access: 300

- name: Delete a persona definition
  arubanetworks.aoscx.aoscx_persona:
    name: iot-access
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from requests.utils import quote

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from pyaoscx.interface import Interface

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )

INTERFACES_URI = "system/interfaces"


def _get_persona(session, name):
    """Return (exists, is_persona) for the given interface name."""
    encoded = quote(name, safe="")
    uri = "{0}/{1}?attributes=name,type,is_persona".format(
        INTERFACES_URI, encoded
    )
    response = session.request("GET", uri)
    if response.status_code == 200:
        data = response.json()
        return True, bool(data.get("is_persona", False))
    return False, False


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        state=dict(
            type="str", default="create", choices=["create", "delete"]
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    name = ansible_module.params["name"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    session = get_pyaoscx_session(ansible_module)

    exists, is_persona = _get_persona(session, name)

    if state == "delete":
        if exists:
            if not is_persona:
                ansible_module.fail_json(
                    msg="Interface '{0}' is not a persona definition; "
                    "refusing to delete it.".format(name)
                )
            if not ansible_module.check_mode:
                encoded = quote(name, safe="")
                uri = "{0}/{1}".format(INTERFACES_URI, encoded)
                response = session.request("DELETE", uri)
                if response.status_code not in (200, 204):
                    ansible_module.fail_json(
                        msg="Failed to delete persona definition '{0}': "
                        "{1}".format(name, response.text)
                    )
            result["changed"] = True
    else:
        if not exists:
            if not ansible_module.check_mode:
                interface = Interface(session, name)
                interface.type = "system"
                interface.is_persona = True
                if "is_persona" not in interface.config_attrs:
                    interface.config_attrs.append("is_persona")
                interface.create()
            result["changed"] = True

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
