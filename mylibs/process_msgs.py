import os
import smtplib
import time
import imaplib
import email
import datetime
from termcolor import colored
from pandas import DataFrame
import pandas
import subprocess
import json
import mylibs.helpers as helpers
import mylibs.mailbox as mailbox
import mylibs.wallet_commands as wallet_commands

import re


def save_msg(kk,msg,file=''):

	tmpf=''
	if file=='':
		tmpf=os.path.join('archive','inbox','msg_id_'+str(kk)+'.txt')
	else:
		tmpf=file
	
	with open(tmpf, 'w+') as f: # overwrite last id
		
		f.write( str(msg) )
		f.close()

		
		
		
def readcurrentdecry():

	tmpf=os.path.join('archive','inbox','proc','currentd.txt')
	msg_d=''
	with open(tmpf, 'r') as f: # overwrite last id
		
		msg_d=helpers.clear_whites(f.read())
		f.close()
		
	os.remove(tmpf)
		
	return msg_d


def process_main(msg_dict,fullgpgpass,simplepass=''):
	
	# print('asd',msg_dict.keys(),type(msg_dict.keys()))
	# kk=list(msg_dict.keys()).sort() #ensure order 
	# print(fullgpgpass,simplepass)
	
	
	full_gpg_cmd="gpg --pinentry loopback --passphrase "+fullgpgpass #+" -o "++" -d "+
	simple_gpg="gpg --pinentry loopback --passphrase "+simplepass
	
	commands={}
	
	for k in sorted(msg_dict):
		# print(k,msg_dict[k])
		save_msg(k,msg_dict[k])
		
		# iter=0
		for manymsg in msg_dict[k]:
			tmpf=os.path.join('archive','inbox','proc','current.txt')
			# print(tmpf)
			save_msg(0,manymsg,file=tmpf)
			
			# first try RSA
			
			str_rep=subprocess.getoutput(full_gpg_cmd+" -o "+tmpf.replace('current.txt','currentd.txt')+" -d "+tmpf)
			
			if 'RSA' in str_rep:
				print('Assume correct RSA')
				# print(k,'RSA',readcurrentdecry())
				# commands.append({k:readcurrentdecry()})
				commands[k]=readcurrentdecry()
				
			elif 'AES' in str_rep:
				print('Assume error - try AES')
				str_rep=subprocess.getoutput(simple_gpg+" -o "+tmpf.replace('current.txt','currentd.txt')+" -d "+tmpf)
				# print(k,'AES',readcurrentdecry())
				# commands.append({k:readcurrentdecry()})
				commands[k]=readcurrentdecry()
			else:
				print('Decrypt failed')
				
			os.remove(tmpf)
		
			
	return commands		
	
	
	
	
def encrypt_msg(msg_content,mid,rsa_pass='',aes_pass=''):

	tmp_path1=os.path.join('archive','outbox','proc','tmpmsg.txt')
	
	with open(tmp_path1, 'w+') as f:
					
		f.write(msg_content)
		f.close()	

	# h_head,t_tail=os.path.split(somefile)
	tmp_path2=os.path.join('archive','outbox','proc','at_'+str(mid)+'_'+helpers.now_time_str()+'.txt')
	# ofile=os.path.join(h_head,'current_encr.txt')
	
	if rsa_pass=='':
		str_gpg="gpg --cipher-algo AES256 --pinentry loopback --passphrase "+aes_pass+" -o "+tmp_path2+" -a -c "+tmp_path1
	else:
		str_gpg="gpg --pinentry loopback --passphrase "+rsa_pass+" -o "+tmp_path2+" -a -d "+tmp_path1
		
	# print('Encrypting '+str_gpg)
	gpgo=subprocess.getoutput(str_gpg)
	# print('**** gpg_output',gpgo)
		
	ret_str=''
	
	with open(tmp_path2, 'r') as f:
					
		ret_str=f.read()
		f.close()	
		
	os.remove(tmp_path1)
	# os.remove(tmp_path2)
	
	
	return ret_str,tmp_path2
	
	
	
	
# IMPORTANT : EXIT OUTSIDE!

def cmd_process(user_cmd,COMMANDS,CMD_HELP,WALLET_DEFAULTS,DEAMON_DEFAULTS,CLI_STR):
	
	is_special_cmd=False
	
	if 'help' in user_cmd.lower() or 'history' in user_cmd.lower() or 'send' in user_cmd.lower()  or 'z_getoperationstatus' in user_cmd.lower() or 'merge' in user_cmd.lower():
		is_special_cmd=True
		
		
	
	if user_cmd.lower() in COMMANDS or is_special_cmd: #"send" in ucmd
	
		# print(114)
		if user_cmd.lower()=="exit": # only make sense fo wallet not deamon
			print("...Exiting...")
			exit()
			
		elif "help" in user_cmd.lower():	
			# print(120)
				
			return helpers.helporcmd(user_cmd,COMMANDS,CMD_HELP)
			
		else:	
			# print(125)
			try:
				# print(127)
				helpers.msg_id(user_cmd)
				cmd_res=wallet_commands.process_cmd(WALLET_DEFAULTS,DEAMON_DEFAULTS,CLI_STR,user_cmd)
				return "\nCOMMAND RESULT:\n"+cmd_res
			
			except:
				return "\nCOMMAND WRONG USAGE? Or deamon stop while running... \n"
				
			if user_cmd.lower()=="stop":
				return "Remote Control closed! Handling commands and blockchain download turned off."
				
	else:
		return "\nYour command ["+user_cmd+"] not matching any of\n"+str(COMMANDS )
		
		
		
		
