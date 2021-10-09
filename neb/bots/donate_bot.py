import json
import os

from urllib3 import PoolManager
from urllib.parse import urlencode
from os.path import expanduser

HOST = "https://www.simplicialsoftware.com"
GET_CLAN_MEMBERS_URI = "/api/account/GetClanMembers"
GET_CLAN_INFO_URI = "/api/account/GetClanInfo"
COIN_PURCHASE_URI = "/api/account/CoinPurchase"
SENDMAIL_URI = "/api/account/SendMail"
DONATOR_TICKET = "insert your own ticket here"
EXCEPTIONS = [22621266, 22229823, 22712543, 23063764, 5925616, 22006472, 23299246, 23067926, 23428920]

ERR_NEW_ACCOUNT = "Account must be 3 days old to send mail."

MAIL_SUBJECT = "Thank You :)"
MAIL_MESSAGE = "Thank you for being apart of my clan. :)"

DONATE_AMOUNT = 15000

pdata_send_mail = {
    'Game': 'Nebulous',
    'Ticket': DONATOR_TICKET,
    'ToAID': -1,
    'ToAllClan': 'true',
    'ClanRole': 'INVALID',
    'Subject': MAIL_SUBJECT,
    'Message': MAIL_MESSAGE
}
pdata_donate = {
    'Game': 'Nebulous',
    'Ticket': DONATOR_TICKET,
    'ItemType': 'GIVE_PLASMA',
    'ItemID': '0',
    'ExpectedPrice': DONATE_AMOUNT
}
pdata_get_clan_members = {
    'Game': 'Nebulous',
    'Version': '839',
    'Ticket': DONATOR_TICKET,
    'ClanName': 'Clan',
    'StartIndex': 0,
    'Count': 0,
    'Search': ''
}
pdata_get_clan_info = {
    'Game': 'Nebulous',
    'Version': '839',
    'Ticket': DONATOR_TICKET
}

http = PoolManager()

def neb_req(uri, data):
    headers = {
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    return json.loads(http.urlopen('POST', HOST + uri, body = urlencode(data), headers = headers).data.decode('utf-8'))

def get_clan_members():
    clan_info = neb_req(GET_CLAN_INFO_URI, pdata_get_clan_info)
    members = []

    if clan_info['Error'] is not None:
        print("[ - ] Failed to get clan info: %s" % clan_info['Error'])

        return []

    pdata_get_clan_members['ClanName'] = clan_info['Name']
    pdata_get_clan_members['Count'] = clan_info['ClanMemberCount']

    clan_members = neb_req(GET_CLAN_MEMBERS_URI, pdata_get_clan_members)

    print(clan_members)

    if clan_members['Error'] is not None:
        print("[ - ] Failed to get clan members: %s" % clan_info['Error'])

        return []

    for member in clan_members['ClanMembers']:
        if member['Id'] in EXCEPTIONS:
            continue

        members.append(member['Id'])

    return members

def donate_to(member):
    pdata_donate['ItemID'] = member

    response = neb_req(COIN_PURCHASE_URI, pdata_donate)

    if response['Error'] is not None:
        print("[ - ] Failed to give plasma: %s" % response['Error'])

        return

    print("Done.")

def main():
    for member in get_clan_members():
        print("[ + ] Donating %d plasma to account %d..." % (DONATE_AMOUNT, member), end = ' ')
        donate_to(member)

    # print("[ + ] Sending thank you..", end = ' ')

    # response = neb_req(SENDMAIL_URI, pdata_send_mail)

    # if response['Error'] is not None:
    #    print('Failed.')
    #    print("[ - ] Failed to deliver thank you: %s" % response['Error'])

    #    return

    # print("Done.")

if __name__ == '__main__':
    main()
