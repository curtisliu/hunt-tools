#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

import argparse
import codecs
import os
import pprint
import sys
import urllib

import httplib2
import simplejson as json
from apiclient.discovery import build
from lxml import etree
from oauth2client.file import Storage

HOMEDIR = os.path.expanduser('~')

def get_credentials():
    credentials_file = os.path.join(HOMEDIR, 'gdrive_creds')
    storage = Storage(credentials_file)
    creds = storage.get()
    assert creds
    return creds

def get_authed_http():
    credentials = get_credentials()
    return credentials.authorize(httplib2.Http())

def get_gdrive_service():
    http = get_authed_http()
    return build('drive', 'v2', http=http)

def get_shortener_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return build('urlshortener', 'v1', http=http)


TEMPLATE_SHEET_TITLE = "Hunt Puzzle Template"
GOOGLE_SHEET_MIMETYPE = "application/vnd.google-apps.spreadsheet"

def get_sheet_by_title(title):
    gdrive = get_gdrive_service()
    clauses = (
        "title = '{}'".format(TEMPLATE_SHEET_TITLE.replace("'", "\\'")),
        "mimeType = '{}'".format(GOOGLE_SHEET_MIMETYPE.replace("'", "\\'")),
    )
    query = ' and '.join(clauses)

    request = gdrive.files().list(q=query)
    response = request.execute()

    assert 'items' in response
    items = response['items']
    assert items, "no items! response was \n{}".format(response)
    assert len(items) == 1, "found {} items:\n{}".format(
        len(items), pprint.pformat(items))
    return items[0]

def copy_sheet(sheet, title=None):
    gdrive = get_gdrive_service()
    body = {}
    if title is not None:
        assert isinstance(title, basestring)
        body['title'] = title
    request = gdrive.files().copy(fileId=sheet['id'], body=body)
    response = request.execute()
    # response should be json of new sheet attributes
    return response

def get_worksheet_feed_url(sheet_id):
    return 'https://spreadsheets.google.com/feeds/worksheets/{}/private/full'.format(sheet_id)

def get_cell_feed_url_from_sheet_entry_xml(entry_xml):
    links = []
    for e in entry_xml:
        if not e.tag.endswith('link'):
            continue
        if not e.attrib['rel'].endswith('cellsfeed'):
            continue
        links.append(e)
    assert len(links) == 1, etree.fromstring(entry_xml, pretty_print=True)
    return links[0].attrib['href']

# def set_cell(sheet_id, row, col, value, original_value=None):
#     h = get_authed_http()
#     worksheet_feed_url = get_worksheet_feed_url(sheet_id)
#     response_headers, response = h.request(worksheet_feed_url)
#     xml_tree = etree.fromstring(response)

#     # first get sheet 1
#     entries = [e for e in xml_tree if e.tag.endswith('entry')]
#     assert len(entries) == 1
#     sheet1 = entries[0]

#     cell_feed_url = get_cell_feed_url_from_sheet_entry_xml(sheet1)

#     response_headers, response = h.request(cell_feed_url)
#     xml_tree = etree.fromstring(response)
#     entries = [e for e in xml_tree if e.tag.endswith('entry')]


def get_cell_entry_url(sheet_id, row, col):
    return 'https://spreadsheets.google.com/feeds/cells/{}/od6/private/full/R{}C{}'.format(sheet_id, row, col)


def set_cell(sheet_id, row, col, value):
    http = get_authed_http()
    cell_entry_url = get_cell_entry_url(sheet_id, row, col)
    response_headers, response = http.request(cell_entry_url)
    cell_entry = etree.fromstring(response)
    edit_url = cell_entry[-2].attrib['href']

    nsmap = {
        None: "http://www.w3.org/2005/Atom",
        'gs': "http://schemas.google.com/spreadsheets/2006"
    }
    put_entry = etree.Element('entry', nsmap=nsmap)
    put_entry.append(cell_entry[0]) # id element
    put_entry.append(cell_entry[-2]) # edit url

    actual_cell = cell_entry[-1]
    actual_cell.text = None
    actual_cell.attrib['inputValue'] = value
    put_entry.append(actual_cell) # put element
    headers = {'content-type': 'application/atom+xml'}
    response_headers, response = http.request(
        edit_url, 'PUT',
        body=etree.tostring(put_entry),
        headers=headers)


class Sheet(object):
    def __init__(self, puzzle_name):
        print("initializing sheet...")
        # locate the template puzzle sheet
        print("locating template sheet...")
        template_sheet = get_sheet_by_title(TEMPLATE_SHEET_TITLE)

        # make a copy of the template and name it puzzle_name
        print("making a copy...")
        self.obj = copy_sheet(template_sheet, title=puzzle_name)

        # pprint.pprint(self.obj)

    @property
    def link(self):
        return self.obj['alternateLink']

    def set_links(self, puzzle_link, channel_link):
        sheet_id = self.obj['id']
        print "setting links on sheet..."
        puzzle_cell_value = '=HYPERLINK("{}","puzzle")'.format(puzzle_link)
        channel_cell_value = '=HYPERLINK("{}","slack")'.format(channel_link)
        set_cell(sheet_id, 1, 1, puzzle_cell_value)
        set_cell(sheet_id, 1, 2, channel_cell_value)


def get_slack_token():
    with open(os.path.join(HOMEDIR, 'slack_token')) as f:
        return f.read().strip()

def create_channel(name):
    body_dict = {
        'token': get_slack_token(),
        'name': name,
    }
    body = urllib.urlencode(body_dict)
    headers = {'content-type': 'application/json'}
    response_headers, channel = httplib2.Http().request(
        "https://slack.com/api/channels.create",
        "POST",
        body=body,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    # handle name taken
    # handle errors
    return json.loads(channel)['channel']

def set_channel_purpose(id, purpose):
    body_dict = {
        'token': get_slack_token(),
        'channel': id,
        'purpose': purpose,
    }
    body = urllib.urlencode(body_dict)
    headers = {'content-type': 'application/json'}
    response_headers, channel = httplib2.Http().request(
        "https://slack.com/api/channels.setPurpose",
        "POST",
        body=body,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

def set_channel_topic(id, topic):
    body_dict = {
        'token': get_slack_token(),
        'channel': id,
        'topic': topic,
    }
    body = urllib.urlencode(body_dict)
    headers = {'content-type': 'application/json'}
    response_headers, channel = httplib2.Http().request(
        "https://slack.com/api/channels.setTopic",
        "POST",
        body=body,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )


class Channel(object):
    def __init__(self, puzzle_name):
        print "creating slack channel"
        self.obj = create_channel(puzzle_name)

    @property
    def link(self):
        return "https://superteamawesome.slack.com/messages/{}/activity/".format(self.obj['name'])

    def set_links(self, puzzle_link, sheet_link):
        chan_id = self.obj['id']
        purpose = 'Puzzle: {} | GSheet: {}'.format(puzzle_link, sheet_link)
        set_channel_purpose(chan_id, purpose)
        set_channel_topic(chan_id, purpose)

def shorten_link(link):
    s = get_shortener_service()
    body = {
        "longUrl": link,
    }
    response = s.url().insert(body=body).execute()
    return response['id']

def create_sheet_and_channel(puzzle_name, puzzle_link):
    # maybe shorten the puzzle link url if we feel like it
    puzzle_link = shorten_link(puzzle_link)

    # create Google Drive Spreadsheet, possibly in proper folders as
    # well. Get the id, and the url
    sheet = Sheet(puzzle_name)

    # create Slack channel. get the id, and the url
    channel = Channel(puzzle_name)

    # edit the spreadsheet with the puzzle link and the slack room link
    sheet.set_links(puzzle_link, shorten_link(channel.link))

    # edit the slack channel with the puzzle link and the spreadsheet link
    channel.set_links(puzzle_link, shorten_link(sheet.link))

    return sheet, channel


def main():
    # read command line args: puzzle name, puzzle link, maybe some round info
    parser = argparse.ArgumentParser(description='Set up puzzle')
    parser.add_argument('puzzle_name', type=str,
                        help='Puzzle Name (chan name, sheet name)')
    parser.add_argument('puzzle_link', type=str,
                        help='url of puzzle')

    args = parser.parse_args()
    print args

    puzzle_name = args.puzzle_name
    puzzle_link = args.puzzle_link

    sheet, channel = create_sheet_and_channel(puzzle_name, puzzle_link)

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
