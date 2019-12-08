# KomodoRemoteControl
Deamon scripts to control native wallet via encrypted email messagaes

Komodo Remote Control: KoReCo

Disclaimer: This is experimental software - use with caution for your own responsibility.

Currently it will use default foler for Komodo assets wallets and blockchain.

Script core is UI layer over komodo-cli and komodod.
Linux version will follow later.

Security measures:
- commands can be sent to wallet via encrypted email, so it needs some params and credentials to use mailbox
  and know which messages to decrypt and download
- additional security are params limiting tx amounts within selected time period (in case someone stole your password for commands encryption he will not steal much)

Modes:
- wallet - simplified wallet over cli
- deamon - listining to defined mailbox and handling commands

This is first test version - sending, displaying wallet status and help should work 

Wallet commands: 
1) send addr_from=z_addr1 addr_to=zadd2 amount=0.001
2) help # display allowed commands
3) exit #exits script but komodod still running
4) stop #stops komodod and exits
5) wallet #display addresses and amounts

It can run any native komodo asset chain (you need to have proper config for that)

To run it you need:

1. komodo-cli.exe and komodod.exe (best in same folder or correct path defined in config files)
2. OpenKeyChain app / Android
2. python 3 with libs/imports :
import os
import smtplib
import time
import imaplib
import email
import datetime
from pandas import DataFrame
import pandas
import subprocess
import json

3. proper config files:
(if you dont have them they will be created and can be edited by running the app so no worries)
custom_wallet_config.txt
custom_deamon_config.txt


Initially komodod will start syncinig, and afterwards you can use commands.
