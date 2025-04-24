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
        self.proto = "https"
        self.types = []

        self.bChannels = ""

        self.QSFP_list = []
        self.activeChannels = []
        self.sdi = []

        self.bEnabledVideosChecked = None

    # System Parameters
        self.partNum = {
            "id": "76.{0}@s",
            "type": "string",
            "name": "s_partNumber",
        }

        self.qsfpType = {
            "id": "73.{0}@s",
            "type": "string",
            "name": "s_qsfpType",
       }

        self.rxPower = {
            "id": "71.{0}@i",
            "type": "integer",
            "name": "d_rxPower",
        }

        self.txPower = {
            "id": "72.{0}@i",
            "type": "integer",
            "name": "d_txPower",
        }

        self.rxBitrate = {
            "id": "80.{0}@i",
            "type": "integer",
            "name": "l_rxBitrate",
        }

        self.txBitrate = {
            "id": "86.{0}@i",
            "type": "integer",
            "name": "l_txBitrate",
        }

        # 0 is Up, 1 is Down
        self.linkStatus = {
            "id": "92.{0}@i",
            "type": "integer",
            "name": "s_linkStatus"
        }
        
        self.linkStatusLookup = {
            0: "DOWN",
            1: "UP",
        }

    # ipInputVideo Parameters
        self.vidEnabled = {
            "id": "130.{0}.{1}@i",
            "type": "integer",
            "name": "s_video_enabled",
        }

        self.inputIp = {
            "id": "131.{0}.{1}@s",
            "type": "string",
            "name": "s_input_ip",
        }

        self.inputPresence = {
            "id": "160.{0}.{1}@i",
            "type": "integer",
            "name": "s_input_presence",
        }

        self.videoBitrate = {
            "id": "161.{0}.{1}@s",
            "type": "integer",
            "name": "l_video_bitrate",
        }

        self.rxTotal = {
            "id": "216.{0}.{1}@i",
            "type": "integer",
            "name": "l_rx_total",
        }

        self.videoStandard = {
            "id": "162.{0}.{1}@s",
            "type": "string",
            "name": "s_video_standard",
        }

        self.rtpPresence = {
            "id": "163.{0}.{1}@i",
            "type": "integer",
            "name": "s_rtp_present",
        }

        self.rtpSeqErrors = {
            "id": "229.{0}.{1}@i",
            "type": "integer",
            "name": "i_rtp_seq_errors",
        }

        self.inputPresenceStatusLookup = {
            0: "Inactive",
            1: "Active",
        }

        self.rtpPresenceStatusLookup = {
            0: "False",
            1: "True",
        }

        self.videoEnabledStatusLookup = {
            0: "Disabled",
            1: "Enabled",
        }
        
    # PTP Parameters
        self.active_ptp = {
            "id": "875.0@i",
            "type": "integer",
            "name": "s_active_ptp",
        }
        self.ptp_status = {
            "id": "852.0@i",
            "type": "integer",
            "name": "s_ptp_status",
        }
        self.master_identity = {
            "id": "828.0@s",
            "type": "string",
            "name": "s_master_identity",
        }
        self.grandmaster_identity = {
            "id": "827.0@s",
            "type": "string",
            "name": "s_grandmaster_identity",
        }
        self.active_ptp_lookup = {
            0: "Main",
            1: "Backup",
        }
        self.ptp_status_lookup = {
            0: "Absent",
            1: "Un-Converged",
            2: "Converged",
        }

        self.qsfpParams = [
            self.partNum,
            self.rxPower,
            self.txPower
        ]

        self.dataPortParams = [
            self.rxBitrate,
            self.txBitrate,
            self.linkStatus
        ]

        self.ipInputVideoParams = [
            self.vidEnabled,
            self.inputIp,
            self.inputPresence,
           # self.videoBitrate,
           # self.rxTotal,
           # self.videoStandard,
            self.rtpPresence,
            self.rtpSeqErrors,
        ]

        self.parameters = []

        for key, value in kwargs.items():

            if "hosts" in key and value:
                self.hosts.extend(value)

            if "proto" in key and value:
                self.proto = value
            
            if "deviceType" in key and value:
                self.deviceType = value

            if "types" in key and value:
                self.types = value

    def checkProto(self, host):
        param = [self.partNum]
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

    def updateParameters(self, **kwargs):
        self.parameters = []

        for key, value in kwargs.items():
            if "type" in key and value:
                type = value

            if "bEnabledVideosChecked" in key and len(str(value)) > 0:
                bVideosChecked = value

            if "bChannels" in key and len(str(value)) > 0:
                bChannels = value

            if "qsfpList" in key and value:
                qsfpList = value
            
            if "activeChannels" in key and value:
                channelList = value
            
            if "sdiList" in key and value:
                sdiList = value

            if "enabledSDI" in key and value:
                enabledSDI = value

            if "activePorts" in key and value:
                activePorts = value

        if type == "qsfp":

            params = self.qsfpParams
            for qsfp in qsfpList:
    
                for template in params:
                    template_copy = copy.deepcopy(template)
                    template_copy["id"] = template_copy["id"].format(str(qsfp))
                    self.parameters.append(template_copy)

        if type == "dataport":
            params = self.dataPortParams

            # Channels are already 0-based, no need to -1. 
            # Unfortunately, channel format is inconsistent among Firmware versions.
            # SDI 1-8 will use <some>.0.0 and .0.1
            # SDI 9-16 will use <some>.9.2 and .9.3 for the same parameters on a different SDI because the organization is broken.

            for channel in channelList:

                for template in params:
                    template_copy = copy.deepcopy(template)
                    template_copy["id"] = template_copy["id"].format(str(channel))

                    self.parameters.append(template_copy)
                    

        if type == "ipInputVideo":

            if bVideosChecked:
                params = self.ipInputVideoParams
                if bChannels:
                    
                    for sdi in enabledSDI: #ENABLED SDI
                        for port in enabledSDI[sdi]['enabledPorts']:
                            port = int(port)

                            match sdi:
                                    
                                case sdi if sdi in range(9, 17):
                                    port+=2
                                
                                case sdi if sdi in range(17, 25):
                                    port+=4

                                case sdi if sdi in range(25, 33):
                                    port+=6

                            for template in params:
                                template_copy = copy.deepcopy(template)
                                template_copy["id"] = template_copy["id"].format(str(sdi), str(port))
                                self.parameters.append(template_copy)


                else:
                # Check all ENABLED ports on each SDI containing an enabled port for all video metrics.
                    for sdi in enabledSDI: #ENABLED SDI
                        for port in enabledSDI[sdi]['enabledPorts']:

                            for template in params:
                                template_copy = copy.deepcopy(template)
                                template_copy["id"] = template_copy["id"].format(str(int(sdi)), str(port))
                                self.parameters.append(template_copy)

            # Check all ports on all SDI for enabled status
            else:
                if bChannels:
                    params = [self.vidEnabled]
                    for sdi in sdiList: #self.sdi list

                        for port in activePorts: #activePorts list
                            port = int(port)

                            match sdi:
                                    
                                case sdi if sdi in range(9, 17):
                                    port+=2
                                
                                case sdi if sdi in range(17, 25):
                                    port+=4

                                case sdi if sdi in range(25, 33):
                                    port+=6

                            for template in params:
                                template_copy = copy.deepcopy(template)
                                template_copy["id"] = template_copy["id"].format(str(sdi - 1), str(port))
                                self.parameters.append(template_copy)

                else:
                    params = [self.vidEnabled]
                    for sdi in sdiList:
                        for port in activePorts:

                            for template in params:
                                template_copy = copy.deepcopy(template)
                                template_copy["id"] = template_copy["id"].format(str(sdi - 1), str(port))
                                self.parameters.append(template_copy)


    def checkQSFP(self, host):
        self.parameters = []
        ports = ['1 - 12']
        formattedPorts = []
        self.updateList(ports, formattedPorts)
        totalQsfpList = []
        qsfpList = []

        for port in formattedPorts:
            template_copy = copy.deepcopy(self.qsfpType)
            template_copy["id"] = template_copy["id"].format(str(port - 1))
            self.parameters.append(template_copy)

        results = self.fetch(host, self.parameters)

        for result in results['result']['parameters']:
            if ('error' in result) or (len(str(result['value'])) == 0):
                continue

            else:
              if(result['value']):
                if 'unknown' in result['value']:
                  _instance = (result["id"].split(".")[1])
                  _instance = int(_instance.split("@")[0])
                  totalQsfpList.append(_instance)
                  continue

                else:
                   _instance = (result["id"].split(".")[1])
                   _instance = int(_instance.split("@")[0])
                   qsfpList.append(_instance)
                   totalQsfpList.append(_instance)

        return qsfpList, totalQsfpList


    def checkChannels(self, host, qsfpList):
        self.parameters = []
        if self.deviceType == 'evIPG':
            lastPort = int(qsfpList[-1])
        elif self.deviceType == '570ipg':
            lastPort = 12

        template_copy = copy.deepcopy(self.rxBitrate)
        template_copy["id"] = template_copy["id"].format(str(lastPort + 1))
        self.parameters.append(template_copy)

        results = self.fetch(host, self.parameters)

        if 'error' in results:
          return False
        else:

          for result in results['result']['parameters']:
              print(lastPort + 1)
              if 'error' in result:
               if "Failed to retrieve data." in result['error']['message']:
                 return False
             
              else:
                 return True
             
    def checkSDI(self, host):
        self.parameters = []
        sdiList = []
        
        template_copy = copy.deepcopy(self.vidEnabled)
        template_copy["id"] = template_copy["id"].format(str(16), str(0))
        self.parameters.append(template_copy)

        results = self.fetch(host, self.parameters)

        for result in results['result']['parameters']:
            if 'error' in result:
             if "Failed to retrieve data." in result['error']['message']:
                 self.updateList(["1 - 16"], sdiList) 
             
            else:
                self.updateList(["1 - 32"], sdiList) 
            
            return sdiList

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
        host_instance[host]['qsfp'] = {}
        host_instance[host]['dataport'] = {}
        host_instance[host]['ipInputVideo'] = {}
        


        for type in self.types:

            if type == "qsfp":
                qsfpList, totalQsfpList = self.checkQSFP(host)
                if qsfpList:
                    params = {
                        'type': 'qsfp',
                        'qsfpList': qsfpList
                    }
                    print(qsfpList, 'qsfpList')
                    print(totalQsfpList, 'totalqsfplist')
                    


                    self.updateParameters(**params)

                    qsfp = host_instance[host]['qsfp']

                    results = self.fetch(host, self.parameters)

                    
                    try:
                        activePorts = []

                        for result in results["result"]["parameters"]:
                            key = result["name"]

                            # separate "240.1@i" to "1" or 301.2.0@i to "2"
                            _instance = result["id"].split(".")[1]

                            _instance = _instance.split("@")[0]

                            if "partNum" in result["name"] and len(result["value"]) != 0:
                                result["value"] = result["value"].rstrip()
                                activePorts.append(_instance)

                            if _instance in activePorts:

                                if "Power" in result["name"]:
                                    result["value"] = result["value"] / 100

                                _instance = int(_instance) + 1
                                
                                if _instance not in qsfp.keys():

                                    qsfp.update(
                                        {
                                            _instance:
                                                {
                                                key: result["value"],
                                                "i_port": _instance,
                                                }
                                        }
                                    )
                                
                                else:
                                    qsfp[_instance].update({key: result["value"]})

                    except Exception as e:
                        print(e)
                else:
                    break
                    

            if type == "dataport":

                bChannels = self.checkChannels(host, totalQsfpList)
                channelNames = []
                activeChannels = []
                if bChannels:

                    channelCounter = 0

                    for port in activePorts:
                        for x in range(4):
                            channelNames.append(f'{port}.{channelCounter + 1}')
                            channelCounter+=1

                    for x in range(channelCounter):
                        activeChannels.append(str(x))
                    
                    params = {
                        'type': 'dataport',
                        'activeChannels': activeChannels
                    }
                    
                    self.updateParameters(**params)

                else:
                    for port in activePorts:
                        channelNames.append(port)
                    
                    params = {
                        'type': 'dataport',
                        'activeChannels': activePorts
                    }
                    self.updateParameters(**params)

                dataport = host_instance[host]['dataport']

                results = self.fetch(host, self.parameters)


                try:
                    for result in results["result"]["parameters"]:
                        key = result["name"]

                        # separate "240.1@i" to "1" or 301.2.0@i to "2"
                        _instance = result["id"].split(".")[1][:1]

                        # upconvert base 0 to base 1
                        _instance = int(_instance) + 1

                        # perform lookup link status enum
                        if "linkStatus" in result["name"]:
                            result["value"] = self.linkStatusLookup[result["value"]]
                        
                        if _instance not in dataport.keys():

                            dataport.update(
                                {
                                    _instance:
                                        {
                                        key: result["value"],
                                        "i_port": _instance,
                                        }
                                }
                            )
                        
                        else:
                            dataport[_instance].update({key: result["value"]})

                    # host_instance.update()

                except Exception as e:
                    print(e)

            if type == "ipInputVideo":
                bEnabledVideosChecked = False
                sdiList = self.checkSDI(host)

                _sdi_prefix = "sdi_"
            
                enabledSDI = {}
                ipInputVideo = host_instance[host]['ipInputVideo']
                # Need list of x.y to make parameters regardless of if channels are enabled

                params = {
                    'type': 'ipInputVideo',
                    'sdiList': sdiList,
                    'bEnabledVideosChecked': bEnabledVideosChecked,
                    'bChannels': bChannels,
                    'activePorts': activePorts
                }

                self.updateParameters(**params)

                enabledResults = self.fetch(host, self.parameters)

                try:

                    for result in enabledResults["result"]["parameters"]:
                        if 'error' in result:
                            return
                        

                        key = result["name"]
                        sdi_id = result["id"].split(".")[1]
                        qsfp_id = result["id"].split(".")[2]
                        qsfp_id = qsfp_id.split("@")[0]

                        if "video_enabled" in result["name"]:
                            result["value"] = self.videoEnabledStatusLookup[result["value"]]
                            if result["value"] == "Enabled":
                                
                                if sdi_id not in enabledSDI.keys():

                                    enabledSDI.update(
                                        {
                                            sdi_id: {}
                                        }
                                    )
                                    enabledSDI[sdi_id]['enabledPorts'] = []

                                if enabledSDI[sdi_id]['enabledPorts'] != None:
                                    portList = enabledSDI[sdi_id]['enabledPorts']
                                    if qsfp_id not in portList:
                                        portList.append(qsfp_id)
                             
                        
                    bEnabledVideosChecked = True

                except Exception as e:
                    print(e)

                if bEnabledVideosChecked:
                    if enabledSDI:

                        params = {
                            'type': 'ipInputVideo',
                            'bEnabledVideosChecked': bEnabledVideosChecked,
                            'bChannels': bChannels,
                            'enabledSDI': enabledSDI,
                        }

                        self.updateParameters(**params)
                        ipInputVideoResults = self.fetch(host, self.parameters)

                        try:

                            if self.deviceType == "evIPG":
                                prefix = "s_qsfp"
                                
                            elif self.deviceType == "570ipg":
                                prefix = "s_sfp"

                            for result in ipInputVideoResults["result"]["parameters"]:

                                key = result["name"]

                                if "video_enabled" in result["name"]:
                                    result["value"] = self.videoEnabledStatusLookup[result["value"]]

                                if "input_presence" in result["name"]:
                                    result["value"] = self.inputPresenceStatusLookup[result["value"]]

                                if "rtp_present" in result["name"]:
                                    result["value"] = self.rtpPresenceStatusLookup[result["value"]]

                                sdi_id = result["id"].split(".")[1]
                                qsfp_id = result["id"].split(".")[2]

                                sdi_instance = _sdi_prefix + (str(int(sdi_id) + 1))
                                qsfp_instance = int(qsfp_id.split("@")[0]) + 1



                                if sdi_instance not in ipInputVideo.keys():

                                    ipInputVideo.update(
                                        {
                                            sdi_instance: {}
                                        }
                                    )

                                if bChannels:
                                    sdi_id = int(sdi_id) + 1

                                    match sdi_id:

                                        case sdi_id if sdi_id in range(1, 9):
                                            channel = 1
                                            channel_qsfp_instance = f'{qsfp_instance}.{channel}'
                                            
                                        case sdi_id if sdi_id in range(9, 17):
                                            qsfp_instance-=2
                                            channel = 2
                                            channel_qsfp_instance = f'{qsfp_instance}.{channel}'
                                        
                                        case sdi_id if sdi_id in range(17, 25):
                                            qsfp_instance-=4
                                            channel = 3
                                            channel_qsfp_instance = f'{qsfp_instance}.{channel}'

                                        case sdi_id if sdi_id in range(25, 33):
                                            qsfp_instance-=6
                                            channel = 4
                                            channel_qsfp_instance = f'{qsfp_instance}.{channel}' 

                                else:
                                    channel_qsfp_instance = qsfp_instance   

                                if qsfp_instance not in ipInputVideo[sdi_instance].keys():

                                    ipInputVideo[sdi_instance].update(
                                        {
                                            qsfp_instance: {
                                                key: result["value"],
                                                "s_sdi": sdi_instance,
                                                prefix: channel_qsfp_instance
                                            }
                                        }
                                    )

                                else:

                                    ipInputVideo[sdi_instance][qsfp_instance].update({key: result["value"]})
                                        
                        except Exception as e:
                            print(e)
                            
                    else:
                        continue


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

def main():

    params = {"hosts": ["10.193.67.22", "10.193.77.126"], 
              "deviceType": "evIPG",
              "types": ["qsfp", "dataport", "ipInputVideo"],
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
