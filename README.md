To get this working, you first need the appropriate Python libraries (should be all the ones in requirements.txt)

Then you also need to generate a google token. You can follow the guide [here](https://developers.google.com/drive/web/quickstart/quickstart-python#step_1_enable_the_drive_api)

Basically, you need to create a project, then generate client id and client secret, and put those in your homedir (whatever comes back when you run `python -c 'import os; print os.path.expanduser("~")'`) in files `gdrive_client_id` and `gdrive_client_secret`. Then I think you can use `get_credentials()` in `gdrive_api.py` to grab and save the token you'll use for all your api requests.

You also need to grab the slack token, probably from [here](https://api.slack.com/web#auth). And put that in a file `slack_token`. Then you should be able to call
```
./prep_puzzle.py 'Build Your Own Sudoku' 'http://www.mit.edu/~puzzle/2014/puzzle/build_your_own_sudoku/'
```
