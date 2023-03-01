# YouTube Subscription Importer

_This script is a WIP._

This script allows you to import your YouTube subscriptions into a new account. If you don't like the idea of having to manually subscribe to all your favorite channels again, this script is for you.

## Rate-Limitations

You can only import 200 subscriptions at a time. This is a limitation of the API, not the script. If you're subbed to more than 200 channels, you'll need to run the script every 24 hours(when your 10,000 quota resets) until you've imported all your channels.

For more information, see [YouTube Data API (v3) - Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost#quota).

## Setup

This is assuming you have python installed on your machine. If you don't, you can download it [here](https://www.python.org/downloads/).

1. Fork the repo and install the requirements: `pip install -r requirements.txt`
2. Create a new project in the [Google Developer Console](https://console.developers.google.com/)
3. Enable the YouTube Data API v3 in 'Enabled APIs and Services' -> 'YouTube Data API v3'
4. Setup OAuth consent screen and add both your email addresses as test users
5. Create a new OAuth Client ID and select 'Desktop App' as the application type
6. Download the credentials file and save it as `client_secret.json` in the root of the project
7. Run the script: `python import.py`
8. Follow the instructions in the terminal
9. Enjoy your new account with all your old subscriptions!

## Troubleshooting

If you experience any issues, I would highly recommend switching `reset_script = False` to `reset_script = True` in `import.py` and running the script again. This will query the API for all your subscriptions and re-save them to the JSON files. Otherwise it will use the existing JSON files and the channels saved in them.

1. If you get an error saying `No such file or directory: 'client_secret.json'`, make sure you've downloaded the credentials file and saved it as `client_secret.json` in the root of the project.

## Known Issues

- On some browsers when you try and give the script access to your google account and click 'continue' it will just load forever. If this happens, refresh the page and try again. It has always worked for me on the second try. I'm not sure why this happens on Chrome, but I'm working on a fix 👍
