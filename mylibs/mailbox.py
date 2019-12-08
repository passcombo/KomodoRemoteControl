# mailbox functions
import os
import smtplib
import time
import imaplib
import email
import datetime
# from termcolor import colored
# from pandas import DataFrame
# import pandas
# import subprocess
# import json
import mylibs.helpers as helpers

import re


import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders




def check_att_size(att_file_path,max_bytes=1024*1024*8):
	bytes_size = os.path.getsize(att_file_path)
	if bytes_size>max_bytes:
		return ' Img or attachment too big. Byte size '+str(bytes_size)+' bigger then max '+str(max_bytes)
	else :
		return str(bytes_size)
		
		
				
		

def send_html_email(sender_email,password,sender_name,receiver_email, subj, text_part='\n', file_attach=[], img_file='' , log_file_path='log.txt'):

	message = MIMEMultipart("html") #html
	message.set_charset('utf8')
	message["Subject"] = subj
	message["From"] = sender_name
			
	header_str_tmp_main='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "https://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
	header_str_tmp_main+='<html xmlns="https://www.w3.org/1999/xhtml">\n'
	header_str_tmp_main+="""
							<head>
							<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
							<meta http-equiv="X-UA-Compatible" content="IE=edge" />
							<meta name="viewport" content="width=device-width, initial-scale=1.0 " />
							</head>
							<body>
						"""
	
	if img_file!='':
	
		cas=check_att_size(img_file)
		if len(cas)>20:
			# helpers.log_file(log_err,'\t\t Img too big '+img_file+cas )
			return cas
		
		# helpers.log_file(log_file_path,'\t\t Img size '+img_file+' '+cas )
	
		h_head,t_tail=os.path.split(img_file) #<div style='width:1286px;height:836px'> </div>width:1456px;height:929px   #width='1456px' height='929px' width='100%' height='100%' 
		
		img_html=header_str_tmp_main+"<img src='cid:image1' alt='"+t_tail+"' title='"+t_tail+"'>"+'</body></html>'
		
		
		# msgText = MIMEText("<img src='cid:image1' alt='"+t_tail+"' title='"+t_tail+"'>", 'html')#width=80% height=80% #1456 x 929
		
		msgText = MIMEText(img_html, 'html')#width=80% height=80% #1456 x 929
		message.attach(msgText)
		
		try:
			fp = open(img_file, 'rb')
			msgImage = MIMEImage(fp.read())
			fp.close()
			msgImage.add_header('Content-ID', '<image1>')
			msgImage.add_header('Content-Disposition', 'inline', filename=t_tail) #, 'inline', filename=
			message.attach(msgImage)
		except:
			print("Could not lokte embeded img:",img_file)
			# helpers.log_file(log_file_path,'\t\t Could not lokte embeded img:' )
		
		
	else:
		# if len(html_part)<10:
		html_part=header_str_tmp_main+text_part+'</body></html>'
		# print(html_part)
		part2 = MIMEText(html_part, "html")
		message.attach(part2)
		
	# print('html ready sending')
	
	if len(file_attach)>0:
		for file in file_attach:
		
			cas=check_att_size(file)
			if len(cas)>20:
				# helpers.log_file(log_err,'\t\t  '+file+cas )
				continue
			
			# helpers.log_file(log_file_path,'\t\t Attachment size '+file+' '+cas )
		
			h_head,t_tail=os.path.split(file)
			part_file = MIMEBase('application', 'octet-stream') #MIMEBase('multipart', 'mixed; name=%s' % t_tail)   #MIMEBase('application', 'octet-stream')
			part_file.set_payload(open(file, 'rb').read())
			encoders.encode_base64(part_file)
			part_file.add_header('Content-Disposition', 'attachment; filename="%s"' % t_tail)
			message.attach(part_file)
			
	# print('att ready sending',message)
	#get all the attachments

	# Create secure connection with server and send email
	context = ssl.create_default_context()
	
	# print(receiver_email)
	# exit()
	
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
	
		server.login(sender_email, password)
		
		server.send_message( message, sender_email,  receiver_email )		# ','.join(receiver_email)
		
		# helpers.log_file(log_file_path,'\t\t SENT !!!' )
		# for em in receiver_email:
			# server.send_message( message, sender_email, em   ) #https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
			
			# print('mail sent to ',  em ) # server.sendmail( sender_email, em, message.as_string() ) #https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
			
		server.close()
		
	return 'msg sent'








# write and get tiem of last processes command to not search deeper in history
# def last_proc_mail_datetime(mailtime=None,file_path=os.path.join("logs","last_proc_mail_time.txt") ): # saving tx done

	# time_format='%Y-%m-%d %H:%M:%S'
	# tmpdatetime=datetime.datetime.today() - datetime.timedelta(days=1)
		
	# if mailtime!=None:

		# x1=mailtime.strftime(time_format)
		
		# with open(file_path, 'w+') as f:
			# f.write(str(x1))
			# f.close()
						
	# else: # if none - read 
		
		# if os.path.exists(file_path):
			# with open(file_path, 'r') as f:
				# tmpstr=f.read()
				# if len(tmpstr)>8:
					# tmpdatetime= datetime.datetime.strptime(tmpstr, time_format)
				# f.close()		
		
	# return tmpdatetime
	
def last_proc_mail_id(mail_id=None,file_path=os.path.join("logs","last_proc_mail_id.txt") ): # saving tx done

	# time_format='%Y-%m-%d %H:%M:%S'
	# tmpdatetime=datetime.datetime.today() - datetime.timedelta(days=1)
	lastid=0
		
	if mail_id!=None:

		# x1=mailtime.strftime(time_format)
		
		with open(file_path, 'w+') as f:
			f.write(str(mail_id))
			f.close()
						
	else: # if none - read 
		
		if os.path.exists(file_path):
			with open(file_path, 'r') as f:
				lastid=f.read().strip()
				# if len(tmpstr)>8:
					# tmpdatetime= datetime.datetime.strptime(tmpstr, time_format)
				f.close()	

		if helpers.is_num(lastid):
			lastid=int(lastid)
		
	return lastid
		
# gpg --passphrase zxc -o asdf.txt -d testdecrypt.txt
# split -----BEGIN PGP MESSAGE-----
# -----END PGP MESSAGE-----
# if multiple detected
# save to separate files
# decrypt files
# run cmd / later
# create msg with cmd status
# encrypt msg
# write to file\
# send encrypted
# >gpg --pinentry loopback --passphrase cqwe -o asdf.txt -d testdecrypt.txt

# dodac foldery do operacji  przechowywaniem plikow zaszyfrowanych przy i wychodzacych
# pzeniesc wsystko do subfolderu ... 




def read_email_from_gmail(FROM_EMAIL ,FROM_PWD ,SMTP_SERVER, sender_email, title_contains):

	last_datetime=datetime.datetime.today() - datetime.timedelta(days=1) #last_proc_mail_datetime()	
	
	pgp_start='-----BEGIN PGP MESSAGE-----'
	pgp_end='-----END PGP MESSAGE-----'
	
	# try:
	mail = imaplib.IMAP4_SSL(SMTP_SERVER)
	mail.login(FROM_EMAIL,FROM_PWD)
	mail.select('inbox')

	# type, data = mail.search(None, 'ALL')
	date = last_datetime.strftime("%d-%b-%Y") #(datetime.datetime.today() - timedelta(2))
	
	print(date, '(SENTSINCE {0})'.format(date),'(FROM {0})'.format(sender_email.strip())) #'(SENTSINCE {0})'.format(date),
	
	ttype, data = mail.search(None,  '(SENTSINCE {0})'.format(date), '(FROM {0})'.format(sender_email.strip()) ) 
	
	if ttype !='OK':
		print('no msg found')
		return
	
	mail_ids = data[0]


	id_list = mail_ids.split()   
	# first_email_id = int(id_list[0])
	# latest_email_id = int(id_list[-1])
	inter_indxi=[int(x) for x in id_list]
	
	################ CONDITIONS:
	# msg_from_cond='mintos'
	# fileformat='.xlsx'
	
	# rep_fname='originator-loans-zenka-ke-eur'
	# rep_fname2='.xlsx'
	
	# todo:
	# najpierw przeszukiwac tekst i musi zawierac pgp msg start/end text/plain
	# jesli nie znajdzie - przeszukiwac text/html - to na pozniej ... 
	# later also file attachment zip
	
	msg_to_process={}
	
	lpmi=last_proc_mail_id()
	
	for i in inter_indxi : 
		
		if i<=lpmi:
			continue
	
		typ, dd = mail.fetch(str(i), '(RFC822)' ) # '(BODY.PEEK[TEXT])'
		
		for response_part in dd:
		
		
			if isinstance(response_part, tuple):
				msg = email.message_from_string(response_part[1].decode('utf-8'))
				# print('\nk',msg.keys())
				# print('from? ',msg['from'])
				# print('sub? ',msg['Subject'])
				
				# msg validation initial:
				# print('testing ',sender_email,title_contains)
				# print(sender_email,"not in",str(msg['from']))
				# print(helpers.clear_whites(title_contains).lower(),"not in",helpers.clear_whites(str(msg['Subject'])).lower())
				
				if sender_email not in str(msg['from']) or helpers.clear_whites(title_contains).lower() not in helpers.clear_whites(str(msg['Subject'])).lower():
					print('Wrong sender or title - skip.\n',str(msg['from']),helpers.clear_whites(str(msg['Subject'])).lower())
					continue
				
				# msg_internal_id_str=str(msg['Message-ID'])
				# print('1',msg)
				# ijkijk=0
				for part in msg.walk():
					# print('***',ijkijk ,part.get_content_type() )
					if part.get_content_type()=='text/plain':
						tmpcont=str(part.get_payload())
						msg_list=[]
						if pgp_start in tmpcont:
							# print('\n\n\n\n',tmpcont,'\n\n\n\n')
							split1=tmpcont.split(pgp_start)
							for s1 in split1:
								if pgp_end in s1:
									split2=s1.split(pgp_end)
									for s2 in split2:
								# x = re.findall(pgp_start+".*"+pgp_end, tmpcont)
										if len(helpers.clear_whites(s2))>1:
											tmpmsg=pgp_start+s2+pgp_end
											# print('*',tmpmsg)
											msg_list.append(tmpmsg)
									
							# msg_to_process.append({'mail_id':str(i), 'mail_content':msg_list})
							msg_to_process[i]=msg_list
				
				# if len(msg_to_decrypt)==0: process html
				# if still 0 - process attachment ? or allways ?
	# print('\n',msg_to_process,'\n')
	return 	msg_to_process		
					# print('part',part,len(part))
					# print('as string',part.as_string())
					# print('payload','['+str(part.get_payload())+']')
					# ijkijk+=1
					
			# else:
				# print('\n $ response_part',response_part)
				# print(type(msg))
				# print('k',msg.keys())
				# print('v',msg.values())
				# print(msg.items())
				
				# for ijk in msg.items():
					# print(ijk)
					# print('\n')
				# print(msg[0])
				
		# typ, dd = mail.fetch(str(i), '(BODY.PEEK[HEADER])'	)
		
		# for response_part in dd:
			# if isinstance(response_part, tuple):
				# msg = email.message_from_string(response_part[1].decode('utf-8'))
				
				# print('\n\n\n\n2',msg,len(msg),type(msg))
				# print('k',msg.keys())
				# print('v',msg.values())

		
				# if msg_from_cond not in msg['from']:
					# print('continue on ',msg['from'])
					# continue
				
				# file_content=None
				# file_name=None
				
				# for part in msg.walk():
						
					# if part.get_content_type() == 'application/octet-stream':
						# file_name=part.get_filename()
						# file_name_datetime_str=file_name.replace(rep_fname,'').replace(rep_fname2,'')
						# str_file_date=file_name_datetime_str[0:4]+'-'+file_name_datetime_str[4:6]+'-'+file_name_datetime_str[6:8]
						

						# file_date= datetime.datetime.strptime(str_file_date,'%Y-%m-%d').date()
						
						# if file_date in proper_dates:
							# print('File from this date already in DB',file_date)
							# break
						
						# print('...Preparing for new file load',file_date)
						
						# if file_name and (file_name.endswith(fileformat)):
							# file_content=part.get_payload(decode=1)
							# save_file(file_name,file_content)
							# df=readxlsx2df(file_name,file_date)
							# write_data(df)
						# else:
							# file_name=None
							
				
				# email_subject = msg['subject']
				# email_from = msg['from']
				# print('From : ' + email_from + '\n')
				# print('Subject : ' + email_subject + '\n')












def is_conn_bad( mail_from, mail_from_pswd, SMTP_SERVER):
	print('checking mail_from, mail_from_pswd, SMTP_SERVER',mail_from, mail_from_pswd, SMTP_SERVER)
	try:
		mail = imaplib.IMAP4_SSL(SMTP_SERVER)
		mail.login(mail_from,mail_from_pswd)
		mail.select('inbox')
		print('$$$ EMAIL WORKS')
		return False # OK
	except:
		print('***\n***\n***\n *** EMAIL CONNECTION FAILED - POSSIBLE REASONS:\n 1. SOME ACTION MAY BE NEEDED AFTER LOGGING IN TO YOUR EMAIL (ENABLE IMAP or change security settings) \n2. YOU MAY HAVE TO INSTALL NEWER VERSION OF IMAPLIB IN PYTHON ')
		return True	










def verify_email_conn(DEAMON_DEFAULTS):
	
	print('DEAMON MODE ON - checking email ... ')

	if DEAMON_DEFAULTS["mail_from"].strip().lower()=='ask':
		DEAMON_DEFAULTS["mail_from"]=input("\nEnter mail_from: ")
		DEAMON_DEFAULTS["mail_from"]=DEAMON_DEFAULTS["mail_from"].lower()

		
	if DEAMON_DEFAULTS["mail_from_pswd"].strip().lower()=='ask':
		DEAMON_DEFAULTS["mail_from_pswd"]=input("\nEnter mail_from_pswd: ")
		DEAMON_DEFAULTS["mail_from_pswd"]=DEAMON_DEFAULTS["mail_from_pswd"].lower()
		
	connv=is_conn_bad(DEAMON_DEFAULTS["mail_from"], DEAMON_DEFAULTS["mail_from_pswd"], DEAMON_DEFAULTS["SMTP_SERVER"])
	
	if connv==False:
		return DEAMON_DEFAULTS
	
	print('! Mail box connection problem. One or all of following values are wrong:')
	print("... mail_from:"+DEAMON_DEFAULTS["mail_from"])
	print("... mail_from_pswd:"+DEAMON_DEFAULTS["mail_from_pswd"])
	print("... SMTP_SERVER:"+DEAMON_DEFAULTS["SMTP_SERVER"])
		
	want_edit=input("\nDo you want to edit these values or exit script? [edit/exit]: ")
	while want_edit not in ['edit','exit']:
		print("Wrong value, please use onlt 'edit' or 'exit'")
		want_edit=input("\nDo you want to edit these values or exit script? [edit/exit]: ")
	
	if want_edit.lower().strip()=='exit':
		exit()
		return -1
		
	badconniter=2
	
	while badconniter>0 and connv:
		print('! Changing mailbox connection values:')
		print("... mail_from:"+DEAMON_DEFAULTS["mail_from"])
		print("... mail_from_pswd:"+DEAMON_DEFAULTS["mail_from_pswd"])
		print("... SMTP_SERVER:"+DEAMON_DEFAULTS["SMTP_SERVER"])
		
		print("\nYou've got "+str(badconniter)+" more attempts...")
		
		DEAMON_DEFAULTS["mail_from"]=input("\nEnter mail_from: ")
		DEAMON_DEFAULTS["mail_from"]=DEAMON_DEFAULTS["mail_from"].lower()
		
		DEAMON_DEFAULTS["mail_from_pswd"]=input("\nEnter mail_from_pswd: ")
		DEAMON_DEFAULTS["mail_from_pswd"]=DEAMON_DEFAULTS["mail_from_pswd"].lower()
		
		DEAMON_DEFAULTS["SMTP_SERVER"]=input("\nEnter SMTP_SERVER: ")
		DEAMON_DEFAULTS["SMTP_SERVER"]=DEAMON_DEFAULTS["SMTP_SERVER"].lower()
		badconniter-=1
		connv=is_conn_bad(DEAMON_DEFAULTS["mail_from"], DEAMON_DEFAULTS["mail_from_pswd"], DEAMON_DEFAULTS["SMTP_SERVER"])

	if connv==False:
		return DEAMON_DEFAULTS
	
	if badconniter==0:
		print("\nCould not establish connection with mailbox - exit deamon ...")
		exit()		
		return -1
	
	
