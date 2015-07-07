#!/usr/bin/env python
"""
Copyright 2015 Brocade Communications Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import logging
import xml.etree.ElementTree as ET

from ncclient import manager
from ncclient import xml_
import ncclient

import pynos.versions.ver_5.ver_5_0_1.bgp
import pynos.versions.ver_5.ver_5_0_1.snmp
import pynos.versions.ver_5.ver_5_0_1.interface
import pynos.versions.ver_5.ver_5_0_1.lldp
import pynos.versions.ver_5.ver_5_0_1.system
import pynos.versions.ver_6.ver_6_0_1.bgp
import pynos.versions.ver_6.ver_6_0_1.snmp
import pynos.versions.ver_6.ver_6_0_1.interface
import pynos.versions.ver_6.ver_6_0_1.lldp
import pynos.versions.ver_6.ver_6_0_1.system

VERSIONS = {
    '5.0.1': {
        'bgp': pynos.versions.ver_5.ver_5_0_1.bgp.BGP,
        'snmp': pynos.versions.ver_5.ver_5_0_1.snmp.SNMP,
        'interface': pynos.versions.ver_5.ver_5_0_1.interface.Interface,
        'lldp': pynos.versions.ver_5.ver_5_0_1.lldp.LLDP,
        'system': pynos.versions.ver_5.ver_5_0_1.system.System,
        },
    '6.0.1': {
        'bgp': pynos.versions.ver_6.ver_6_0_1.bgp.BGP,
        'snmp': pynos.versions.ver_6.ver_6_0_1.snmp.SNMP,
        'interface': pynos.versions.ver_6.ver_6_0_1.interface.Interface,
        'lldp': pynos.versions.ver_6.ver_6_0_1.lldp.LLDP,
        'system': pynos.versions.ver_6.ver_6_0_1.system.System,
        }
    }

NOS_ATTRS = ['bgp', 'snmp', 'interface', 'lldp', 'system']


class DeviceCommError(Exception):
    """
    Error with device communication.
    """
    pass


class Device(object):
    """
    Device object holds the state for a single NOS device.

    Attributes:
        bgp: BGP related actions and attributes.
        interface: Interface related actions and attributes.
        snmp: SNMP related actions and attributes.
    """
    def __init__(self, **kwargs):
        """
        Args:
            conn (tuple): IP/Hostname and port of the VDX device you
                intend to connect to. Ex. ('10.0.0.1', '22')
            auth (tuple): Username and password of the VDX device you
                intend to connect to. Ex. ('admin', 'password')
            hostkey_verify (bool): True to verify hostkey, False to bypass
                verify.
            auth_method (string): ```key``` if using ssh-key auth.
                ```userpass``` if using username/password auth.
            auth_key (string): Location of ssh key to use for authentication.

        Returns:
            Instance of the device object.
        """
        self._conn = kwargs.pop('conn')
        self._auth = kwargs.pop('auth')
        self._hostkey_verify = kwargs.pop('hostkey_verify', None)
        self._auth_method = kwargs.pop('auth_method', 'userpass')
        self._auth_key = kwargs.pop('auth_key', None)
        self._mgr = None

        self.reconnect()

        ver = self.firmware_version

        for nos_attr in NOS_ATTRS:
            setattr(self, nos_attr, VERSIONS[ver][nos_attr](self._callback))

    @property
    def mac_table(self):
        """Returns the MAC table of the device.

        Args:

        Returns:

        Raises:

        Examples:
        """
        pass

    @property
    def firmware_version(self):
        """
        Returns firmware version.

        Args:
            None

        Returns:
            Dictionary

        Raises:
            None
        """
        namespace = "urn:brocade.com:mgmt:brocade-firmware-ext"

        request_ver = ET.Element("show-firmware-version", xmlns=namespace)

        ver = self._callback(request_ver, handler='get')
        return ver.find('.//*{%s}os-version' % namespace).text

    def _callback(self, call, handler='edit_config', target='running',
                  source='startup'):
        """
        Callback for NETCONF calls.

        Args:
            call: An Element Tree element containing the XML of the NETCONF
                call you intend to make to the device.
            handler: Type of ncclient call to make.
                get: ncclient dispatch. For custom RPCs.
                edit_config: NETCONF standard edit.
                delete_config: NETCONF standard delete.
                copy_config: NETCONF standard copy.
            target: Target configuration location for action. Only used for
                edit_config, delete_config, and copy_config.
            source: Source of configuration information for copying
                configuration. Only used for copy_config.

        Returns:
            None

        Raises:
            None
        """
        try:
            call = ET.tostring(call)
            if handler == 'get':
                call_element = xml_.to_ele(call)
                return ET.fromstring(str(self._mgr.dispatch(call_element)))
            if handler == 'edit_config':
                self._mgr.edit_config(target=target, config=call)
            if handler == 'delete_config':
                self._mgr.delete_config(target=target)
            if handler == 'copy_config':
                self._mgr.copy_config(target=target, source=source)
        except (ncclient.transport.TransportError,
                ncclient.transport.SessionCloseError,
                ncclient.transport.SSHError,
                ncclient.transport.AuthenticationError,
                ncclient.transport.SSHUnknownHostError) as error:
            logging.error(error)
            raise DeviceCommError

    @property
    def connection(self):
        """
        Poll if object is still connected to device in question.

        Args:
            None

        Returns:
            bool: True if connected, False if not.

        Raises:
            None
        """
        return self._mgr.connected

    def reconnect(self):
        """
        Reconnect session with device.

        Args:
            None

        Returns:
            bool: True if reconnect succeeds, False if not.

        Raises:
            None
        """
        if self._auth_method is "userpass":
            self._mgr = manager.connect(host=self._conn[0],
                                        port=self._conn[1],
                                        username=self._auth[0],
                                        password=self._auth[1],
                                        hostkey_verify=self._hostkey_verify)
        elif self._auth_method is "key":
            self._mgr = manager.connect(host=self._conn[0],
                                        port=self._conn[1],
                                        kay_filename=self._auth_key,
                                        hostkey_verify=self._hostkey_verify)
        else:
            raise ValueError("auth_method incorrect value.")
        self._mgr.timeout = 600

        return True

    def find_interface_by_mac(self, **kwargs):
        """Find the interface through which a MAC can be reached.

        Args:

        Returns:

        Raises:

        Examples:
        """
        pass