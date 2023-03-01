import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


# Loaded from the client_secrets.json file
with open('client_secrets.json', "r") as secrets_json:
    clientSecrets = json.load(secrets_json)
    CLIENT_ID = clientSecrets['installed']['client_id']
    CLIENT_SECRET = clientSecrets['installed']['client_secret']


# Defining the scope for the origin account
ORIGIN_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# Defining the scope for the target account
TARGET_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]

reset_script = False


def get_authenticated_service_origin(credentials=None):
    # Get credentials for the origin account
    if not credentials:
        if os.path.exists("tokens/origin_token.json"):
            credentials = Credentials.from_authorized_user_file(
                "tokens/origin_token.json", ORIGIN_SCOPES
            )

        if not credentials or not credentials.valid:
            # If there are no (valid) credentials available, let the user log in.
            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", ORIGIN_SCOPES
            )
            credentials = flow.run_local_server(
                port=0,
                authorization_prompt_message="Authorization required for the origin account. Opening the browser to authenticate..",
                success_message="Success! Origin account authorized. You may now close the window.",
            )

            # Save the credentials for the next run
            with open("tokens/origin_token.json", "w") as token:
                token.write(credentials.to_json())

    # Build the YouTube API client for the origin account
    youtube = build("youtube", "v3", credentials=credentials)

    return youtube


def get_origin_subscriptions():
    print("Getting subscriptions from origin account..")

    # If the JSON file exists and the reset_script variable is False, then read the data from the JSON file
    if os.path.exists("subscriptions/origin_subscriptions.json") and not reset_script:
        with open("subscriptions/origin_subscriptions.json", "r") as json_file:
            subscriptions = json.load(json_file)
            return subscriptions
    else:
        # Get the authenticated YouTube API client for the origin account
        youtube = get_authenticated_service_origin()

        # Get the first page of the list of the origin account's subscriptions
        subscriptions_list_response = (
            youtube.subscriptions()
            .list(part="snippet", mine=True, maxResults=50)
            .execute()
        )

        subscriptions = []

        # Loop through each page of the list until there are no more items
        while subscriptions_list_response:
            for subscription in subscriptions_list_response.get("items", []):
                subscriptions.append(
                    subscription["snippet"]["resourceId"]["channelId"])

            # Check if there are more items to retrieve
            if "nextPageToken" in subscriptions_list_response:
                next_page_token = subscriptions_list_response["nextPageToken"]

                # Get the next page of the list of subscriptions
                subscriptions_list_response = (
                    youtube.subscriptions()
                    .list(
                        part="snippet",
                        mine=True,
                        maxResults=50,
                        pageToken=next_page_token,
                    )
                    .execute()
                )
            else:
                break

        # Write the subscriptions data to the JSON file
        with open("subscriptions/origin_subscriptions.json", "w") as json_file:
            json.dump(subscriptions, json_file)
        print("Completed getting the origin account's subscriptions")
        return subscriptions


def get_authenticated_service_target(target_credentials=None):

    # Get credentials for the target account
    if not target_credentials:
        if os.path.exists("tokens/target_token.json"):
            target_credentials = Credentials.from_authorized_user_file(
                "tokens/target_token.json", TARGET_SCOPES
            )

        if not target_credentials or not target_credentials.valid:
            # If there are no (valid) credentials available, let the user log in.
            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", TARGET_SCOPES
            )
            target_credentials = flow.run_local_server(
                port=0,
                _DEFAULT_AUTH_PROMPT_MESSAGE="Authorization required for the target account. Opening the browser to authenticate..",
                success_message="Success! Target account authorized. You may now close the window.",
            )

            # Save the credentials for the next run
            with open("tokens/target_token.json", "w") as token:
                token.write(target_credentials.to_json())

    # Build the YouTube API client for the target account
    target_youtube = build("youtube", "v3", credentials=target_credentials)

    return target_youtube


def get_target_subscriptions():
    print("Getting subscriptions from target account..")

    # If the JSON file exists and the reset_script variable is False, then read the data from the JSON file
    if os.path.exists("subscriptions/target_subscriptions.json") and not reset_script:
        with open("subscriptions/target_subscriptions.json", "r") as json_file:
            subscriptions = json.load(json_file)
            return subscriptions
    else:
        # Get the authenticated YouTube API client for the target account
        youtube = get_authenticated_service_target()

        # Get the first page of the list of the target account's subscriptions
        subscriptions_list_response = (
            youtube.subscriptions()
            .list(part="snippet", mine=True, maxResults=50)
            .execute()
        )

        subscriptions = []

        # Loop through each page of the list until there are no more items
        while subscriptions_list_response:
            for subscription in subscriptions_list_response.get("items", []):
                subscriptions.append(
                    subscription["snippet"]["resourceId"]["channelId"])

            # Check if there are more items to retrieve
            if "nextPageToken" in subscriptions_list_response:
                next_page_token = subscriptions_list_response["nextPageToken"]

                # Get the next page of the list of subscriptions
                subscriptions_list_response = (
                    youtube.subscriptions()
                    .list(
                        part="snippet",
                        mine=True,
                        maxResults=50,
                        pageToken=next_page_token,
                    )
                    .execute()
                )
            else:
                break

        # Write the target subscriptions data to the JSON file
        with open("subscriptions/target_subscriptions.json", "w") as json_file:
            json.dump(subscriptions, json_file)
            print("Completed getting the target account's subscriptions")
        return subscriptions


def remove_duplicates(subscriptions, target_subscriptions):
    # Convert the arrays to sets and get the difference
    if os.path.exists("subscriptions/unique_subscriptions.json") and not reset_script:
        with open("subscriptions/unique_subscriptions.json", "r") as json_file:
            unique_arr = json.load(json_file)
            print(
                f"unique_subscriptions.json exists. New subscriptions to add: {len(unique_arr)}")
            return unique_arr
    else:
        unique_origin_subscriptions = set(subscriptions)
        unique_target_subscriptions = set(target_subscriptions)
        unique_set = unique_origin_subscriptions.symmetric_difference(
            unique_target_subscriptions
        )
        if len(unique_set) == 0:
            print("No new subscriptions to add. Exiting.")
            exit()
        else:
            # Convert the set back to a list and sort it
            unique_arr = list(unique_set)
            unique_arr.sort()

            # Write the unique subscriptions data to the JSON file
            with open("subscriptions/unique_subscriptions.json", "w") as json_file:
                json.dump(unique_arr, json_file)
            print(
                f"Created unique_subscriptions.json. New subscriptions to add: {len(unique_arr)}")
            return unique_arr


def subscribe_to_channels(unique_subscriptions, length):
    print('Adding the new subscriptions to the target account')
    # Build the YouTube API client for the target account
    target_youtube = get_authenticated_service_target()
    # Subscribe to each channel on the target account

    with open("subscriptions/unique_subscriptions.json", "r") as json_file:
        unique_subscriptions = json.load(json_file)

    i = 1
    for channel in unique_subscriptions.copy():
        try:
            print(
                f"Running {i} of {length}. Adding {channel} from the Subscriptions.")
            target_youtube.subscriptions().insert(
                part="snippet",
                body={"snippet": {"resourceId": {"channelId": channel}}},
            ).execute()
            # Remove the channel from the list
            unique_subscriptions.remove(channel)
            # Write the unique subscriptions data to the JSON file
            with open("subscriptions/unique_subscriptions.json", "w") as json_file:
                print(f'Removing {channel} from the JSON file.')
                json.dump(unique_subscriptions, json_file)
            i += 1
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Get the subscriptions for the origin account
    subscriptions = get_origin_subscriptions()

    # Get the subscriptions for the target account
    target_subscriptions = get_target_subscriptions()

    # Remove the duplicate subscriptions
    unique_subscriptions = remove_duplicates(
        subscriptions, target_subscriptions)

    # Subscribe to the new channels
    subscribe_to_channels(unique_subscriptions, len(unique_subscriptions))
