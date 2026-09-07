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
module: aoscx_interface_persona
version_added: "5.0.0"
short_description: Configure the persona of an AOS-CX interface.
description:
  - This module configures the persona (the C(system/interfaces) persona
    object) of an AOS-CX interface, letting a port follow an C(access) or
    C(uplink) role, or a user-defined C(custom) persona.
author: Aruba Networks (@ArubaNetworks)
options:
  interface:
    description: Name of the interface to configure (for example C(1/1/5)).
    required: true
    type: str
  config:
    description: >
      Persona role applied to the interface. C(access) for an access port,
      C(uplink) for an uplink port, or C(custom) to apply a user-defined
      persona (see the C(custom) option).
    required: false
    type: str
    choices:
      - access
      - uplink
      - custom
  custom:
    description: >
      User-defined persona value, applied when I(config) is C(custom). Between
      1 and 64 characters.
    required: false
    type: str
  mode:
    description: >
      How the persona is applied. C(attach) keeps the interface configuration
      following its persona, C(copy) applies the persona configuration once.
    required: false
    type: str
    choices:
      - attach
      - copy
  state:
    description: Configure or reset (clear) the interface persona.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Apply the access persona to a port
  arubanetworks.aoscx.aoscx_interface_persona:
    interface: 1/1/5
    config: access
    mode: attach
    state: create

- name: Apply a custom persona
  arubanetworks.aoscx.aoscx_interface_persona:
    interface: 1/1/6
    config: custom
    custom: tenant-blue
    mode: copy
    state: create

- name: Clear the interface persona
  arubanetworks.aoscx.aoscx_interface_persona:
    interface: 1/1/5
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )

PERSONA_FIELDS = ("config", "custom", "mode")


def main():
    module_args = dict(
        interface=dict(type="str", required=True),
        config=dict(
            type="str", default=None,
            choices=["access", "uplink", "custom"],
        ),
        custom=dict(type="str", default=None),
        mode=dict(type="str", default=None, choices=["attach", "copy"]),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[("config", "custom", ["custom"])],
    )

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    name = ansible_module.params["interface"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    session = get_pyaoscx_session(ansible_module)
    device = Device(session)
    interface = device.interface(name)

    current = getattr(interface, "persona", None)
    if not isinstance(current, dict):
        current = {}

    if state == "delete":
        new_persona = {}
    else:
        supplied = {
            key: ansible_module.params[key]
            for key in PERSONA_FIELDS
            if ansible_module.params[key] is not None
        }
        new_persona = dict(current)
        new_persona.update(supplied)

    changed = new_persona != current
    if changed:
        interface.persona = new_persona
        if "persona" not in interface.config_attrs:
            interface.config_attrs.append("persona")
        if not ansible_module.check_mode:
            interface.apply()

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
