import os
import sys
import time
import json
import queue
import threading
import datetime
import subprocess
import shutil

import pandas as pd
import calculate_new
import matlab.engine
import position

#Uncomment line below for local debug of packages
sys.path.append(r"../unpi")
sys.path.append(r"../rtls")
sys.path.append(r"../rtls_util")

from rtls_util import RtlsUtil, RtlsUtilLoggingLevel, RtlsUtilException, RtlsUtilTimeoutException, \
    RtlsUtilNodesNotIdentifiedException, RtlsUtilScanNoResultsException

headers = ['pkt', 'sample_idx', 'rssi', 'ant_array', 'channel', 'i', 'q']
TABLE = None
POST_ANALYZE_FILE_LIST = set()


def get_date_time():
    return datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")


def get_csv_file_name_for(identifier, conn_handle, with_date=True):
    data_time = get_date_time()
    logging_file_path = os.path.join(os.path.curdir, os.path.basename(__file__).replace('.py', '_log'))

    if not os.path.isdir(logging_file_path):
        os.makedirs(logging_file_path)

    identifier = identifier.lower().replace(":", "")
    if with_date:
        filename = "iq_data.csv"
        #filename = os.path.join(logging_file_path, f"{data_time}_rtls_raw_iq_samples_{identifier}_{conn_handle}.csv")
    else:
        filename = "iq_data.csv"
        #filename = os.path.join(logging_file_path, f"rtls_raw_iq_samples_{identifier}_{conn_handle}.csv")
    return filename


## User function to proces
def results_parsing(q):
    global TABLE, POST_ANALYZE_FILE_LIST
    pkt_count = 0

    while True:
        try:
            data = q.get(block=True, timeout=0.5)
            if isinstance(data, dict):
                data_time = datetime.datetime.now().strftime("[%m:%d:%Y %H:%M:%S:%f] :")

                if 'type' in data and data['type'] == "RTLS_CMD_AOA_RESULT_RAW":
                    if TABLE is None:
                        TABLE = pd.DataFrame(columns=headers)

                    identifier = data["identifier"]
                    connHandle = data['payload']['connHandle']
                    channel = int(data['payload']['channel'])
                    offset = int(data['payload']['offset'])
                    rssi = data['payload']['rssi']
                    antenna = data['payload']['antenna']
                    samplesLength = data['payload']["samplesLength"]

                    for indx, sample in enumerate(data['payload']['samples']):
                        sample_idx = offset + indx
                        sample_i = sample['i']
                        sample_q = sample['q']

                        row = {
                            'pkt': 0,
                            'sample_idx': sample_idx,
                            'rssi': rssi,
                            'ant_array': antenna,
                            'channel': channel,
                            'i': sample_i,
                            'q': sample_q
                        }
                        TABLE = TABLE.append(row, ignore_index=True)

                    df_by_channel = TABLE.loc[TABLE['channel'] == channel]

                    if len(df_by_channel) == samplesLength:
                        df_by_channel = df_by_channel.sort_values(by=['sample_idx'])
                        df_by_channel.loc[:, "pkt"] = df_by_channel.loc[:, "pkt"].replace(to_replace=0, value=pkt_count)

                        csv_file_name = get_csv_file_name_for(identifier, connHandle, with_date=False)
                        POST_ANALYZE_FILE_LIST.add(csv_file_name)

                        if os.path.isfile(csv_file_name):
                            df_by_channel.to_csv(csv_file_name, mode='a', index=False, header=False)
                        else:
                            df_by_channel.to_csv(csv_file_name, index=False)
                        print(f"{data_time} Added new set of IQ into {csv_file_name}")

                        pkt_count += 1
                        TABLE = TABLE.loc[TABLE['channel'] != channel]

                else:
                    print(f"{data_time} {json.dumps(data)}")

            elif isinstance(data, str) and data == "STOP":
                print("STOP Command Received")

                for entry in list(POST_ANALYZE_FILE_LIST)[:]:
                    date_time = get_date_time()
                    file_name = os.path.basename(entry)
                    dir_name = os.path.dirname(entry)
                    new_entry = os.path.abspath(os.path.join(dir_name, f"{file_name}"))
                    #new_entry = os.path.abspath(os.path.join(dir_name, f"{date_time}_{file_name}"))
                    os.rename(entry, new_entry)
                    POST_ANALYZE_FILE_LIST.remove(entry)
                    POST_ANALYZE_FILE_LIST.add(new_entry)

                break
            else:
                pass
        except queue.Empty:
            continue


def aoa_post_analyze(selected_ant=16):
    global POST_ANALYZE_FILE_LIST
    aoa_exe_path = os.path.abspath("../rtls_ui/aoa/aoa.exe")
    support_files_ant1 = os.path.abspath("../rtls_ui/aoa/support_files/Ant1")
    support_files_ant2 = os.path.abspath("../rtls_ui/aoa/support_files/Ant2")

    if os.path.isfile(aoa_exe_path):
        if len(POST_ANALYZE_FILE_LIST) > 0:
            for fp in POST_ANALYZE_FILE_LIST:
                dir_name = os.path.splitext(fp)[0]
                if selected_ant >= 32:
                    shutil.copytree(support_files_ant2, dir_name)
                else:
                    shutil.copytree(support_files_ant1, dir_name)

                shutil.copy2(fp, dir_name)
                csv_file = os.path.join(dir_name, os.path.basename(fp))

                print("----------------------------------------------------------------------------\n")
                print(f"Analyzing file : {fp}")

                print("\nAlgorithm : Algo1")
                output = subprocess.check_output(
                    f'{aoa_exe_path} --pct_file {csv_file} --algo algo1 --search_speed fast').decode()
                output = output.replace('\r\n', '\r\n\t\t')
                print(output)

                print("\nAlgorithm : Algo2")
                output = subprocess.check_output(
                    f'{aoa_exe_path} --pct_file {csv_file} --algo algo2 --search_speed fast').decode()
                output = output.replace('\r\n', '\r\n\t\t')
                print(output)

                print("----------------------------------------------------------------------------\n")


## Main Function
def main():
    ## Predefined parameters
    slave_bd_addr = None  # "80:6F:B0:1E:38:C3" # "54:6C:0E:83:45:D8"
    scan_time_sec = 5
    connect_interval_mSec = 100

    ## Angle of Arival Demo Enable / Disable
    aoa = True
    th_aoa_results_parsing = None
    aoa_params = None

    ## Taking python file and replacing extension from py into log for output logs + adding data time stamp to file
    data_time = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    logging_file_path = os.path.join(os.path.curdir, os.path.basename(__file__).replace('.py', '_log'))
    if not os.path.isdir(logging_file_path):
        os.makedirs(logging_file_path)
    logging_file = os.path.join(logging_file_path, f"{data_time}_{os.path.basename(__file__).replace('.py', '.log')}")

    ## Initialize RTLS Util instance
    rtlsUtil = RtlsUtil(logging_file, RtlsUtilLoggingLevel.INFO)
    ## Update general time out for all action at RTLS Util [Default timeout : 30 sec]
    rtlsUtil.timeout = 5

    all_nodes = []
    try:
        devices = [
            {"com_port": "COM4", "baud_rate": 460800, "name": "CC26x2 Master"},
            # {"com_port": "COM29", "baud_rate": 460800, "name": "CC26x2 Passive"}
        ]
        ## Setup devices
        master_node, passive_nodes, all_nodes = rtlsUtil.set_devices(devices)
        print(f"Master : {master_node} \nPassives : {passive_nodes} \nAll : {all_nodes}")

        ## Reset devices for initial state of devices
        rtlsUtil.reset_devices()
        print("Devices Reset")

        ## Code below demonstrates two option of scan and connect
        ## 1. Then user know which slave to connect
        ## 2. Then user doesn't mind witch slave to use
        if slave_bd_addr is not None:
            print(f"Start scan of {slave_bd_addr} for {scan_time_sec} sec")
            scan_results = rtlsUtil.scan(scan_time_sec, slave_bd_addr)
            print(f"Scan Results: {scan_results}")

            rtlsUtil.ble_connect(slave_bd_addr, connect_interval_mSec)
            print("Connection Success")
        else:
            print(f"Start scan for {scan_time_sec} sec")
            scan_results = rtlsUtil.scan(scan_time_sec)
            print(f"Scan Results: {scan_results}")

            rtlsUtil.ble_connect(scan_results[0], connect_interval_mSec)
            print("Connection Success")

        ## Start angle of arrival feature
        if aoa:
            if rtlsUtil.is_aoa_supported(all_nodes):
                aoa_params = {
                    "aoa_run_mode": "AOA_MODE_RAW",  ## AOA_MODE_ANGLE, AOA_MODE_PAIR_ANGLES, AOA_MODE_RAW
                    "aoa_cc26x2": {
                        "aoa_slot_durations": 2,
                        "aoa_sample_rate": 1,
                        "aoa_sample_size": 1,
                        "aoa_sampling_control": int('0x10', 16), #0x11
                        ## bit 0   - 0x00 - default filtering, 0x01 - RAW_RF no filtering,
                        ## bit 4,5 - default: 0x10 - ONLY_ANT_1, optional: 0x20 - ONLY_ANT_2
                        "aoa_sampling_enable": 1,
                        "aoa_pattern_len": 3,
                        "aoa_ant_pattern": [0, 1, 2]
                    }
                }
                rtlsUtil.aoa_set_params(aoa_params)
                print("AOA Paramas Set")

                ## Setup thread to pull out received data from devices on screen
                th_aoa_results_parsing = threading.Thread(target=results_parsing, args=(rtlsUtil.aoa_results_queue,))
                th_aoa_results_parsing.setDaemon(True)
                th_aoa_results_parsing.start()
                print("AOA Callback Set")

                rtlsUtil.aoa_start(cte_length=20, cte_interval=1)
                print("AOA Started")
            else:
                print("=== Warring ! One of the device not supporting AOA functionality ===")

        ## Sleep code to see in the screen receives data from devices
        timeout_sec = 5
        print("Going to sleep for {} sec".format(timeout_sec))
        timeout = time.time() + timeout_sec
        while timeout >= time.time():
            time.sleep(0.01)

        if aoa and rtlsUtil.is_aoa_supported(all_nodes):
            rtlsUtil.aoa_results_queue.put("STOP")
            print("Try to stop AOA result parsing thread")
            if th_aoa_results_parsing:
                th_aoa_results_parsing.join()

            rtlsUtil.aoa_stop()
            print("AOA Stopped")

        if rtlsUtil.ble_connected:
            rtlsUtil.ble_disconnect()
            print("Master Disconnected")

    except RtlsUtilNodesNotIdentifiedException as ex:
        print(f"=== ERROR: {ex} ===")
        print(ex.not_indentified_nodes)
    except RtlsUtilTimeoutException as ex:
        print(f"=== ERROR: {ex} ===")
    except RtlsUtilException as ex:
        print(f"=== ERROR: {ex} ===")
    finally:
        rtlsUtil.done()
        print("Done")

        print("Executing analyze on results")

        angle1 = position.estimate_angle()   ################################################
        position.send_angle(angle1)    

        if aoa_params:
            aoa_post_analyze(aoa_params['aoa_cc26x2']['aoa_sampling_control'])
        else:
            aoa_post_analyze()
    
    


if __name__ == '__main__':
    main()
