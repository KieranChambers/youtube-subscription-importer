import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
# pip install google-api-python-client google-auth python-dotenv
load_dotenv()

# Replace with your client ID and client secret
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Defining the scope for the origin account
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# Defining the scope for the target account
TARGET_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube"
]

reset_script = True


def get_authenticated_service_origin(credentials=None):
    # Get credentials for the origin account
    if not credentials:
        if os.path.exists("tokens/origin_token.json"):
            credentials = Credentials.from_authorized_user_file(
                "tokens/origin_token.json", SCOPES)

        if not credentials or not credentials.valid:
            # If there are no (valid) credentials available, let the user log in.
            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES)
            credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("tokens/origin_token.json", "w") as token:
                token.write(credentials.to_json())

    # Build the YouTube API client for the origin account
    youtube = build("youtube", "v3", credentials=credentials)

    return youtube


def get_origin_subscriptions():
    # If the JSON file exists and the reset_script variable is False, then read the data from the JSON file
    if os.path.exists(
            "subscriptions/origin_subscriptions.json") and not reset_script:
        with open("subscriptions/origin_subscriptions.json", 'r') as json_file:
            subscriptions = json.load(json_file)
            return subscriptions
    else:
        # Get the authenticated YouTube API client for the origin account
        youtube = get_authenticated_service_origin()

        # Get the first page of the list of the origin account's subscriptions
        subscriptions_list_response = youtube.subscriptions().list(
            part="snippet", mine=True, maxResults=50).execute()
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
                subscriptions_list_response = youtube.subscriptions().list(
                    part="snippet",
                    mine=True,
                    maxResults=50,
                    pageToken=next_page_token,
                ).execute()
            else:
                break

        # Write the subscriptions data to the JSON file
        with open("subscriptions/origin_subscriptions.json", 'w') as json_file:
            json.dump(subscriptions, json_file)
        print("Completed getting the origin account's subscriptions")
        return subscriptions


def get_authenticated_service_target(target_credentials=None):
    # Get credentials for the target account
    if not target_credentials:
        if os.path.exists("tokens/target_token.json"):
            target_credentials = Credentials.from_authorized_user_file(
                "tokens/target_token.json", TARGET_SCOPES)

        if not target_credentials or not target_credentials.valid:
            # If there are no (valid) credentials available, let the user log in.
            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", TARGET_SCOPES)
            target_credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("tokens/target_token.json", "w") as token:
                token.write(target_credentials.to_json())

    # Build the YouTube API client for the target account
    target_youtube = build("youtube", "v3", credentials=target_credentials)

    return target_youtube


def get_target_subscriptions():
    # If the JSON file exists and the reset_script variable is False, then read the data from the JSON file
    if os.path.exists(
            "subscriptions/target_subscriptions.json") and not reset_script:
        with open("subscriptions/target_subscriptions.json", 'r') as json_file:
            subscriptions = json.load(json_file)
            return subscriptions
    else:
        # Get the authenticated YouTube API client for the target account
        youtube = get_authenticated_service_target()

        # Get the first page of the list of the target account's subscriptions
        subscriptions_list_response = youtube.subscriptions().list(
            part="snippet", mine=True, maxResults=50).execute()
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
                subscriptions_list_response = youtube.subscriptions().list(
                    part="snippet",
                    mine=True,
                    maxResults=50,
                    pageToken=next_page_token,
                ).execute()
            else:
                break

        # Write the target subscriptions data to the JSON file
        with open("subscriptions/target_subscriptions.json", 'w') as json_file:
            json.dump(subscriptions, json_file)
            print("Completed getting the target account's subscriptions")
        return subscriptions


def remove_duplicates(subscriptions, target_subscriptions):
    # Convert the arrays to sets and get the difference
    if os.path.exists(
            "subscriptions/unique_subscriptions.json") and not reset_script:
        with open("subscriptions/unique_subscriptions.json", 'r') as json_file:
            unique_arr = json.load(json_file)
            return unique_arr
    else:
        unique_origin_subscriptions = set(subscriptions)
        unique_target_subscriptions = set(target_subscriptions)
        unique_set = unique_origin_subscriptions.symmetric_difference(
            unique_target_subscriptions)

        # Convert the set back to a list and sort it
        unique_arr = list(unique_set)
        unique_arr.sort()

        # Write the unique subscriptions data to the JSON file
        with open("subscriptions/unique_subscriptions.json", 'w') as json_file:
            json.dump(unique_arr, json_file)
        return unique_arr


def subscribe_to_channels(unique_subscriptions, length):
    # Build the YouTube API client for the target account
    target_youtube = get_authenticated_service_target()
    # Subscribe to each channel on the target account
    if os.path.exists("subscriptions/unique_subscriptions.json"):
        with open("subscriptions/unique_subscriptions.json", 'r') as json_file:
            unique_subscriptions = json.load(json_file)

    i = 0
    for channel in unique_subscriptions:
        try:
            print(f'Running {i} of {length}')
            target_youtube.subscriptions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "resourceId": {
                            "channelId": channel
                        }
                    }
                },
            ).execute()
            unique_subscriptions.remove(channel)
            i += 1
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Get the subscriptions subscribed to by the origin account
    print('Getting subscriptions from origin account')
    subscriptions = get_origin_subscriptions()

    # Get the subscriptions subscribed to by the target account
    print('Getting subscriptions from target account')
    target_subscriptions = get_target_subscriptions()

    # Remove the subscriptions that are already subscribed to by the target account
    unique_subscriptions = remove_duplicates(subscriptions,
                                             target_subscriptions)
    print(f'Number of new subscriptions to add: {len(unique_subscriptions)}')

    # Subscribe to the subscriptions on the target account
    print('Subscribing to new subscriptions')
    subscribe_to_channels(unique_subscriptions, len(unique_subscriptions))
