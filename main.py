import os
import uuid
import json

from azure.storage.blob import BlobServiceClient, ContentSettings, BlobType
from azure.storage.blob import BlobClient

# for InteractiveBrowserCredential
from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential


def get_pending_case() -> []:
    account_url = "https://swltest01.blob.core.windows.net/"

    try:
        # if "WEBSITE_INSTANCE_ID" in os.environ:
        #     credential = DefaultAzureCredential()
        #     # print("---running on Azure---")
        # else:
        #     credential = InteractiveBrowserCredential()
        #     # print("---running locally---")

        credential = DefaultAzureCredential()

        print("check1")
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

        container_pending_exists = blob_service_client.get_container_client("case-info-pending").exists()
        if container_pending_exists:
            container_client_pending = blob_service_client.get_container_client("case-info-pending")
            print("check2")
        else:
            container_client_pending = blob_service_client.create_container("case-info-pending")
            print("check3")

        # container_running_exists = blob_service_client.get_container_client("case-info-running").exists()
        # if container_running_exists:
        #     container_client_running = blob_service_client.get_container_client("case-info-running")
        #     print("check4")
        # else:
        #     container_client_running = blob_service_client.create_container("case-info-running")
        #     print("check5")

        # container_finished_exists = blob_service_client.get_container_client("case-info-finished").exists()
        # if container_finished_exists:
        #     container_client_finished = blob_service_client.get_container_client("case-info-finished")
        #     print("check6")
        # else:
        #     container_client_finished = blob_service_client.create_container("case-info-finished")
        #     print("check7")

        blob_name_pending = "blob-case-info-pending"
        # blob_name_running = "blob-case-info-running"
        # blob_name_finished = "blob-case-info-finished"
        print("check8")

        all_case_info_dict = {"pending_case": {}, "running_case": {}, "finished_case": {}, "all_case": {}}

        # Check if blob exists
        pending_blob_exist = container_client_pending.get_blob_client(blob_name_pending).exists()
        # running_blob_exist = container_client_running.get_blob_client(blob_name_running).exists()
        # finished_blob_exist = container_client_finished.get_blob_client(blob_name_finished).exists()

        if pending_blob_exist:
            # Get blob content as JSON
            print("check9")
            blob_content_pending = container_client_pending.get_blob_client(blob_name_pending).download_blob().readall()
            print("check9-1")
            print(blob_content_pending)
            print(type(blob_content_pending))
            case_info_dict_pending = json.loads(blob_content_pending)
            print("check9-2")
            # all_case_info_dict["pending_case"].append(case_info_dict_pending)
            all_case_info_dict["pending_case"] = case_info_dict_pending
            print("check9-3")
            # all_case_info_dict["all_case"].append(case_info_dict_pending)
            all_case_info_dict["all_case"] = case_info_dict_pending
            print("check9-4")

        else:
            print("check10")

        # if running_blob_exist:
        #     # Get blob content as JSON
        #     print("check11")
        #     blob_content_running = container_client_running.get_blob_client(blob_name_running).download_blob().readall()
        #     case_info_dict_running = json.loads(blob_content_running)
        #     # all_case_info_dict["running_case"].append(case_info_dict_running)
        #     all_case_info_dict["running_case"] = case_info_dict_running
        #     # all_case_info_dict["all_case"].append(case_info_dict_running)
        #     all_case_info_dict["all_case"] = case_info_dict_running
        # else:
        #     print("check12")
        #
        # if finished_blob_exist:
        #     # Get blob content as JSON
        #     print("check13")
        #     blob_content_finished = container_client_finished.get_blob_client(
        #         blob_name_finished).download_blob().readall()
        #     case_info_dict_finished = json.loads(blob_content_finished)
        #     # all_case_info_dict["finished_case"].append(case_info_dict_finished)
        #     all_case_info_dict["finished_case"] = case_info_dict_finished
        #     # all_case_info_dict["all_case"].append(case_info_dict_finished)
        #     all_case_info_dict["all_case"] = case_info_dict_finished
        # else:
        #     print("check14")

        # print(all_case_info_dict)
        pending_case_info_list = all_case_info_dict["pending_case"]["case"]
        print(pending_case_info_list)

        # download blob
        for case in pending_case_info_list:
            container_name = case["case_id"]
            blob_name = "test_" + case["case_target"]
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)




        return pending_case_info_list

    except Exception as ex:
        print('Exception:')
        print(ex)


# def start_analysis(case_list):
#     for case in case_list:
#         print(case["case_id"])
#     blob_client = blob_service_client.get_blob_client(container=container_name, blob="sample-blob.txt")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pending_case_list = get_pending_case()

