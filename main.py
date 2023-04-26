import os
import uuid
import json

from azure.storage.blob import BlobServiceClient, ContentSettings, BlobType
from azure.storage.blob import BlobClient

# for InteractiveBrowserCredential
from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    account_url = "https://swltest01.blob.core.windows.net/"
    # if not isinstance(queryset, QuerySet):
    #     raise ValueError("queryset argument must be a Django queryset")

    # for cache
    # cache_key = 'case_info_query_set'
    # cached_query_set = cache.get(cache_key)
    # if cached_query_set is not None:
    #     return cached_query_set

    try:
        if "WEBSITE_INSTANCE_ID" in os.environ:
            credential = DefaultAzureCredential()
            # print("---running on Azure---")
        else:
            credential = InteractiveBrowserCredential()
            # print("---running locally---")

        print("check1")
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

        container_pending_exists = blob_service_client.get_container_client("case-info-pending").exists()
        if container_pending_exists:
            container_client_pending = blob_service_client.get_container_client("case-info-pending")
            print("check2")
        else:
            container_client_pending = blob_service_client.create_container("case-info-pending")
            print("check3")

        container_running_exists = blob_service_client.get_container_client("case-info-running").exists()
        if container_running_exists:
            container_client_running = blob_service_client.get_container_client("case-info-running")
            print("check4")
        else:
            container_client_running = blob_service_client.create_container("case-info-running")
            print("check5")

        container_finished_exists = blob_service_client.get_container_client("case-info-finished").exists()
        if container_finished_exists:
            container_client_finished = blob_service_client.get_container_client("case-info-finished")
            print("check6")
        else:
            container_client_finished = blob_service_client.create_container("case-info-finished")
            print("check7")

        blob_name_pending = "blob-case-info-pending"
        blob_name_running = "blob-case-info-running"
        blob_name_finished = "blob-case-info-finished"
        print("check8")
        all_case_info_dict = {"pending_case": {}, "running_case": {}, "finished_case": {}, "all_case": {}}

        # Check if blob exists
        pending_blob_exist = container_client_pending.get_blob_client(blob_name_pending).exists()
        running_blob_exist = container_client_running.get_blob_client(blob_name_running).exists()
        finished_blob_exist = container_client_finished.get_blob_client(blob_name_finished).exists()

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

        if running_blob_exist:
            # Get blob content as JSON
            print("check11")
            blob_content_running = container_client_running.get_blob_client(blob_name_running).download_blob().readall()
            case_info_dict_running = json.loads(blob_content_running)
            # all_case_info_dict["running_case"].append(case_info_dict_running)
            all_case_info_dict["running_case"] = case_info_dict_running
            # all_case_info_dict["all_case"].append(case_info_dict_running)
            all_case_info_dict["all_case"] = case_info_dict_running
        else:
            print("check12")

        if finished_blob_exist:
            # Get blob content as JSON
            print("check13")
            blob_content_finished = container_client_finished.get_blob_client(
                blob_name_finished).download_blob().readall()
            case_info_dict_finished = json.loads(blob_content_finished)
            # all_case_info_dict["finished_case"].append(case_info_dict_finished)
            all_case_info_dict["finished_case"] = case_info_dict_finished
            # all_case_info_dict["all_case"].append(case_info_dict_finished)
            all_case_info_dict["all_case"] = case_info_dict_finished
        else:
            print("check14")

        print(all_case_info_dict)
        # if not all_case_info_dict["all_case"]:
        #     print("check15")
        #     queryset = queryset.none()
        #     cache.set(cache_key, queryset)
        #     return queryset

        # Use case_info_dict to filter queryset, if needed
        # For example, assuming case_info_dict has a list of case IDs
        # print(all_case_info_dict["all_case"]["case"])
        # case_ids = all_case_info_dict["all_case"]["case"].get('case_id', [])
        # case_ids = [case_info_dict.get('case_id') for case_info_dict in all_case_info_dict["all_case"]["case"]]
        # print(case_ids)
        # queryset = queryset.filter(case_id__in=case_ids)

        # print("xxxxx")
        # print(queryset)
        # print("xxxxx")

        # for cache
        # cache.set(cache_key, queryset)

    except Exception as ex:
        print('Exception:')
        print(ex)

    # return queryset


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
