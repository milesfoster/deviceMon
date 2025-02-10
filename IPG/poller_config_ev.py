import json
from insite_plugin import InsitePlugin
from ipgMon import DeviceMonitor


class Plugin(InsitePlugin):
    def can_group(self):
        return True

    def fetch(self, hosts):

        try:

            self.collector

        except Exception:

            params = {"hosts": hosts,
                      "deviceType": "evIPG",
                      "types": ["qsfp", "dataport", "ipInputVideo"]}

            self.collector = DeviceMonitor(**params)

        documents = []

        for host, types in self.collector.collect.items():
            for key, item in types.items():
                for prop, value in item.items():

                    if key == 'ipInputVideo':
                        # Nested one deeper than the General params

                        for _, sdi in value.items():
                            document = {"fields": sdi, "host": host, "name": key}

                            documents.append(document)

                    else:
                        # General params are nested inside first layer of host
                        
                        document = {"fields": value, "host": host, "name": key}

                        documents.append(document)

        return json.dumps(documents)