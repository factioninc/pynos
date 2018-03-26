"""
Copyright 2015 Brocade Communications Systems, Inc.

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
import xml.etree.ElementTree as ET

class SystemMonitor(object):
    """
    SystemMonitor class containing all VCS Fabric system monitor methods and attributes.
    """

    def __init__(self, callback):
        """SystemMonitor init method.

        Args:
            callback: Callback function that will be called for each action.

        Returns:
            SystemMonitor Object

        Raises:
            None
        """
        self._callback = callback

    @property
    def system_monitors(self):
        """dict: system monitor details
        """

        rbridge_id = 'all'
        namespace = 'urn:brocade.com:mgmt:brocade-system-monitor-ext'

        get_system_monitor = ET.Element('show-system-monitor', xmlns=namespace)
        rbridge = ET.SubElement(get_system_monitor,
                                         "rbridge-id")
        rbridge.text = rbridge_id
        monitor_results = self._callback(get_system_monitor, handler='get')
        results = []
        for item in monitor_results.findall('.//{%s}switch-status' % namespace):
            components = []
            switch_name = item.find('.//{%s}switch-name' % namespace).text
            switch_state = item.find('.//{%s}switch-state' % namespace).text
            switch_rbridge_id = item.find('.//{%s}rbridge-id-out' % namespace).text
            switch_state_reason = item.find('.//{%s}switch-state-reason' % namespace).text
            for comp in item.findall('.//{%s}component-status' % namespace):
                component_name = comp.find('.//{%s}component-name' % namespace).text
                component_state = comp.find('.//{%s}component-state' % namespace).text
                component = {
                    'component-name': component_name,
                    'component-state': component_state
                }
                components.append(component)
            result = {
                'switch-name': switch_name,
                'switch-rbridge-id': switch_rbridge_id,
                'switch-state': switch_state,
                'switch-state-reason': switch_state_reason,
                'components': components
            }
            results.append(result)
        return results
