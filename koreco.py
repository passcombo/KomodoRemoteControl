# TODO:
# better reply when succes send - current wallet status
# list unconfirmed properly - ... 
# desctibe sec measures ...
# dodac jakies lorem ipsum - powiekszajacy objetosc tekst ... 



# 1. online test
# 2. listunspent -> listtransactions
# 3. correct history
# 4. finalize migrate
# 5. finalize send any
# 
# zastapic listunspent przez listtransactions - stamtad wziac wszystkie adresy ... 	
# w portfelu - dodac niepotwierdzony balance 

# 3. ? send2 function
# 4. first online test
# dodac tylko wersje z zip aes encryption instead gpg
# 
# [ok] try sending
# dodac opcje sendany addr_to amount - zeby nie podawac adresu poczatkowego
# dodac tez opcje ksiazki adresowej
# ostatecznei zostawic input ale zrobic wersje deamon dla maila
# aply limits
# implement mail read and reply
# d. image with title and alt implementation - html email - read on client side - test normal read, later encrypted
# incoming encryption, response (+confirmation =1 msg)
# default incoming confirmation sending / monitorin raw text incoming to my address ?
# set data directory / hushd ?


# komende wallet moze odpalac w tle i zawsze meic pod reka bo moze sie przydac ?
# odpalac po kazdym sprawdzeniu, wykonaniu tranzakcji lub dodaniu adresu zeby meic aktualny stan
# dodac listowanie incoming tx ...

# implementacja wysylania oraz limitow 

# todo: monitor input commands
# interpretation
# run
# confirmations
# limits: amount / time
# db logs - sent to apply limits
# calc total sent amount during TIME
# monitoring incoming payments
# global variables in file: chain name, default address, monitor incoming, ask confirmations, refresh time



import os
import smtplib
import time
import imaplib
import email

from termcolor import colored
# from datetime import datetime
# from datetime import timedelta
import datetime

# from openpyxl import load_workbook
from pandas import DataFrame
import pandas
import subprocess
import json
# import mylibs.wallet_commands as wallet_commands
import mylibs.helpers as helpers
import mylibs.mailbox as mailbox
import mylibs.process_msgs as msgproc

os.system('color')
# import platform

# should test basics on start:
# email connection works
# 

	
# DEAMON_DEFAULTS["full-gpg-password"], DEAMON_DEFAULTS["symetric-password"]


DEAMON_DEFAULTS={
"tx_amount_limit":"100",
"tx_time_limit_hours":"24",
"tx_limit_type":"total", # or "per_addr"
"mail_title_contains":"lorem ipsum 666",
"decrypted_mail_content_contains":"heLL o wallet", # not needed - encrypted with pass if one guess pass can als oguess this 
"SMTP_SERVER":"imap.yahoo.com",
"full-gpg-password":"",
"symetric-password":"", # used for simple encryption or zip files 
"mail_from":"sendfromemail@asdf.com", # if = ask will perform forced ask on start
"mail_from_pswd":"asdf1234%^&*QWER", # if = ask will perform forced ask on start
"mail_to":"sendtoemail@asdf.com", # if empty or same as from - use drafts ... 
# "responsive":"True", #if responsive - after each action gives feedback (read cmd, run cmd, found incoming payment - active monitoring, )
"delete_after_sent":"True" # if mail to is not empty and diff to mail from (sending email, not draft) - it will delete sent email after some minutes
}

# double or quadruple escapes needed on win
WALLET_DEFAULTS={
"cli":"komodo-cli.exe",
"ac_name":"KOMODO",
"ac_params":"",
"komodod-path":"komodod.exe",
"deamon_warning":"make sure server is running and you are connecting to the correct RPC port",
"fee":"0.0001"
}


# cwd = os.getcwd()
# print(cwd)
# exit()




selected_mode=helpers.ask_mode() #'deamon' # 'wallet' #'deamon' # helpers.ask_mode() #'wallet' #ask_mode() # if selected_mode=='deamon':


edit_wallet_deamon=True

tmpcond,tmppid=helpers.check_komodod_running()
if tmpcond:
	edit_wallet_deamon=False

		
wc,rd=helpers.create_config_file_if_not_exist( os.path.join("config","custom_wallet_config.txt") ,WALLET_DEFAULTS)

if edit_wallet_deamon:
	helpers.ask_edit(wc,rd, os.path.join("config","custom_wallet_config.txt") ,WALLET_DEFAULTS)
	
WALLET_DEFAULTS=helpers.get_dict_config( os.path.join("config","custom_wallet_config.txt"),WALLET_DEFAULTS)
print("WALLET_CONFIG",WALLET_DEFAULTS)	
	
	
	
	
# exit()

wc,rd=helpers.create_config_file_if_not_exist( os.path.join("config","custom_deamon_config.txt")  ,DEAMON_DEFAULTS)
helpers.ask_edit(wc,rd,os.path.join("config","custom_deamon_config.txt") ,DEAMON_DEFAULTS)
DEAMON_DEFAULTS=helpers.get_dict_config(os.path.join("config","custom_deamon_config.txt") ,DEAMON_DEFAULTS)
print("DEAMON_DEFAULTS",DEAMON_DEFAULTS)	

if selected_mode=='deamon':
	DEAMON_DEFAULTS=mailbox.verify_email_conn(DEAMON_DEFAULTS)
	
# exit()

COMMANDS=list(set(["help"
		, "help COMMAND"
		,"wallet"
		,"newzaddr"
		,"newaddr" 
		, "send"
		,"blocks" 
		,"stop"
		,"exit"
		,"getinfo"
		, "validateaddress"
		,"listunspent"
		,"listunconfirmed"
		
		# ,"history"
		# , "merge"
		# , "send2" # send only typing to addr, wallet will figure out how to pay using total balance first chekcing it payment possible ... 
		# , "z_getoperationstatus"
		# ,"listaddressgroupings"
		# ,"listtransactions"
		# ,"getreceivedbyaddress"
		# ,"getrawtransaction"
		# ,"gettransaction"
		# ,"createrawtransaction"
		])) #.sort() # ensure unique
COMMANDS.sort()




CMD_HELP={"COMMAND":"EXAMPLE:\nhelp send"
		, "send":"EXAMPLE:\nsend from=zs1kp6dthe7sperd7n47cm6du4xd3q3kwc785dmz4pyc47xawydygy9ku5y3ha24pspdra4vygk04c to=zs19t5wmas587nvnaw2m5g00vky6v07jyfld2y90l3yj2gsj74qfsmck2szvhr5vjvz0f5vkq4uv8q amount=0.001 \n # you may also use aliasses like:\n send from=zs104c to=zs1v8q amount=0.002"
		, "stop":"Stop komodod and exit script"
		, "exit":"Exit script without stopping komodod"
		, "merge":"merge from=zaddr1,zaddr2,..,zaddrN to=zaddrM"
		, "validateaddress":"EXAMPLE:\nvalidateaddress zs19t5wmas587nvnaw2m5g00vky6v07jyfld2y90l3yj2gsj74qfsmck2szvhr5vjvz0f5vkq4uv8q"}
		
FULL_DEAMON_PARAMS=[WALLET_DEFAULTS["komodod-path"] , "-ac_name="+WALLET_DEFAULTS["ac_name"]] + WALLET_DEFAULTS["ac_params"].split(" ") #"komodod.exe"
CLI_STR=WALLET_DEFAULTS["cli"]+" -ac_name="+WALLET_DEFAULTS["ac_name"]



#####################################################################
####################### VERIFY wallet is synced

SLEEP_TIME=7

max_iter=777777

# deamon_already_running=False
deamon_started=False
zxc=''


while max_iter>-1:

	print("... CHECKING WALLET STATUS ... ",max_iter)
	try:
	# if True:
		print('\n\n_>_+_><><> \n\ngetinfo \n\n IF THIS text will not move for too long (1-2 minutes) - check system tasks and kill all related tasks!')
		zxc=subprocess.getoutput(CLI_STR+" getinfo") # check wallet stat synced
		zxc=str(zxc)
		# print('****** ZXC \n\n\n ******** \n',zxc)
		
		if 'is not recognized' in zxc or 'exe' in zxc:
			print('Command ['+CLI_STR+" getinfo"+'] not recognized - wrong path ?')
		
		elif WALLET_DEFAULTS["deamon_warning"] in zxc:
		
			if deamon_started:
				print("\n komodod deamon not responding? ..o.o... [komodod] already running ?.. if this error persists - check system processes and kill [komodod] ")
				# break
				
				# better find process, kill it, then start again and wait few seconds ... 
				print('... Will try to resolve automatically first ... searching komodod process to kill:')
				tmpcond,tmppid=helpers.check_komodod_running()
				print('Found',tmppid)
				time.sleep(3)
				print('Killing process:')
				killproc=psutil.Process(tmppid)
				killproc.kill()
				time.sleep(1)
				print('Starting komodod:')
				
				subprocess.Popen( FULL_DEAMON_PARAMS) # stdout , stdout=DEVNULL 
				
				print('Started komodod. Give few seconds to catch up data...')
				time.sleep(SLEEP_TIME)
				
			else:
				print("\n*** DEAMON NOT RUNNING ? - TRY RUNNING DEAMON ***\n") #in new terminal
				
				subprocess.Popen( FULL_DEAMON_PARAMS) #, stdout=DEVNULL  
				print("\n STARTED DEAMON \n")
				deamon_started=True
				time.sleep(SLEEP_TIME)	
				
		else:
		
			y = json.loads(zxc)
			
			while y["longestchain"]==0 :
				print("\n***  ... WAITING PROPER DEAMON STATE... Now: longestchain==0\n")
				time.sleep(3*SLEEP_TIME)	
				zxc=subprocess.getoutput(CLI_STR+" getinfo") # check wallet stat synced
				zxc=str(zxc)
				y = json.loads(zxc)				
			
			if y["synced"]==True:
				print('\nWALLET SYNCED!\n')
				break
			else:
				print('\n... AWAITING WALLET SYNC ...',y["blocks"],y["longestchain"])
				
		
	except:
		print("Except",zxc)
	
	time.sleep(SLEEP_TIME)	
		
	max_iter-=1
		
		

		
if WALLET_DEFAULTS["deamon_warning"] not in zxc:
	
	print( helpers.helporcmd("help",COMMANDS,CMD_HELP,False) )
	# for iicmd in COMMANDS:
		# print(iicmd)

	
	

# cmd_iter=0
# cmd_iter_max=13

while WALLET_DEFAULTS["deamon_warning"] not in zxc:


	if selected_mode=='wallet':	
	
		print("\nEnter your command:")
		time.sleep(0.5)
		user_cmd=input()
		user_cmd=helpers.clear_whites(user_cmd)
		
		cmd_res=msgproc.cmd_process(user_cmd,COMMANDS,CMD_HELP,WALLET_DEFAULTS,DEAMON_DEFAULTS,CLI_STR)
		print(cmd_res)
	
	elif selected_mode=='deamon':
	
		time.sleep(7)
		
		FROM_EMAIL=DEAMON_DEFAULTS["mail_from"]
		FROM_PWD=DEAMON_DEFAULTS["mail_from_pswd"]
		SMTP_SERVER=DEAMON_DEFAULTS["SMTP_SERVER"]
		sender_email=DEAMON_DEFAULTS["mail_to"]
		title_contains=DEAMON_DEFAULTS["mail_title_contains"]
		
		tmpstr=mailbox.read_email_from_gmail(FROM_EMAIL , FROM_PWD , SMTP_SERVER, sender_email, title_contains)

		if len(tmpstr)==0:
			print("No new command... "+str(datetime.datetime.today()))
		
		else:
		
			print('\n'+str(datetime.datetime.today())+" > Got commands!\n")
			
			commands2run=msgproc.process_main(tmpstr,DEAMON_DEFAULTS["full-gpg-password"], DEAMON_DEFAULTS["symetric-password"])
			
			# print(commands2run)
			# exit()
			
			for cc in commands2run:
				retstr=''
				print('... executing: '+commands2run[cc])
				smisplit=commands2run[cc].split(';')
				# print(smisplit)
				
				for semii in smisplit:
					# print(semii)
					if len(semii)<2:
						continue
					cmd_res=msgproc.cmd_process(semii,COMMANDS,CMD_HELP,WALLET_DEFAULTS,DEAMON_DEFAULTS,CLI_STR)
					retstr+='[!] Command ['+semii+"] \n [+] Result ["+cmd_res+"]\n\n"
				
				m_from=DEAMON_DEFAULTS["mail_from"]
				m_pa=DEAMON_DEFAULTS["mail_from_pswd"]
				m_to=DEAMON_DEFAULTS["mail_to"]
				m_subj="Processed command "+str(cc) #str(mailbox.last_proc_mail_id())
				
				helpers.save_file(os.path.join('archive','outbox',str(cc)+'.txt'),cmd_res)
				# print('\n***\n***\n send feedback ',retstr,m_subj)
				
				
				# -- encrypt cmd result
				encr_msg,encr_file=msgproc.encrypt_msg(cmd_res,cc,rsa_pass='',aes_pass=DEAMON_DEFAULTS["symetric-password"]) #DEAMON_DEFAULTS["full-gpg-password"], DEAMON_DEFAULTS["symetric-password"]
				# print(encr_msg)
				
				mailbox.send_html_email(m_from,m_pa, "KoReCo Deamon",m_to, m_subj, 'See att',file_attach=[encr_file])
				os.remove(encr_file)
				# wyrzucic html
				# tylko zalacznik
				# nr pliku zeby nie bylo pytania ... s
				
				mailbox.last_proc_mail_id(mail_id=cc)
		
	zxc=str(subprocess.getoutput(CLI_STR+" getinfo"))


	
	
	


if WALLET_DEFAULTS["deamon_warning"] not in zxc:

	# ONLY STOP IF STARTED:
	if deamon_started:
		tmplst=CLI_STR+" stop"
		tmplst=tmplst.split(" ")
		print(tmplst)
		subprocess.Popen(tmplst)
		print('\nEND\n')