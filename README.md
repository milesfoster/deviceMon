## Device Monitor

Device Monitor is designed for the MAGNUM-Analytics Poller application. This poller uses the cfgjsonrpc webeasy program to retrieve data. The metrics collected are primarily focused around MPPM parameters (video presence). Inputs that are not enabled are not collected from to reduce the amount of parameters requested.


The Device Monitor module collects parameters in a similar structure to the WebEasy layout:
    1. Collects QSFP/Dataport Metrics (Part Numbers, RX/TX Power Levels, RX/TX Bitrates, Link Status)
    2. Collects ipInputVideo Metrics (Video Enabled, Input IP, Input Presence, Video Bitrate, Total Bitrate, Video Standard, RTP Presence & Errors)
    3. Metrics collection from each device is threaded to avoid blocking
    4. Values are formatted into human-readable text. These values can be easily used for Data Visualization & notifications.

### Prerequisites

- Magnum-ANALYTICS Version 11 or newer
- Python 3.5.2 or newer (already installed on Analytics HW)
- Python3 Requests Library (already installed on Analytics HW)

### Installation


1. Copy {flavor}Mon.py script to the /pll-1/data/python/modules directory via WinSCP or Command Line:
    ```sh
    cp ipgMon.py /opt/evertz/insite/parasite/applications/pll-1/data/python/modules
    ```

2. Restart the poller application
   ```sh
   git clone https://github.com/github_username/repo_name.git
   ```


### Configuration

1. Once the module has been installed to the correct directory, navigate to the Poller application
2. Click the "+" icon at the top right> Custom Poller to open the poller creation menu
3. Enter a Name, Summary, and any relevant Description info
4. Enter the list of hosts to poll in the Hosts tab
5. In the Input tab, change the type to Python
6. In the Input tab, change the Metric Set Name field to "mppm"
7. From the Python tab, select the Advanced tab and enable the CPython Bindings option
8. Select the Script tab and paste the contents of poller_config.py into the panel.
9. Ensure the device type parameters match the script provided (e.g. "type": "evIPG", or "570ipg" if using the ipgMon variant)
10. Save changes, then restart the poller program

## Under The Hood

- This poller makes several checks along the way to ensure that the correct metrics and representation is used on a device. This is necessary because the evIPG type can represent the same data with different varIDS depending on firmware version & configuration.
    - Writing the poller this way allows users to avoid headaches with maintenance, there is no need to be aware of what cards use what ports nor the nomenclature used to represent ports. Some evIPG's represent ports as QSFP1 or QSFP2, whereas other flavors will use a channel syntax to represent each lane of the QSFP (QSFP1.1, QSFP1.2, QSFP1.3, etc.)

- The checks are:
    - What protocol does this card support for requests, http or https?
    - What QSFP's actually have a valid QSFP present?
    - How does the card represent QSFPs? Channel, or non-channel?
    - How many SDI inputs does this card use?
    - Of those SDI inputs, what SFP's are in use?

These checks allow the module to collect only the necessary information, rather than collecting all data, all the time. This means the requests to the cards contain less parameters & will not fill the database with unneeded info.

There are plans to provide a debug mode in the future that will collect all metrics regardless of enabled status.

## Testing

The ipgMon.py script can be run manually from the terminal using the following command:

```sh
sudo python3 ipgMon.py
```

Example ouput from the terminal:
```sh
[
 {
  "fields": {
   "s_partNumber": "SFP10G-TR13-A",
   "i_port": 1,
   "d_rxPower": -4.06,
   "d_txPower": -1.35
  },
  "host": "10.193.69.111",
  "name": "qsfp"
 },
 {
  "fields": {
   "l_rxBitrate": 1343096,
   "i_port": 1,
   "l_txBitrate": 4028517,
   "s_linkStatus": "UP"
  },
  "host": "10.193.69.111",
  "name": "dataport"
 },
 {
  "fields": {
   "s_video_enabled": "Enabled",
   "s_sdi": "sdi_10",
   "s_sfp": 1,
   "s_input_ip": "239.132.54.211",
   "s_input_presence": "Active",
   "s_rtp_present": "True",
   "i_rtp_seq_errors": 259
  },
  "host": "10.193.69.111",
  "name": "ipInputVideo"
 },
]

```

## Roadmap

- [x] Add Threaded support
- [ ] Include Kibana Objects for import
- [ ] Add parameter categories (ipOutputVideo, ipInputAudio, ipInputAnc, PTP)
- [ ] Update Scorpion-6 support to not require Trunk Port definitions
- [ ] Add a debug/verbose mode to collect all inputs regardless of Enabled status








