import requests
import json
import sys
import time
import argparse

if sys.version_info[0] < 3:
    print('python2 not supported, please use python3')
    sys.exit()

# Parse command line args
parser = argparse.ArgumentParser(description='Crypto Dashboard')
parser.add_argument('-c', metavar='config.json', dest='cfile', action='store',
                    default='config.json',
                    help='set a config file (default: config.json)')
# parser.add_argument('-y', dest='alwaysyes', action='store_const',
#                     default=False, const=True,
#                     help='automatic yes for log saving (default: no)')

args = parser.parse_args()

# Load the config file
try:
    conf = json.load(open(args.cfile, 'r'))
except:
    print('Unable to load config file.')
    sys.exit()


if 'logfile' in conf:
    LOGFILE = conf['logfile']
else:
    LOGFILE = 'cdashboard.json'


def handle_error(ex, msg, exit):
    error_msg = time.strftime('%Y-%m-%d %H:%M:%S: ') + msg
    if ex is not None:
        error_msg += ': ' + str(ex)
    print(error_msg)
    if exit:
        sys.exit()

def loadLog():
    try:
        data = json.load(open(LOGFILE, 'r'))
    except:
        data = {
            "cryptodashboard_file_version": 0.6,
            "lasttimecalculated": 0,
            "coins": {}
        }
    return data


def savelog(log, filename):
    json.dump(log, open(filename, 'w'), indent=4, separators=(',', ': '))


def get_node_url(url):
    node_url = url
    if not node_url.startswith('http'):
        handle_error(None, 'node_url needs to be in the format http://localhost:<port>', False)
    if node_url.endswith('/'):
        node_url = node_url[:-1]

    return node_url


##############################################################################3
# get_walletbalance
# This function expects an url which is complete and  returns only one number, the balance!
# most API's have two ways to show balance's: a complete website or explicit values of the address.
# You need the API part which shows the explicit values.
def get_walletbalance(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            response_json = response.json()
            return float(response_json)
        else:
            return float(0)
    except:
        return float(0)


##############################################################################3
# get_walletlasttransaction
# This function expects an url which is complete and  returns two numbers, the time and the amount!
# This function expects
def get_walletlasttransaction(url, walletaddress):

    # get the base_url of the url which is provided
    from urllib.parse import urlsplit
    base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))

    amountreceived = float(0.0)

    # Get the latest transaction for this Address
    try:
        response = requests.get(base_url + "ext/getaddress/" + walletaddress)
        if response.status_code == 200:
            response_json = response.json()
            last_txs_nr = len(response_json["last_txs"])
            addresses = response_json["last_txs"][last_txs_nr - 1]["addresses"]

            # Get with this address the latest Blockhash for this Address
            response2 = requests.get(base_url + "api/getrawtransaction?txid=" + addresses + "&decrypt=1")
            if response2.status_code == 200:
                response_json2 = response2.json()
                blockhash = response_json2["blockhash"]

                # Get with this address the latest time and amount for the last txid
                response3 = requests.get(base_url + "api/getblock?hash=" + blockhash)
                if response3.status_code == 200:
                    response_json3 = response3.json()
                    timereceived = response_json3.get("time", 0)
                    for payment in response_json2["vout"]:
                        x = payment["scriptPubKey"].get("addresses")
                        if x:
                            for voutaddresses in x:
                                if voutaddresses == walletaddress:
                                    amountreceived = payment["value"]
                    return timereceived, amountreceived
                else:
                    return 0,0
            else:
                return 0,0
        else:
            if base_url == "https://chainz.cryptoid.info/":
                # Get the latest transaction for this Address
                # Currently an API key is needed and is not available to receive by email (dd April 9, 2018)
    #            response = requests.get(base_url + "???" + walletaddress)
    #            if response.status_code == 200:
    #                response_json = response.json()
                return 0,0
            return 0,0
    except:
        return 0, 0


##############################################################################3
# compare dictionary's
# x = dict(a=1, b=2)
# y = dict(a=2, b=2)
# added, removed, modified, same = dict_compare(x, y)
#############################################################################3
def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same


##############################################################################3
# get_dpos_api_info
# specific for Dpos explorers and their API
# node_url: is the base of the API without the /, which is stripped earlier
# address: can be several identifications: the public address; the publickey
# api_info : which part of the API we use (see if statement

def get_dpos_api_info(node_url, address, api_info):
        if api_info == "publicKey":
            request_url = node_url + '/api/accounts/getPublicKey?address=' + address
        elif api_info == "delegate":
            request_url = node_url + '/api/delegates/get?publicKey=' + address
        elif api_info == "accounts":
            request_url = node_url + '/api/delegates/voters?publicKey=' + address
        elif api_info == "balance":
            request_url = node_url + '/api/accounts/getBalance?address=' + address
        elif api_info == "transactions":
            request_url = node_url + '/api/transactions?limit=1&recipientId=' + address + '&orderBy=timestamp:desc'
        elif api_info == "epoch":
            request_url = node_url + '/api/blocks/getEpoch'
        else:
            return 0

        try:
            response = requests.get(request_url)
            if response.status_code == 200:
                response_json = response.json()
                if response_json['success']:
                     return response_json[api_info]
                else:
#                    print(request_url + ' ' + str(response.status_code) + ' Failed to get ' + api_info)
                    return 0
            else:
                print("Error: " + request_url + ' ' + str(response.status_code) + ', response not 200' + api_info)
                return 0
        except:
                print("Error: url is probably not correct: " + request_url)
                return 0


def dashboard():
    from urllib.parse import urlsplit
    from datetime import datetime
    from operator import itemgetter

    # read the json, this is the database of the dashbaord
    coininfo_output = loadLog()

    coin_explorerlink = ""
    # Update last time the cryptodashboard has run
    coininfo_output['lasttimecalculated'] = int(time.time())
    timestamp = coininfo_output['lasttimecalculated']
    timereceived = 0
    amountreceived = 0

    for item in conf["coins"]:
        coinitemexists = 0

        if item in coininfo_output["coins"]:
            coinitemexists = 1

        # Section: dpos_delegate and dpos_private
        if conf["coins"][item]["cointype"] == "dpos_delegate" or conf["coins"][item]["cointype"] == "dpos_private":
            coin_nodeurl = get_node_url(conf["coins"][item]["node"])
            coin_explorerlink = coin_nodeurl.replace("wallet", "explorer")

            # get the public key of this address
            coin_pubkey = get_dpos_api_info(coin_nodeurl, conf["coins"][item]["pubaddress"], "publicKey")

            # first check if url is working, if so, I asume other calls will also work ;-)
            if coin_pubkey:
                # get the current balance of this address
                balance = int(get_dpos_api_info(coin_nodeurl, conf["coins"][item]["pubaddress"], "balance"))/100000000

                # get all the delegate info
                coin_delegateinfo = get_dpos_api_info(coin_nodeurl, coin_pubkey, "delegate")

                # get number of voters
                nrofvoters = len(get_dpos_api_info(coin_nodeurl, coin_pubkey, "accounts"))

                # get last transaction
                transactions = (get_dpos_api_info(coin_nodeurl, conf["coins"][item]["pubaddress"], "transactions"))
                if transactions != 0:
                    amountreceived = transactions[0]["amount"] / 100000000

                    coin_epoch = get_dpos_api_info(coin_nodeurl, 0, "epoch")
                    # convert the epoch time to a normal Unix time in sec datetime.strptime('1984-06-02T19:05:00.000Z', '%Y-%m-%dT%H:%M:%S.%fZ')
                    utc_dt = datetime.strptime(coin_epoch, '%Y-%m-%dT%H:%M:%S.%fZ')
                    # Convert UTC datetime to seconds since the Epoch and add the found transaction timestamp to get the correct Unix date/time in sec.
                    timereceived = (utc_dt - datetime(1970, 1, 1)).total_seconds() + transactions[0]["timestamp"]


                # todo get the next forger: niet in dit bestand!
                # https://explorer.oxycoin.io/api/delegates/getNextForgers
                # https://wallet.oxycoin.io/api/delegates/getNextForgers?limit=201


                # check if item/coin already excists? If not, add coin to the output list
                if coinitemexists != 1:
                    coininfo_output["coins"][item] = {
                        "coin": conf["coins"][item]["coin"],
                        "cointype": conf["coins"][item]["cointype"],
                        "delegatename": "",
                        "explink": coin_explorerlink + "/address/" + conf["coins"][item]["pubaddress"],
                        "history": []
                    }

                # generic variable coin info
                coininfo_tocheck = {
                    "timestamp": timestamp,
                    "totalbalance": balance,
                    "amountreceived": amountreceived,
                    "timereceived": timereceived,
                    "rank": 0,
                    "approval": 0,
                    "nrofvoters": 0
                }

                # Specific delegate Dpos coin info
                if coin_delegateinfo != 0:
                    coininfo_output["coins"][item]["delegatename"] = coin_delegateinfo["username"]
                    coininfo_tocheck["rank"] = coin_delegateinfo["rate"]
                    coininfo_tocheck["approval"] = coin_delegateinfo["approval"]
                    coininfo_tocheck["nrofvoters"] = nrofvoters

                # archive the coin info:
                # 1. check if coin info is the same as earlier samples, in the history (timestamp may differ)
                # 2. for the overview add/overwrite the info to the current coin info.
                coininfo_alreadypresent = 0
                for coininfohistory in coininfo_output["coins"][item]["history"]:
                    added, removed, modified, same = dict_compare(coininfohistory, coininfo_tocheck)
                    if len(modified) == 1 and "timestamp" in modified:
                        coininfo_alreadypresent = 1
                        break
                if coininfo_alreadypresent == 0:
                    coininfo_output["coins"][item]["history"].append(coininfo_tocheck)

                # try to figure out the 24h change of rank and nrofvoters
                #todo: need testing before release!! probably combine the above functionality with this one... while ittering over the history array
                # coininfohistory = sorted(
                #     coininfo_output["coins"][item]["history"],
                #     key=int k: ("timestamp" not in k, k.get("timestamp", None)),
                #     reverse=True
                #     )

                coininfo_output["coins"][item]["history"].sort(key=lambda x:x["timestamp"], reverse=True)
                for coininfohistory in coininfo_output["coins"][item]["history"]:
                    timestamp24hpast = int(time.time()) - 23 * 60 * 59
                    # coin_timestamp_readable = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(coininfohistory["timestamp"])))
                    # timestamp24hpast_readable = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp24hpast))

                    if coininfohistory["timestamp"] <= timestamp24hpast:
                        rankdelta24h = coininfohistory["rank"] - coininfo_tocheck["rank"]
                        coininfo_tocheck["rankdelta24h"] = rankdelta24h
                        votersdelta24h = coininfo_tocheck["nrofvoters"] - coininfohistory["nrofvoters"]
                        coininfo_tocheck["nrofvoters24h"] = votersdelta24h
                        totalbalancedelta24h = coininfo_tocheck["totalbalance"] - coininfohistory["totalbalance"]
                        coininfo_tocheck["totalbalancedelta24h"] = totalbalancedelta24h
                        break

                coininfo_output["coins"][item].update(coininfo_tocheck)

                print(coininfo_output["coins"][item])

        elif conf["coins"][item]["cointype"] == "masternode" or conf["coins"][item]["cointype"] == "pos_staking" or conf["coins"][item]["cointype"] == "wallet":
            # Section: masternode, pos_staking and wallet
            # todo: clean this up if neccesary to split it in masternode, pos_staking and or wallet
            balance = get_walletbalance(conf["coins"][item]["exploreraddress"] + conf["coins"][item]["pubaddress"])
            timereceived, amountreceived = get_walletlasttransaction(conf["coins"][item]["exploreraddress"], conf["coins"][item]["pubaddress"])

            # get the base_url of the url which is provided
            base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(conf["coins"][item]["exploreraddress"]))

            if coinitemexists != 1:
                coininfo_output["coins"][item] = {
                    "coin": conf["coins"][item]["coin"],
                    "cointype": conf["coins"][item]["cointype"],
                    "delegatename": "",
                    "timereceived": timereceived,
                    "explink": base_url + "address/" + conf["coins"][item]["pubaddress"],
                    "history": []
                }
            #create temp coininfo block to check if the same values are already in the json, if so, I don't want those values
            coininfo_tocheck = {
                "timestamp": timestamp,
                "rank": "",
                "totalbalance": balance,
                "approval": "",
                "nrofvoters":"",
                "amountreceived": amountreceived,
                "timereceived": timereceived
            }

            coininfo_alreadypresent = 0
            for coininfohistory in coininfo_output["coins"][item]["history"]:
                added, removed, modified, same = dict_compare(coininfohistory, coininfo_tocheck)
                if len( modified ) == 1 and "timestamp" in modified:
                    coininfo_alreadypresent = 1
                    break

            if coininfo_alreadypresent == 0:
                coininfo_output["coins"][item]["history"].append(coininfo_tocheck)


            coininfo_output["coins"][item]["history"].sort(key=lambda x:x["timestamp"], reverse=True)
            for coininfohistory in coininfo_output["coins"][item]["history"]:
                timestamp24hpast = int(time.time()) - 23 * 60 * 59
                coin_timestamp_readable = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(coininfohistory["timestamp"])))
                timestamp24hpast_readable = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp24hpast))

                if coininfohistory["timestamp"] <= timestamp24hpast:
                    totalbalancedelta24h = coininfo_tocheck["totalbalance"] - coininfohistory["totalbalance"]
                    coininfo_tocheck["totalbalancedelta24h"] = totalbalancedelta24h
                    break

            coininfo_output["coins"][item].update(coininfo_tocheck)

            print(coininfo_output["coins"][item])
        else:
            print("Unknown cointype: " + conf["coins"][item]["cointype"] + ", please check your config.json. Valid cointypes are: dpos_delegate, dpos_private, masternode and pos_staking.")

    savelog(coininfo_output, LOGFILE)


def logcruncher():
    # read the json, this is the database of the dashbaord
    coininfo_crunched = coininfo_tocrunch = loadLog()

    # calculate the variables
    daytime = 4 * 60 * 60
    weektime = 7 * daytime
    monthtime = 4 * weektime

    currenttime = int(time.time())

    debugthis = 0
  #  if debugthis == 1:
    # 21 april 2018
 #       currenttime = 1524268800

    today_timestamp_readable = time.strftime("%Y-%m-%d", time.localtime(int(currenttime)))

    # for every coin, crunch the history
    for item in conf["coins"]:

        pasttime = currenttime
        coininfohistory = sorted(coininfo_tocrunch["coins"][item]["history"], key=lambda k: ("timestamp" not in k, k.get("timestamp", None)), reverse=True)
        coin_daytimestamparray_readable = []
        coinhisroytitem_temp = {

            "history": []
        }

        for coinhisroytitem in coininfohistory:
            # between < 1 day every hour needs 1 entry
            # after this 1 day is 1 entry in the log

            coin_timestamp_readable = time.strftime("%Y-%m-%d", time.localtime(int(coinhisroytitem["timestamp"])))

            # If coin timestamp is from today; add them all
            if coin_timestamp_readable == today_timestamp_readable:
                if debugthis == 1:
                    coinhisroytitem["timestamp_readable"] = coin_timestamp_readable
                coinhisroytitem_temp["history"].append(coinhisroytitem)


            # If coin timestamp is from today -1 day; add only the first and skip the rest
            if pasttime - daytime >= coinhisroytitem["timestamp"]:
                if coin_timestamp_readable not in coin_daytimestamparray_readable:
                    if debugthis == 1:
                        coinhisroytitem["timestamp_readable"] = coin_timestamp_readable
                    coinhisroytitem_temp["history"].append(coinhisroytitem)

                    # add this timestamp to the compare array -  we don't need another sample for this date!
                    coin_daytimestamparray_readable.append(time.strftime("%Y-%m-%d", time.localtime(int(coinhisroytitem["timestamp"]))))

        coininfo_crunched["coins"][item]["history"] = coinhisroytitem_temp["history"].copy()

    if debugthis == 1:
        print(coininfo_crunched)
        savelog(coininfo_crunched, "test_" + LOGFILE)
    else:
        savelog(coininfo_crunched, LOGFILE)

#########################################################
# Todo
# 1. implement in the HTML the periode to look back from a dropdown; looks like: https://plnkr.co/edit/mig31CiYgHX3iH9DI6Wc?p=preview



if __name__ == "__main__":
    dashboard()
#    Todo!!! reduce/rotate log function
#     if conf["crunch_history"]:
#         logcruncher()
