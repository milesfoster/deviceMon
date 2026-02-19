import json
from insite_plugin import InsitePlugin
from tsAcoMon import DeviceMonitor


class Plugin(InsitePlugin):
    def can_group(self):
        return True

    def fetch(self, hosts):

        try:

            self.collector

        except Exception:

            params = {
                "hosts": hosts,
                "disks": [1, 2]
                }

            self.collector = DeviceMonitor(**params)

        documents = []

        for host, values in self.collector.collect.items():

            document = {"fields": values, "host": host, "name": "tsAco"}
            documents.append(document)

        return json.dumps(documents)