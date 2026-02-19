import copy
import json
from threading import Thread

import requests
import urllib3

# if disk ID is a thing, do some other stuff to make all the values have DISK1, disk2 prefix
    
class DeviceMonitor:
    def __init__(self, **kwargs):

        self.hosts = []
        self.proto = "http"
        self.types = []
        self.disks = []

    # Parameters
        self.logToRam = {
            "id": "2120.0@i",
            "type": "integer",
            "name": "s_logToRam",
        }
        
        self.logToRamLookup = {
            0: "Not Running",
            1: "Running",
        }

        self.cpuUsage = {
            "id": "1401.0",
            "type": "integer",
            "name": "i_cpuUsage",
        }

        self.memoryUsage = {
            "id": "1402.0",
            "type": "integer",
            "name": "l_MemoryUsage",
        }

        self.memoryTotal = {
            "id": "1404.0",
            "type": "integer",
            "name": "l_totalMemory",
        }

        self.memoryFree = {
            "id": "1405.0",
            "type": "integer",
            "name": "l_freeMemory",
        }

        self.memoryBuffers = {
            "id": "1406.0",
            "type": "integer",
            "name": "l_memoryBuffers",
        }

        self.memoryCached = {
            "id": "1407.0",
            "type": "integer",
            "name": "l_cachedMemory",
        }

        self.diskName = {
            "id": "1600.{0}@s",
            "type": "string",
            "name": "s_DiskName"
        }

        self.diskTotalSpace = {
            "id": "1601.{0}@s",
            "type": "integer",
            "name": "i_totalDiskSpace"
        }

        self.diskAvailableSpace = {
            "id": "1602.{0}@s",
            "type": "integer",
            "name": "i_availableDiskSpace"
        }

        self.folderName = {
            "id": "1700.0@s",
            "type": "string",
            "name": "s_logFolderName"
        }

        self.folderUsedSpace = {
            "id": "1702.0@s",
            "type": "string",
            "name": "l_folderUsedSpace"
        }

        for key, value in kwargs.items():

            if "hosts" in key and value:
                self.hosts.extend(value)

            if "proto" in key and value:
                self.proto = value
            
            if "disks" in key and value:
                self.disks.extend(value)

        self.parameters = []

        for template in [
            self.logToRam,
            self.cpuUsage,
            self.memoryFree,
            self.memoryTotal,
            self.diskName,
            self.diskAvailableSpace,
            self.diskTotalSpace,
            self.folderName,
            self.folderUsedSpace
        ]:
            
            if "Disk" in template['name']:
                for disk in self.disks:
                    template_copy = copy.deepcopy(template)
                    template_copy["id"] = template_copy["id"].format(str(disk - 1))
                    self.parameters.append(template_copy)
            
            else:
                template_copy = copy.deepcopy(template)
                self.parameters.append(template_copy)

    def fetch(self, host, parameters):

        try:

            with requests.Session() as session:

                ## get the session ID from accessing the login.php site
                resp = session.get(
                    "%s://%s/login.php" % (self.proto, host),
                    verify=False,
                    timeout=15.0,
                )

                session_id = resp.headers["Set-Cookie"].split(";")[0]

                payload = {
                    "jsonrpc": "2.0",
                    "method": "get",
                    "params": {"parameters": parameters},
                    "id": 1,
                }

                url = "%s://%s/3480fr/cgi-bin/cfgjsonrpc" % (self.proto, host)

                headers = {
                    "Content-type": "application/json",
                    "Cookie": session_id + "; webeasy-loggedin=true",
                }

                response = session.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    verify=False,
                    timeout=15.0,
                )
                print(response.text, 'response')
                return json.loads(response.text)

        except Exception as error:
            return str(error)


    def parse_results(self, host, collection):

        host_instance = {host: {}}    
        results = self.fetch(host, self.parameters)

        try:
            for result in results["result"]["parameters"]:
                key = result['name']
                value = result['value']


                # perform logToRam lookup 
                if "s_logToRam" in result["name"]:
                    value = self.logToRamLookup[result["value"]]

                if "Memory" in result["name"]:
                    value = result['value'] * 1000000

                # handle multiple disks
                if "Disk" in result["name"]:

                    # separate "240.1" to "1" or 301.2.0 to "2"
                    _instance = result["id"].split(".")[1][:1]
                    # upconvert base 0 to base 1
                    _instance = str(int(_instance) + 1)
                    
                    key = result['name'] + '_disk' + _instance

                if "folderUsedSpace" in result["name"]:
                    value = int(result['value'])


                if key not in host_instance[host].keys():
                    host_instance[host].update(
                                {
                                key: value
                                }

                    )
                
                else:
                    host_instance[host].update({key: value})

            collection.update(host_instance)

        except Exception as e:
            print(e)

    @property
    def collect(self):

        collection = {}

        threads = [
            Thread(target=self.parse_results, args=(host, collection,)) for host in self.hosts
        ]

        for x in threads:
            x.start()

        for y in threads:
            y.join()
        return collection
    
def main():

    params = {"hosts": ["172.16.157.101", "172.16.168.23"], "disks": [1, 2]}

    collector = DeviceMonitor(**params)

    inputQuit = False

    while inputQuit is not "q":

        documents = []

        for host, values in collector.collect.items():

            document = {"fields": values, "host": host, "name": "tsAco"}
            documents.append(document)


        print(json.dumps(documents, indent=1))

        inputQuit = input("\nType q to quit or just hit enter: ")


if __name__ == "__main__":
    main()