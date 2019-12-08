# wallet commands

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

import re

# ta funkcja czasem w petli i nieelegancko wychodzi w polaczeniu z 		list_unspent=all_t_addr_list()...
def get_t_balance(CLI_STR,test_addr):
	
	list_unspent=all_t_addr_list(CLI_STR) #json.loads( subprocess.getoutput(CLI_STR+" "+'listunspent') ) #
	test_balance=float(0)
	
	for lu in list_unspent:
		
		if lu["address"]==test_addr:
			test_balance+=float(lu["amount"])
			
	return test_balance
	
	
	
def get_t_addr_json(a1,list_unspent): # takes json a1 and json unspent


	for lu in list_unspent:
		cc=0
		for aa in a1:
			if lu["address"]==aa:
				break
			cc+=1
		# print('\n 569 checking',lu["address"],cc,len(a1))
		if cc==len(a1):
			a1.append(lu["address"])
			
	# print('560',a1)
	return a1
	
	

def address_aliases(addr_list): # address_aliases(get_wallet(True))
	alias_map={}
	for aa in addr_list:
		tmpa=aa[:3].lower()+aa[-3:].lower()
		iter=1
		while tmpa in alias_map.values():
			tmpa+=str(iter)
			iter+=1
		
		alias_map[aa]=tmpa #.append([aa, tmpa])
		
	return alias_map
	
	
	
# WALLET_DEFAULTS,DEAMON_DEFAULTS,
# list unspent nie jest bezpieczne do wyswietlania portfela
# gdy adres procesowany - ten ukryty jest gubiony ... 	
def get_wallet(CLI_STR,only_addr_list=False,or_addr_amount_dict=False):

	addr_list=[]
	addr_amount_dict={}
	total_balance=float(0)
	wl=[]
	amounts=[]
	r1=subprocess.getoutput(CLI_STR+" "+'getaddressesbyaccount ""')
	
	a1=json.loads(r1)
	
	list_unspent=all_t_addr_list(CLI_STR) #json.loads( subprocess.getoutput(CLI_STR+" "+'listunspent') ) 
	
	a1=get_t_addr_json(a1,list_unspent)
	# print(606,a1)
	
	for aa in a1:
		addr_list.append(aa)
		amount_init=get_t_balance(CLI_STR,aa)
		addr_amount_dict[aa]=amount_init
				
		if amount_init>0:
			wl.append("{:.8f}".format(amount_init)+" "+aa)
			amounts.append(amount_init)	
			total_balance+=amount_init
		else:
			wl.append("{:.8f}".format(0) +" "+aa)
			amounts.append(0)	
	
	r2=subprocess.getoutput(CLI_STR+" "+"z_listaddresses")
	
	a1=json.loads(r2)
	
	for aa in a1:
		addr_list.append(aa)
		tmp=subprocess.getoutput(CLI_STR+" "+'z_getbalance '+aa)
		tmp=float(tmp) #+float(random.random())
		addr_amount_dict[aa]=tmp
		total_balance+=tmp
		wl.append("{:.8f}".format(tmp)+" "+aa)
		amounts.append(tmp)
		
	alias_map=address_aliases(addr_list)
	
	if only_addr_list:
		return alias_map
		
	if or_addr_amount_dict:
		return addr_amount_dict
		
	wl2=[]
	for ww in wl:
		tmpw=ww.split(' ')
		tmpadr=tmpw[1]
		wl2.append( ww.replace(tmpadr, tmpadr+' alias:['+alias_map[tmpadr]+']' ) )
	
	wl=wl2	
		
	wl.append("=== Total === "+ "{:.8f}".format(total_balance) ) #str(total_balance)) #"{:.9f}".format(numvar)
	amounts.append(total_balance+1)
	
	wl=[wl[i[0]] for i in sorted(enumerate(amounts), key=lambda x:x[1], reverse=True)]
	
	
	return '\n'.join(wl)
	
	
	
def get_zaddr_history(CLI_STR,addr):
	
	v1=json.loads( subprocess.getoutput(CLI_STR+" "+'z_listreceivedbyaddress '+addr) )
	lz=[]
	lconfs=[]
	for zz in v1:
		mm=''
		if 'memo' in zz:
			# mm=zz["memo"].decode("hex")
			try:
				mm=''+str(bytes.fromhex(zz["memo"]).decode('utf-8')).strip(' \r\0')
			except:
				mm=''
		lz.append('Conf='+str(zz["confirmations"])+' amount='+str(zz["amount"])+' txid='+zz["txid"]+' memo:'+mm)
		lconfs.append(int(zz["confirmations"]))
		
	lz=[lz[i[0]] for i in sorted(enumerate(lconfs), key=lambda x:x[1], reverse=True)]
	
	return '\n'.join(lz)
	
	

# zastapic listunspent przez listtransactions - stamtad wziac wszystkie adresy ... 	
	

def all_t_addr_list(CLI_STR):
	
	listunspent=json.loads( subprocess.getoutput(CLI_STR+" "+'listunspent') ) 
	luaggr={}
	for lu in listunspent:
		if lu["address"] not in luaggr.keys():
			luaggr[lu["address"]]=lu["amount"]
		else:
			luaggr[lu["address"]]+=lu["amount"]
	
	# print(listunspent)
	v1=json.loads( subprocess.getoutput(CLI_STR+" "+'listreceivedbyaddress 1 true true') )
	addrl=[]
	# print(v1)
	tmpaddr=[]
	for zz in v1:
		# print(zz["address"])
		# lz.append(zz["address"]+' conf='+str(zz["confirmations"])+' amount='+str(zz["amount"]))
		initamount=float(0)
		if len(luaggr)>0:
			for kk,lu in luaggr.items():
				if kk==zz["address"]: #lu["address"]
					initamount+=lu #["amount"]
		
		tmpaddr.append(zz["address"])
		addrl.append({"address":zz["address"],"amount":initamount})
		
	# just in case addr in unspent but not in received ... 
	for kk,lu in luaggr.items():
		if kk not in tmpaddr:
			addrl.append({"address":kk,"amount":lu})
		
		# lconfs.append(int(zz["confirmations"]))
	return addrl
	
	
	
	
def get_taddr_history(CLI_STR,addr=None):
	
	v1=json.loads( subprocess.getoutput(CLI_STR+" "+'listreceivedbyaddress 1 true true') )
	# print(v1)
	lz=[]
	lconfs=[]
	
	for zz in v1:

		lz.append(zz["address"]+' conf='+str(zz["confirmations"])+' amount='+str(zz["amount"]))
		# taddr.append()
		lconfs.append(int(zz["confirmations"]))
		
	lz=[ lz[i[0]] for i in sorted(enumerate(lconfs), key=lambda x:x[1], reverse=True)]
	# print(lz)
	lz2=[]
	if addr!=None:
		
		for tt in lz:
			# print(tt,'vs',addr, (addr in tt))
			if addr in tt:
				lz2.append(tt)
		lz=lz2					
	
	return lz
	
	
	
	

	
def aliast_to_addr(alias_map,alias):
		
	# if alias in alias_map.values(): # addr_to is alias!
		# print(' alias detected')
	for oo in alias_map:
		if alias_map[oo]==alias:
			# addr_to=oo
			print('...alias['+alias+'] changed to addr ['+oo+']')
			return oo
				# break
	return alias
			
			
			
def isaddrvalid(CLI_STR,addr):
		
	tmp=''
	is_z=False
	
	if addr[0]=='z':
		tmp=subprocess.getoutput(CLI_STR+" "+'z_validateaddress '+addr)
		is_z=True
	else:
		tmp=subprocess.getoutput(CLI_STR+" "+'validateaddress '+addr)
		
	tmpj=json.loads(tmp)
			
	return tmpj['isvalid'],is_z
	
				
# if from list =[all] - take all
# if to_addr=any - take any z addr, if nonexistent - create one
# if list = aliast - replace with addr				
def merge_to(CLI_STR,from_dict,to_addr): #z_mergetoaddress '["ANY_SAPLING", "t1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd"]' 
	
	alias_map=address_aliases(get_wallet(CLI_STR,True))
	
	
	if to_addr in alias_map.values(): # addr_to is alias!
		print(' alias detected')
		to_addr=aliast_to_addr(alias_map,to_addr)	
	vv,isz=isaddrvalid(CLI_STR,to_addr)
	# print(740,vv,isz)
	if vv==False:
		return 'Not valid to_addr '+to_addr
	
	tmpstr='['
	
	for fl,flal in from_dict.items():
	
		if fl in alias_map.values(): # addr_to is alias!
			print(' alias detected')
			fl=aliast_to_addr(alias_map,fl)	
			
		#validate addr on the list
		vv,isz=isaddrvalid(CLI_STR,fl)
		if vv:
			tmpstr+='"'+fl+'",'
		else:
			print('Skip bad addr ',fl)	
	
	tmpstr+=']'
	tmpstr=tmpstr.replace(',]',']')
			
	tmpstr=tmpstr.replace('"','\\"')
		
	tmp_str=CLI_STR+" "+'z_mergetoaddress ' + tmpstr +' '+to_addr
	# print(tmp_str)
			
	tmp=subprocess.getoutput(tmp_str)
	
	return tmp
	
	
				
def get_any_zaddr(WALLET_DEFAULTS,CLI_STR):

	min_v_addr=''
	min_k_val=-1
	fee_v_addr=''
	for kk,vv in get_wallet(CLI_STR,or_addr_amount_dict=True).items():
		if kk[0]=='z':
			if fee_v_addr=='' and vv<=float(WALLET_DEFAULTS["fee"]):
				fee_v_addr=kk
			if min_v_addr=='':
				min_v_addr=kk
				min_k_val=vv
			elif vv<min_k_val:
				min_v_addr=kk
				
	if min_v_addr=='': #gen z addr
		return subprocess.getoutput(CLI_STR+" "+"z_getnewaddress" )
	else:
		if fee_v_addr=='':
			return min_v_addr
		else:
			return fee_v_addr
			
			

#####################################################################
####################### PROCESSING COMMANDS	
# WALLET_DEFAULTS,DEAMON_DEFAULTS,

def process_cmd(WALLET_DEFAULTS,DEAMON_DEFAULTS,CLI_STR,ucmd):

	ucmd=helpers.fix_equal(ucmd)

	
	if 'merge' in ucmd.lower():
		
		fromobj=helpers.get_key_eq_value(ucmd,'from')
		if "is missing in" in fromobj:
			return fromobj
			
		if fromobj.lower()=='all':
			fromobj=get_wallet(CLI_STR,True)	
		else:
			flist=fromobj.split(',')
			fromobj={}
			for ff in flist:
				fromobj[ff]=ff
		
		
		toobj=helpers.get_key_eq_value(ucmd,'to')
		if "is missing in" in toobj:
			return toobj
			
		if toobj.lower()=='any':
			# check z addr exist - best with = fee value or just any
			# if no z addr - create one CLI_STR,
			toobj=get_any_zaddr(WALLET_DEFAULTS,CLI_STR)
			print('any z addr',toobj)
			
		return merge_to(CLI_STR,fromobj,toobj)
	
	elif "history" in ucmd.lower(): # DODAC ZADDR + memo
	
		if ucmd.strip()=="history":
			print('show total history')
			
			# now only taddr:
			lz=get_taddr_history(CLI_STR)
			# print(str(lz))
			return 'Transactions for addr:\n'+('\n'.join(lz) )
		else:
			print('history for selected addr')
			tmp_addr=ucmd.split(' ')
			if len(tmp_addr)>1:
				addr=tmp_addr[1]
				
				alias_map=address_aliases(get_wallet(CLI_STR,True))
				if addr in alias_map.values(): # addr_to is alias!
					print(' alias detected')
					addr=aliast_to_addr(alias_map,addr)
				
				v12,isz=isaddrvalid(CLI_STR,addr)
				
				if v12!=True: #v1['isvalid']!=True and v2['isvalid']!=True:
					
					daddr=get_wallet(CLI_STR,True)
					laddr=[str(xx)+' alias:['+str(daddr[xx])+']'   for xx in daddr]
					return 'addr for history invalid, try one of these:\n'+('\n'.join(laddr))
					
				elif isz: #v1['isvalid']:
					return get_zaddr_history(CLI_STR,addr) # z_listreceivedbyaddress
				else:
					lz=get_taddr_history(CLI_STR,addr)
					# print(str(lz))
					return 'Transactions for addr:\n'+('\n'.join(lz) )					

	elif ucmd.lower()=="wallet":
	
		return get_wallet(CLI_STR)
		
	elif "validateaddress" in ucmd.lower():
	
		tmp=ucmd.split(" ")
	
		if len(tmp)==1:
			return "Address missing"
			
		elif len(tmp)==2 and tmp[0]=="validateaddress":
		
			tmpaddr=tmp[1]
			tmpb,isz=isaddrvalid(CLI_STR,tmpaddr)
			if tmpb:
				return 'Addr '+tmpaddr+' is valid'
			else:
				return '!! Addr '+tmpaddr+' NOT valid'
			
			
	elif "listunspent" == ucmd.lower():	
		
		tmp1=subprocess.getoutput(CLI_STR+" "+'z_listunspent ' )
		tmp2=all_t_addr_list(CLI_STR) #subprocess.getoutput(CLI_STR+" "+'listunspent ' )
		return str(tmp1)+'\n'+str(tmp2)
		
	elif "send" in ucmd.lower():	
	
		amount=helpers.get_key_eq_value(ucmd,'amount')
		if "is missing in" in amount:
			return amount
		
		if amount.lower()!='all':
			amount=float(amount)
		else:
			amount='all'
			
			
		alias_map=address_aliases(get_wallet(CLI_STR,True))	# can be useful for verifying both addr

		addr_to=helpers.get_key_eq_value(ucmd,'addr_to')
		
		if "is missing in" in addr_to:
			return addr_to
			
		if addr_to in alias_map.values(): # addr_to is alias!alias_map=address_aliases(get_wallet(True))
			print(' alias detected')
			addr_to=aliast_to_addr(alias_map,addr_to)
			
		# addr validation
		v12,isz=isaddrvalid(CLI_STR,addr_to)
		
		if v12!=True: #v1['isvalid']!=True and v2['isvalid']!=True:
			print('addr <to> not valid v1,v2',addr_to)
			return 'addr <to> not valid v12 '+str(addr_to)
			
			
			
			
		addr_from=helpers.get_key_eq_value(ucmd,'addr_from')
		if "is missing in" in addr_from:
			return addr_from
			
		
		if addr_from in alias_map.values(): # addr_to is alias!
			print(' alias detected')
			addr_from=aliast_to_addr(alias_map,addr_from)	
			
			
		# addr validation
		v12,isz=isaddrvalid(CLI_STR,addr_from)
		
		if v12!=True: #v1['isvalid']!=True and v2['isvalid']!=True:
			# print('addr from not valid v1,v2',v1,v2)
			return 'addr <to> not valid v12 '+str(addr_from)
			
		# print('addr_from',addr_from)
		# check balance:
		cur_balance=0
		if isz: #v1['isvalid']:
			cur_bal=subprocess.getoutput(CLI_STR+" "+'z_getbalance '+addr_from)
			cur_bal=round(float(cur_bal) ,8)
			if amount=='all':
				amount=round(cur_bal- float(WALLET_DEFAULTS["fee"]),8) #0.0001
			if cur_bal<amount:
				return "\n TX CANCELLED. Current balance requested addr is ["+str(cur_bal)+"] <= requested amount of ["+str(amount)+ "]"
				
		else: # v2['isvalid']:
			cur_bal=get_t_balance(CLI_STR,addr_from) #subprocess.getoutput(CLI_STR+" "+'getreceivedbyaddress '+addr_from)
			cur_bal=round(float(cur_bal)  ,8)
			# print('cur bal',cur_bal,addr_from)
			if amount=='all':
				amount=round(cur_bal-float(WALLET_DEFAULTS["fee"]) ,8) #0.0001
			if cur_bal<amount:
				return "\n TX CANCELLED. Current balance of requested addr is ["+str(cur_bal)+"] <= requested amount of ["+str(amount)+ "]"
		
		amount=round(amount,8)
			
		if amount<=float(WALLET_DEFAULTS["fee"]):
			return 'Amount '+str(amount)+' lower then fee '+str(WALLET_DEFAULTS["fee"])+' - wont process it.'
			
		check_limit=helpers.get_available_limited_balance(DEAMON_DEFAULTS)
		# print(amount,check_limit)
		if amount>check_limit:
			return 'Amount > limit = '+str(check_limit)+' Remeber about [tx_amount_limit]='+str(DEAMON_DEFAULTS["tx_amount_limit"])+' and tx_time_limit_hours='+str(DEAMON_DEFAULTS["tx_time_limit_hours"])
		
		left_balance=0
		
		if amount+float(WALLET_DEFAULTS["fee"])<cur_bal:
		
			left_balance=round(cur_bal-amount-float(WALLET_DEFAULTS["fee"]),8) # ENSURE LEFT BALANCE IS OK
			
			if left_balance+amount+float(WALLET_DEFAULTS["fee"]) >cur_bal:
			
				btmp=(left_balance+amount-cur_bal+float(WALLET_DEFAULTS["fee"]))
				left_balance=round(left_balance - btmp,8) 
				if left_balance+amount+float(WALLET_DEFAULTS["fee"])>cur_bal: # just in case ...
					left_balance=round(left_balance - 0.00000001,8)
					
			# print('***left_balance',left_balance)
		
		
		memo=helpers.get_key_eq_value(ucmd,'memo')
		if "is missing in" in memo:
			memo="Sent via KoReCo - Komodo Remote Controller"
		memo_hex=memo.encode('utf-8').hex()
			
		if isz: #v1['isvalid']:
			if addr_to[0]=='z':
				send_js_str='[{"address":"'+str(addr_to)+'","amount":'+str(amount)+',"memo":"'+str(memo_hex)+'"}]'  #, {"address":"'+str(addr_from)+'","amount":'+str(left_balance)+'}]'
			else:
				send_js_str='[{"address":"'+str(addr_to)+'","amount":'+str(amount)+'}]'
		else:
			if left_balance>0.00000001:
				send_js_str='[{"address":"'+str(addr_to)+'","amount": '+str(amount)+'} , {"address":"'+str(addr_from)+'","amount":'+str(left_balance)+'}]'
			else:
				send_js_str='[{"address":"'+str(addr_to)+'","amount": '+str(amount)+'}]'
			
		# print(send_js_str)
		send_js_str=send_js_str.replace('"','\\"')
		
		tmp_str=CLI_STR+" "+'z_sendmany "' + str(addr_from)+'" "'+send_js_str+'"'
		
		
		tmp=subprocess.getoutput(tmp_str)
		
		if isz: #v1['isvalid']:
			time.sleep(7)
		else:
			time.sleep(1)
			
		checkopstr="z_getoperationstatus "+'[\\"'+str(tmp)+'\\"]'
		
		opstat=subprocess.getoutput(CLI_STR+" "+checkopstr)
		# print(str(opstat))
		opstat_orig=opstat
		opstat=json.loads(opstat)[0]["status"]
		
		while opstat=="executing":
			print('... processing . .. ... ')
			time.sleep(7)
			checkopstr="z_getoperationstatus "+'[\\"'+str(tmp)+'\\"]'
		
			opstat=subprocess.getoutput(CLI_STR+" "+checkopstr)
			# print(str(opstat))
			opstat=json.loads(opstat)[0]["status"]
			opstat_orig=opstat
		
		if opstat=="success":
			
			helpers.sent_log_append(amount,addr_from,addr_to)
		else:
			print('FAILED opstat ',str(opstat_orig) )
			return 'FAILED\n'+str(opstat_orig)
		
		return ' SUCCESS \n' #str(tmp)+
		
	elif ucmd.lower()=="blocks":
		tmp=subprocess.getoutput(CLI_STR+" "+"getblockcount" )
		return ucmd+" "+str(tmp)
		
		
	elif ucmd.lower()=="newzaddr":
		tmp=subprocess.getoutput(CLI_STR+" "+"z_getnewaddress" )
		return ucmd+" "+str(tmp)
		
		
	elif ucmd.lower()=="newaddr":
		tmp=subprocess.getoutput(CLI_STR+" "+"getnewaddress" )
		return ucmd+" "+str(tmp)


	elif ucmd.lower()=="stop":
		tmplst=CLI_STR+" "+ucmd
		tmplst=tmplst.split(" ")
		subprocess.Popen(  tmplst  )
		time.sleep(7)
		print("Remote Control closed! Handling commands and blockchain download turned off.")
		
		
		return "Stopping deamon ... "
		
	elif ucmd.lower()=="listunconfirmed":
	
		
		dict_income=[]
		alias_map=address_aliases(get_wallet(CLI_STR,True))
		# print('\n\n\n',alias_map,'\n\n\n')
	
		mempool_list=subprocess.getoutput(CLI_STR+" "+"getrawmempool" )
		a1=json.loads(mempool_list)
		resp=''
		for aa in a1:
		
			tmp=subprocess.getoutput(CLI_STR+" "+'getrawtransaction '+aa+" 1")
			# print('1100',tmp)
			tmpj=json.loads(tmp)
			addtx=False
			
			for vin in tmpj["vin"]:
				# print('1105vin',vin)
			
				if "address" in vin.keys():
					# print("1108address in vin.keys()",vin["address"])
					# print('1109',alias_map.keys(),vin["address"] in alias_map.keys())
					if vin["address"] in alias_map.keys():
						# print('1107mempool vin found addr '+vin["address"])
						addtx=True
						break
			
				if addtx==False:
					for vo in tmpj["vout"]:
						if "addresses" in vo.keys():
							tmparr=vo["addresses"]
							for ttt in tmparr:
								if ttt in alias_map.keys():
									# print('1117mempool vout found addr '+vin["address"])
									addtx=True
									break
						if addtx:
							break
							
				if addtx:
					break
					
			# print(tmp)		
			# print('1121addtx',addtx)
			if addtx:
				resp+=tmp+'\n'
				# print('ok???',resp)
			# else:
				# z tx:
			addtx=False
			tmp=subprocess.getoutput(CLI_STR+" "+'z_viewtransaction '+aa)
			
			if tmp==None:
				continue
			elif 'error' in tmp:
				continue
			
			# print('*** processing z...',resp)
			tmpj=json.loads(tmp)
			for vo in tmpj["outputs"]:
				if "address" in vo.keys():
					tmparr=vo["address"]
					# for ttt in tmparr:
					if tmparr in alias_map.keys():
						# print('1148mempool vout found addr '+vo["address"])
						# print('found value',vo["value"])
						dict_income.append({ "to_addr":vo["address"], "amount":vo["value"], "from_addr":tmpj["spends"][0]["address"] })
						addtx=True
						# break
			if addtx:
				resp+=tmp+'\n'
		print(dict_income)
		return resp	
	
	elif "getrawtransaction" in ucmd.lower():	
		return subprocess.getoutput(CLI_STR+" "+ucmd)
		
	#z_getoperationstatus
	elif "z_getoperationstatus" in ucmd.lower():	
		return subprocess.getoutput(CLI_STR+" "+ucmd)
		
	else:
		print("else")
		return subprocess.getoutput(CLI_STR+" "+ucmd)
	

