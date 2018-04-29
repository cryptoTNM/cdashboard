# Dpos-crypto-dashboard
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ThamarD/Dpos-crypto-dashboard/blob/master/LICENSE)
[![docs](https://img.shields.io/badge/doc-online-blue.svg)](https://github.com/ThamarD/Dpos-crypto-dashboard/wiki)


Dashboard for Dpos delegate information, Masternodes status, staking info and crypto Wallets

An overview of all your important Dpos delegate information, Masternodes status, staking info or even just crypto Wallets!
Crypto Dashboard is made to sort these things out and present you all your important information in one handy overview.



## Installing it

First clone the crypto dashboard repository, install python and requests:

```git clone https://github.com/ThamarD/cdashboard```

```cd cdashboard```

```apt-get install python3-pip```

```pip3 install requests```


## Configure it

To configure the Dashboard we need to open the config.json. With this install you get an example config.json which you need to change based on your own parameters.
Explanation of the parameters:
- cryptodashboard_file_version: internal check if version is correct
- crunch_history: true or false; currently not functioning yet!
- logfile: the file where all coin info is stored and added to; default "cdashboard.json"; you can change this name the way you like
- coins: section where the coin info is represented
   - identifier: coin identifier, 
      - coin: coin name
      - node: Dpos coin node web address
      - pubaddress: the public address of the coin
      - cointype: options are: dpos_delegate, dpos_private, masternode, pos_staking and wallet
      - exploreraddress: coin explorer web address (for cointype: masternode, pos_staking and wallet)


```
Example: config.json
------------------------------------------
{
  "cryptodashboard_file_version": 0.6,
  "crunch_history": false,
  "logfile": "cdashboard.json",
  "coins": {
    "OXY Dutchpool Mainnet": {
      "coin": "OXY",
      "node": "https://wallet.oxycoin.io",
      "pubaddress": "15957132064002739627X",
      "cointype": "dpos_delegate"
    },
    "ONZ Dutchpool Mainnet": {
      "coin": "ONZ",
      "node": "https://node10.onzcoin.com",
      "pubaddress": "ONZkL6Jm1MKGWnVzMzkJ8jwTxbQ8Cudqh1Hw",
      "cointype": "dpos_delegate"
    }
}
``` 
    


## Start it:

```python3 cryptodashboard.py```

or if you want to use another config file:

```python3 cryptodashboard.py -c config2.json```

It produces a file "cdashboard.json" with all the dasboard information which can be presented with the included HTML setup.


We advise to run the cryptodashboard script every hour to collect it's data. The cron line to configure this (use crontab -e):

`00 * * * * cd ~/dashboard && python3 ~/dashboard/cryptodashboard.py`



## Command line usage

```
usage: cryptodashboard.py [-h] [-c config.json] [-y]

Crypto dashboard script

optional arguments:
  -h, --help            show this help message and exit
  -c config.json        set a config file (default: config.json)

```


## Supported/tested chains / explorers

At the moment CryptDashboard supports and is tested on the following chains / explorers:
- Dpos:  OXY, LWF, ONZ, LISK, ARK, SHIFT, RISE
- all clones of Iquidus Explorer 

Known issues:
- a lot of explorer chains are not supported yet; working on it!
- chainz.cryptoid.info - basic info is working, no last TX and date-received

## Changelog

### 0.6
- Initial release


## To Do
We are planning to integrate other cool features:
- support for more coin explorers
- in the HTML overview, select the history periode with a dropdown, now it is 24h and 48h;
- add a live indication in the Dpos main dashboard, the time until the node will forge
- strip/crunch the history of the cdashboard.json, e.g. after 48h only 1 entry a week


	
## License

```
Copyright (c) 2018 Thamar proud member of dutch_pool

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NON INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
```


## Donations

If you like this project and it helps you in your every day work I would greatly appreciate it if you would consider to show some support by donating to one of the below mentioned addresses.

OXY: 	902564290011692795X
LWF: 	2526916071607963001LWF
ONZ: 	ONZfxHuBy5e39nipSZuSgcKhYURE6QkWsK2j
Shift: 	18040765904662116201S
Lisk: 	8890122000260193860L
BTC: 	1NrA8k8wNRwEZj2ooKQEf2fFnF6KqTE32T


## Credits

@st3v3n, @kippers, @fnoufnou
