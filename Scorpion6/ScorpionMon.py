import copy
import json
from threading import Thread

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

class DeviceMonitor:
    def __init__(self, **kwargs):

        self.hosts = []
        self.types = []
        self.proto = "https"
 
    # Trunk Parameters

        self.rxBitrate = {
            "id": "6004.{0}@i",
            "type": "integer",
            "name": "l_rxBitrate",
        }
        self.rxErrorFrames = {
            "id": "6007.{0}@i",
            "type": "integer",
            "name": "l_rxErrorFrames",
        }

        self.txBitrate = {
            "id": "6011.{0}@i",
            "type": "integer",
            "name": "l_txBitrate",
        }

        self.linkStatus = {
            "id": "6003.{0}@i",
            "type": "integer",
            "name": "s_linkStatus"
        }
        
        self.linkStatusLookup = {
            0: "DOWN",
            1: "UP",
        }

    # ipInputVideo Parameters
        self.vidEnabled = {
            "id": "6050.{0}.{1}@i",
            "type": "integer",
            "name": "s_video_enabled",
        }
        self.videoEnabledStatusLookup = {
            0: "Disabled",
            1: "Enabled",
        }

        self.inputIp = {
            "id": "6052.{0}.{1}@s",
            "type": "string",
            "name": "s_input_ip",
        }

        self.inputPresence = {
            "id": "6054.{0}.{1}@i",
            "type": "integer",
            "name": "s_input_presence",
        }
        self.inputPresenceStatusLookup = {
            0: "Inactive",
            1: "Active",
        }

        self.rxTotal = {
            "id": "6055.{0}.{1}@i",
            "type": "integer",
            "name": "l_rx_total",
        }

        self.rtpSeqErrors = {
            "id": "6061.{0}.{1}@i",
            "type": "integer",
            "name": "i_rtp_seq_errors",
        }

        self.videoPresent = {
            "id": "6201.{0}.{1}@i",
            "type": "integer",
            "name": "s_video_present"
        }
        self.videoPresentLookup = {
            0: "Absent",
            1: "Present"
        }

        self.vidProtectionStatus = {
            "id": "6214.{0}@i",
            "type": "integer",
            "name": "s_video_protection_status"
        }
        self.vidProtectionStatusLookup = {
            0: "Unprotected",
            1: "Protected"
        }

        self.vidActivePath = {
            "id": "6215.{0}@i",
            "type": "integer",
            "name": "s_video_active_path"
        }
        self.vidActivePathLookup = {
            0: "None",
            1: "Trunk 1",
            2: "Trunk 2"
        }



        self.trunkParams = [
            self.rxBitrate,
            self.rxErrorFrames,
            self.txBitrate,
            self.linkStatus
        ]

        self.ipInputVideoParams = [
            self.vidEnabled,
            self.inputIp,
            self.inputPresence,
            self.rxTotal,
            self.rtpSeqErrors,
            self.vidProtectionStatus,
            self.vidActivePath
        ]

        for key, value in kwargs.items():

            if "hosts" in key and value:
                self.hosts.extend(value)

            if "proto" in key and value:
                self.proto = value

            if "trunks" in key and value:
                self.trunkList = []
                self.updateList(value, self.trunkList)
            
            if "inputs" in key and value:
                self.inputs = []
                self.updateList(value, self.inputs)

            if "types" in key and value:
                self.types = value

    def checkProto(self, host):
        param = [self.rxBitrate]
        self.proto = 'https'
        self.parameters = []

        for template in param:
            template_copy = copy.deepcopy(template)
            template_copy["id"] = template_copy["id"].format(str(0))
            self.parameters.append(template_copy)

        results = self.fetch(host, self.parameters)

        if 'refused' in results:
          self.proto = 'http'
             
        else:
          self.proto = 'https'

    def updateList(self, valueIn, listIn: list):

        for item in valueIn:
                if isinstance(item, str) and "-" in item:
                    start, stop = item.split("-")
                    listIn.extend(list(range(int(start), int(stop) + 1)))

                else:

                    listIn.append(item)

    def updateParameters(self, type, listIn, videosChecked):
        self.parameters = []

        if type == "trunk":

            params = self.trunkParams
            for trunk in listIn:
    
                for template in params:
                    template_copy = copy.deepcopy(template)
                    template_copy["id"] = template_copy["id"].format(str(trunk - 1))
                    self.parameters.append(template_copy)

        if type == "ipInputVideo":

            if videosChecked:
                params = self.ipInputVideoParams

            # Check all ENABLED trunks on each Input containing an enabled port for all metrics.
            # Don't check .1 on general params that only use .0
                for input in listIn:
                    for trunk in listIn[input]['enabledTrunks']:

                        for template in params:
                            # if 'active_path' in template["name"] or 'video_protection' in template["name"]:
                            #     if input == '1':
                            #         continue
                            template_copy = copy.deepcopy(template)
                            template_copy["id"] = template_copy["id"].format(str(int(input)), str(trunk))
                            self.parameters.append(template_copy)

            # Check all Trunks on all Inputs for enabled status
            else:
                params = [self.vidEnabled]
                for input in self.inputs:
                    for trunk in self.trunkList:

                        for template in params:
                            template_copy = copy.deepcopy(template)
                            template_copy["id"] = template_copy["id"].format(str(input - 1), str(trunk - 1))
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

                url = "%s://%s/cgi-bin/cfgjsonrpc" % (self.proto, host)

                headers = {
                    "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Cookie": session_id + "; webeasy-loggedin=true",
                }

                response = session.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    verify=False,
                    timeout=15.0,
                )

                return json.loads(response.text)

        except Exception as error:
            return str(error)

    def parse_results(self, host, collection):
        self.checkProto(host)
        print(self.proto)

        host_instance = {host: {}}
        host_instance[host]['trunk'] = {}
        host_instance[host]['ipInputVideo'] = {}

        for type in self.types:

            if type == "trunk":

                self.updateParameters("trunk", self.trunkList, False)
                trunk = host_instance[host]['trunk']
                results = self.fetch(host, self.parameters)
                
                try:

                    for result in results["result"]["parameters"]:

                        key = result["name"]

                        # separate "240.1@i" to "1" or 301.2.0@i to "2"
                        _instance = result["id"].split(".")[1][:1]

                        _instance = int(_instance) + 1

                        if "linkStatus" in result["name"]:
                            result["value"] = self.linkStatusLookup[result["value"]]

                        
                        if _instance not in trunk.keys():

                            trunk.update(
                                {
                                    _instance:
                                        {
                                        key: result["value"],
                                        "i_trunk": _instance,
                                        }
                                }
                            )
                        
                        else:
                            trunk[_instance].update({key: result["value"]})

                except Exception as e:
                    print(e)

            if type == "ipInputVideo":
                bEnabledVideosChecked = False
                _input_prefix = "input_"

                enabledInputs = {}
                ipInputVideo = host_instance[host]['ipInputVideo']

                self.updateParameters("ipInputVideo", enabledInputs, bEnabledVideosChecked)
                enabledResults = self.fetch(host, self.parameters)

                try:

                    for result in enabledResults["result"]["parameters"]:
                        if 'error' in result:
                            return

                        key = result["name"]
                        input_id = result["id"].split(".")[1]

                        trunk_id = result["id"].split(".")[2]
                        trunk_id = trunk_id.split("@")[0]

                        if "video_enabled" in result["name"]:
                            result["value"] = self.videoEnabledStatusLookup[result["value"]]
                            if result["value"] == "Enabled":
                                
                                if input_id not in enabledInputs.keys():

                                    enabledInputs.update(
                                        {
                                            input_id: {}
                                        }
                                    )
                                    enabledInputs[input_id]['enabledTrunks'] = []

                                if enabledInputs[input_id]['enabledTrunks'] != None:
                                    trunkList = enabledInputs[input_id]['enabledTrunks']
                                    if trunk_id not in trunkList:
                                        trunkList.append(trunk_id)
                        
                    bEnabledVideosChecked = True

                except Exception as e:
                    print(e)

                if bEnabledVideosChecked:
                    self.updateParameters("ipInputVideo", enabledInputs, bEnabledVideosChecked)

                    ipInputVideoResults = self.fetch(host, self.parameters)

                    try:
                        for result in ipInputVideoResults["result"]["parameters"]:

                            key = result["name"]

                            if "video_enabled" in result["name"]:
                                result["value"] = self.videoEnabledStatusLookup[result["value"]]

                            if "input_presence" in result["name"]:
                                result["value"] = self.inputPresenceStatusLookup[result["value"]]

                            if "video_present" in result["name"]:
                                result["value"] = self.videoPresentLookup[result["value"]]

                            if "video_protection_status" in result["name"]:
                                result["value"] = self.vidProtectionStatusLookup[result["value"]]
                                trunk_instance = 1
                              
                                if "s_video_protection_status" in ipInputVideo[input_instance][trunk_instance].keys():
                                     trunk_instance = 2
                                else:
                                    trunk_instance = 1


                            elif "video_active_path" in result["name"]:
                                input_id = result["id"].split(".")[1]
                                input_id = input_id.split('@')[0]
                                result["value"] = self.vidActivePathLookup[result["value"]]

                                trunk_instance = 1
                                if "s_video_active_path" in ipInputVideo[input_instance][trunk_instance].keys():
                                     trunk_instance = 2
                                else:
                                    trunk_instance = 1

                            
                            else:
                                input_id = result["id"].split(".")[1]
                                trunk_id = result["id"].split(".")[2]
                                trunk_instance = int(trunk_id.split("@")[0]) + 1
                            
                            input_instance = _input_prefix + (str(int(input_id) + 1))


                            if input_instance not in ipInputVideo.keys():

                                ipInputVideo.update(
                                    {
                                        input_instance: {}
                                    }
                                )


                            if trunk_instance not in ipInputVideo[input_instance].keys():

                                ipInputVideo[input_instance].update(
                                    {
                                        trunk_instance: {
                                            key: result["value"],
                                            "s_input": input_instance,
                                            "s_trunk": trunk_instance
                                        }
                                    }
                                )

                            else:
                                ipInputVideo[input_instance][trunk_instance].update({key: result["value"]})
                        
                    except Exception as e:
                        print(e)

        collection.update(host_instance)

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

        # masterCollection = {}
        # for host in self.hosts:
        #     self.parse_results(host, collection)
        #     masterCollection.update(collection)
        # return masterCollection


def main():

    params = {"hosts": ["172.17.223.110", "172.17.196.51"],
              "trunks": ["1 - 2"],
              "inputs": ["1 - 8"],
              "types": ["trunk", "ipInputVideo"],
    }

    collector = DeviceMonitor(**params)

    inputQuit = False

    while inputQuit is not "q":

        documents = []

        for host, types in collector.collect.items():
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

        print(json.dumps(documents, indent=1))

        inputQuit = input("\nType q to quit or just hit enter: ")


if __name__ == "__main__":
    main()
