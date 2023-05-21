import os
import uuid
import json
import sys

import requests
from azure.storage.blob import BlobServiceClient, ContentSettings, BlobType
from azure.storage.blob import BlobClient

# for InteractiveBrowserCredential
from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential


def check_azure_storage_account_status_and_initialized() -> dict:
    # 初始化一個用來存status的dict
    status_list = {"running_container": False,
                   "finished_container": False,
                   "running_blob": False,
                   "finished_blob": False,
                   }

    account_url = "https://swltest01.blob.core.windows.net/"

    if "WEBSITE_INSTANCE_ID" in os.environ:
        credential = DefaultAzureCredential()
        # print("---running on Azure---")
    else:
        credential = InteractiveBrowserCredential()
    # credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

    container_running_exists = blob_service_client.get_container_client("case-info-running").exists()
    container_finished_exists = blob_service_client.get_container_client("case-info-finished").exists()

    # 將container的status存入dict
    status_list["running_container"] = container_running_exists
    status_list["finished_container"] = container_finished_exists

    blob_name_running = "blob-case-info-running"
    blob_name_finished = "blob-case-info-finished"

    if container_running_exists:
        container_client_running = blob_service_client.get_container_client("case-info-running")
    else:
        # 如果running的container不存在，會創建一個
        container_client_running = blob_service_client.create_container("case-info-running")
    # 將running blob的status存入dict
    running_blob_exist = container_client_running.get_blob_client(blob_name_finished).exists()
    status_list["finished_blob"] = running_blob_exist

    if container_finished_exists:
        container_client_finished = blob_service_client.get_container_client("case-info-finished")
    else:
        # 如果finished的container不存在，會創建一個
        container_client_finished = blob_service_client.create_container("case-info-finished")
    # 將finished blob的status存入dict
    finished_blob_exist = container_client_finished.get_blob_client(blob_name_finished).exists()
    status_list["finished_blob"] = finished_blob_exist

    print("-status_list-")
    print(status_list)
    return status_list


def get_analysis_result(key):
    account_url = "https://swltest01.blob.core.windows.net/"

    if "WEBSITE_INSTANCE_ID" in os.environ:
        credential = DefaultAzureCredential()
        # print("---running on Azure---")
    else:
        credential = InteractiveBrowserCredential()
    # credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    container_client_running = blob_service_client.get_container_client("case-info-running")
    blob_name_running = "blob-case-info-running"
    blob_content_running = container_client_running.get_blob_client(blob_name_running).download_blob().readall()
    case_info_dict_running = json.loads(blob_content_running)
    print(case_info_dict_running)

    case_analysis_ids = [case_info_dict.get('case_analysis_id') for case_info_dict in case_info_dict_running["case"]]
    print(case_analysis_ids)

    # call api
    api_key = key
    url_prefix = "https://www.hybrid-analysis.com/api/v2/report/"
    url_postfix = "/summary"
    user_agent = "Falcon Sandbox"
    headers = {
        "accept": "application/json",
        "User-Agent": user_agent,
        "api-key": api_key
    }
    signature_columns = ["name", "category", "threat_level"]
    if case_analysis_ids:
        for analysis_id in case_analysis_ids:
            url = url_prefix + analysis_id + url_postfix
            print(url)
            response = requests.get(url, headers=headers)
            # # Check response status code
            print(response.status_code)
            if response.status_code == 200 or response.status_code == 201:
                print("success-------")
                print(response.json()["md5"])
            print(type(analysis_id))
            for case in case_info_dict_running["case"]:
                if case["case_analysis_id"] == analysis_id:
                    case["case_analysis_hash_md5"] = response.json()["md5"]
                    case["case_analysis_hash_sha1"] = response.json()["sha1"]
                    case["case_analysis_hash_sha256"] = response.json()["sha256"]
                    case["case_analysis_hash_sha512"] = response.json()["sha512"]
                    case["case_analysis_verdict"] = response.json()["verdict"]
                    case["case_analysis_threat_level"] = response.json()["threat_level"]
                    filtered_signature_list = [{key: item[key] for key in signature_columns} for item in response.json()["signatures"]]
                    case["case_analysis_signatures"] = filtered_signature_list
                    print(filtered_signature_list)
                    print("okay okay")

    # turn status to finished
    for case in case_info_dict_running["case"]:
        print(case)
        case["case_status"] = "finished"
        print(case)
    # print(case_info_dict_running)

    container_finished_exists = blob_service_client.get_container_client("case-info-finished").exists()
    if container_finished_exists:
        container_client_finished = blob_service_client.get_container_client("case-info-finished")
        print("1")
    else:
        container_client_finished = blob_service_client.create_container("case-info-finished")
        print("2")
    blob_name_finished = "blob-case-info-finished"
    finished_blob_exist = container_client_finished.get_blob_client(blob_name_finished).exists()
    if not finished_blob_exist:
        print("3")
        # Create the blob
        blob_client = blob_service_client.get_blob_client(container="case-info-finished", blob=blob_name_finished)
        print("4")
        # initialize case_info_finished_dict
        case_info_finished_dict = {"case": []}
    else:
        print("5")
        # Get the blob client
        blob_client = blob_service_client.get_blob_client(container="case-info-finished", blob=blob_name_finished)
        print("6")
        # read current blob
        blob_content_byte = container_client_finished.get_blob_client(blob_name_finished).download_blob().readall()
        print("7")
        # turn byte to dict -> case_info_finished_dict
        case_info_finished_dict = json.loads(blob_content_byte)
        print("8")
        # delete old blob
        blob_client.delete_blob(delete_snapshots="include")
        print("9")

    for case in case_info_dict_running["case"]:
        case_info_finished_dict["case"].append(case)
    # case_info_finished_dict["case"].append(case_info_dict_running["case"])
    print("10")
    # turn case_info_finished_dict into byte
    case_info_finished_byte = json.dumps(case_info_finished_dict).encode('utf-8')
    print("11")
    # upload blob
    blob_client.upload_blob(case_info_finished_byte)
    print("12")

    # clear running blob
    blob_client_running = blob_service_client.get_blob_client(container="case-info-running", blob=blob_name_running)
    clear_running_blob = {"case": []}
    clear_running_blob_byte = json.dumps(clear_running_blob).encode('utf-8')
    blob_client_running.delete_blob(delete_snapshots="include")
    blob_client_running.upload_blob(clear_running_blob_byte)


def process_parameters(param1, param2):
    # Process the parameters as needed
    print("Parameter 1:", param1)


if __name__ == '__main__':
    param1 = sys.argv[1]
    get_analysis_result(param1)




