To get this working, you first need the appropriate Python libraries (can run `sudo pip install -r requirements.txt`, sudo not needed if installing to a virtualenv)

Then you also need to generate a google token. You can follow the guide [here](https://developers.google.com/drive/web/quickstart/quickstart-python#step_1_enable_the_drive_api).

Basically, you need to create a project, then generate client id and client secret, and put those in your homedir (whatever comes back when you run `python -c 'import os; print os.path.expanduser("~")'`) in a file called `hunttools.conf` (you can copy and modify the one in the repo):

```
[gdrive]
client_id = <client_id>
client_secret = <client_secret>
```

You should also enable the Google Drive ([guide](https://developers.google.com/drive/web/enable-sdk#enable_the_drive_api)) and URL Shortener APIs ([guide](https://developers.google.com/url-shortener/v1/getting_started#auth)).

Then you can run `./gdrive_api.py` to grab and save the token you'll use for all your api requests. It will save your credentials to a file called `gdrive_creds` in your home directory.

You also need to grab the slack token, probably from [here](https://api.slack.com/web#auth). And add that to `hunttools.conf` like this:
    
```
[slack]
token = <token>
```

Then you should be able to call
```
./prep_puzzle.py 'Build Your Own Sudoku' 'http://www.mit.edu/~puzzle/2014/puzzle/build_your_own_sudoku/'
```
