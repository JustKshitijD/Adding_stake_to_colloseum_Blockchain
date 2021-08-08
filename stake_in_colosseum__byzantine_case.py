import threading
import time
import random

ID={}

tournament_no=0
round_no=0
alpha=4

def get_validator():
	return(random.randint(1001,1000+len(ID)))   # a random ID from [1001,1000+len(ID)] is returned


class Node:
	def __init__(self, id):
		self.id=id
		self.isPairedInCurrRound=False
		self.curr_score=0
		#self.POW_list=[]
		self.score_keeper={}
		self.player_score={}
		self.bad_count=1                # (In how many tournaments has node been Byzantine+1)
		self.tot_score=0
		self.has_played_round=False
		#self.__opponent=0
		self.score_validator={}
		self.__validator_pow_list=[]    # private variable

	def check_if_qualified(self):                                 # Assume that player tells truth that it is qualifiedd or not
		if self.has_played_round:                                 #has played current round or not
			print(self.id," has played round earlier!")
			return False

		if(len(self.score_keeper)==0):                           # if score_keeper hash is empty, then no rounds were played
			if round_no==0:
				return True
			return False
		#curr_pow=self.POW_list[0]

		if (self.curr_score==round_no ):                          # only if node has won all rounds so far, is it qualified
			return True
		return False

	def init_fresh_tourn(self):
		self.score_keeper={}                     # In fresh tournament, all the 3 hashes are emptied
		self.player_score={}
		self.isPairedInCurrRound=False
		#self.POW_list=[]
		self.curr_score=0                       # Only curr_score made 0, not tot_score
		self.score_validator={}
		self.__validator_pow_list=[]

	def init_fresh_round(self):                   
		self.isPairedInCurrRound=False
		self.has_played_round=False

	def choose_keeper(self):                                                           
		if self.isPairedInCurrRound==True:         # get keeper. If player calling this function is already paired, return its own id           
			return(self.id)
		return(random.randint(1001,1000+len(ID)))

	def get_validator_pow_list(self):
		return self.__validator_pow_list	

	def keeper_checks_if_player_valid(self,i):
		t1=ID[i].check_if_qualified()
		if t1 is False:
			return False
		if(ID[i].curr_score==0):
			if round_no==0:
				#ID[i].__opponent=j	
				return True
			print("Error:- curr score of node ",i," is zero at non-zere round!")
			return False

		k=ID[i].curr_score
		flag=True
		while k>0:                         # incremented score is hashed in score_keeper
			keeper_id=0                    # check recursively backwards for absence or fake PoW for each score of rounds in tournament
			if k in ID[i].score_keeper.keys():
				keeper_id=ID[i].score_keeper[k]
			else:
				print("Error: POW is a fake, as no keeper alloted to latest score!")
				flag=False
				break	

			if (i,k) in ID[keeper_id].player_score.keys():	
				pow=ID[keeper_id].player_score[(i,k)]  # player_score has hash of [(player_id,score):POW]
			else:
				print("Error: POW is a fake, as keeper doesnt have record of (node,score)!")
				flag=False
				break


			if not(pow.tournament_no==tournament_no and pow.round_no==k-1 and pow.winner==i):  # score is 1 for round 0; winners get POW
				flag=False
				print("pow of score ",k," for node ",i," is invalid")
				break
			k=k-1


		if flag is False:
			return False
		#ID[i].__opponent=j	
		return True

	def verifier_checks_if_player_valid(self,i,win,j):
		if i==win:
			if not(ID[i].has_played_round):                      # not playedd round
				print("Error: Hasnt played round at all!")
				return False
			if ID[i].curr_score!=round_no+1:                     # since winner had got his curr_score incremented                
				print("Error: ID[i].curr_score!=round_no+1 for winner")
				return False

			# if(ID[i].curr_score==0):
			# 	if round_no==0:
			# 		#ID[i].__opponent=j	
			# 		return True
			# 	print("Error:- curr score of node ",i," is zero at non-zere round!")
			# 	return False

			vald=ID[i].score_validator[ID[i].curr_score]   # get validator id corresponding to curr_score
			lst=ID[vald].get_validator_pow_list()    # get pow_list from validator. pow_list in form (tournament_no,round_no,i,j)

			if (tournament_no,ID[i].curr_score-1,i,j) not in lst:    
				print("Fake PoW, as fair game was never played between nodes ",i," and ",j)
				flag=False
				return False

			k=ID[i].curr_score
			flag=True
			while k>0:                         # incremented score is hashed in score_keeper
				if k in ID[i].score_keeper.keys():
					keeper_id=ID[i].score_keeper[k]
				else:
					print("Error: Bad node ",i," ,a winner, as no keeper alloted to latest score!.")
					flag=False
					break	

				if (i,k) in ID[keeper_id].player_score.keys():	
					pow=ID[keeper_id].player_score[(i,k)]  # player_score has hash of [(player_id,score):POW]
				else:
					print("Error: Bad node ",i," , a winner,as keeper doesnt have record of (node,score)!")
					flag=False
					break

				if not(pow.tournament_no==tournament_no and pow.round_no==k-1 and pow.winner==i):
					flag=False
					print("pow of score ",k," for node ",i," is invalid")
					break
				k=k-1


			if flag is False:
				return False
			#ID[i].__opponent=j	
			return True	

		# else:
		# 	if not(ID[i].has_played_round):
		# 		print("Error: Hasnt played round at all!")
		# 		return False
		# 	if ID[i].curr_score!=round_no:
		# 		print("Error: ID[i].curr_score!=round_no for loser")
		# 		return False

		# 	# if(ID[i].curr_score==0):
		# 	# 	if round_no==0:
		# 	# 		#ID[i].__opponent=j	
		# 	# 		return True
		# 	# 	print("Error:- curr score of node ",i," is zero at non-zere round!")
		# 	# 	return False

		# 	k=ID[i].curr_score
		# 	flag=True
		# 	while k>0:                         # incremented score is hashed in score_keeper
		# 		if k in ID[i].score_keeper.keys():
		# 			keeper_id=ID[i].score_keeper[k]
		# 		else:
		# 			print("Error: Bad node ",i," ,a loser, as no keeper alloted to latest score!")
		# 			flag=False
		# 			break	

		# 		if (i,k) in ID[keeper_id].player_score.keys():	
		# 			pow=ID[keeper_id].player_score[(i,k)]  # player_score has hash of [(player_id,score):POW]
		# 		else:
		# 			print("Error: Bad node ",i," ,a loser, as no keeper alloted to latest score!")
		# 			flag=False
		# 			break

		# 		vald=ID[j].score_validator[ID[j].curr_score]
		# 		lst=ID[vald].get_validator_pow_list()

		# 		if (tournament_no,k-1,j,i) not in lst:
		# 			print("Fake PoW, as fair game was never played between nodes ",i," and ",j)
		# 			flag=False
		# 			break	


		# 		if not(pow.tournament_no==tournament_no and pow.round_no==k-1 and pow.winner==i):
		# 			flag=False
		# 			print("pow of score ",k," for node ",i," is invalid")
		# 			break
		# 		k=k-1


		# 	if flag is False:
		# 		return False
		# 	#ID[i].__opponent=j	
		# 	return True					

	def play_game(self,i,j,ii,jj):
		a=random.randint(1,10000)
		b=random.randint(1,10000)
		v=random.randint(1,10000)

		while a==b:
			b=random.randint(1,10000)
		while a==v or b==v:
			v=random.randint(1,10000)

		sc1=ID[i].tot_score/(ID[i].bad_count)
		print("Node i: ",i)
		print("sc1: ",sc1)
		sc2=ID[j].tot_score/(ID[j].bad_count)
		print("sc2: ",sc2)
		print("Node j: ",j)

		if(sc1>sc2):     # greater-one wins
			pow=POW(tournament_no,round_no,i,j)   
			ID[i].curr_score+=1
			ID[i].tot_score+=1
			k=ID[i].curr_score
			ID[i].score_keeper[k]=ii
			ID[ii].player_score[(i,k)]=pow
			print(i," wins!")
			self.__validator_pow_list.append((tournament_no,round_no,i,j))  # Thus, only way to append __validator_pow_list is if you play the game fairly, and only validator can change it from inside itself
			return i

			# k=ID[j].curr_score
			# ID[j].score_keeper[k]=jj
			# ID[jj].player_score[(j,k)]=pow
		else:
			pow=POW(tournament_no,round_no,j,i)
			ID[j].curr_score+=1
			ID[j].tot_score+=1   
			k=ID[j].curr_score
			ID[j].score_keeper[k]=jj
			ID[jj].player_score[(j,k)]=pow
			print(j," wins!")
			self.__validator_pow_list.append((tournament_no,round_no,j,i))
			return j

			# k=ID[i].curr_score
			# ID[i].score_keeper[k]=ii
			# ID[ii].player_score[(i,k)]=pow


class POW:
	def __init__(self,tournament_no,round_no,winner,loser):
		self.tournament_no=tournament_no
		self.round_no=round_no
		self.winner=winner
		self.loser=loser


if __name__=="__main__":
	#global tournament_no
	#global round_no
	#global alpha

	node_list=[]
	for i in range(1,65):
		node_list.append(Node(i+1000))  # id is 1001,1002,...1064
	for i in range(1,65):
		ID[i+1000]=node_list[i-1]

	st=time.time()

	while True:                          # Tournament played continuously
		round_no=0
		print("###############################################################################################")
		print("t= ",tournament_no)
		#print("start time of  tournament:- ",int(time.time()-st))
		for key in ID:
			ID[key].init_fresh_tourn() 

		for k in range(0,alpha):                  # alpha rounds
			print("-----------------------------------------------------------------------------------------")
			print("round_no: ",round_no)
			pairing_list=[]
			colluding_list=[]
			#round_no+=1
			for key in ID:
				ID[key].init_fresh_round()        # Every tournament gets fresh rounds
			for i in ID:                          # i,j are keys
				if ID[i].isPairedInCurrRound==False:                  #ID[i] definitely not paired in this round
					flag=True
					while True:                  # instead of iterating, can j be chosen randomly
						j=random.randint(1001,1000+len(ID))

						if i==j:
							continue
						ii=ID[i].choose_keeper() 
						jj=ID[j].choose_keeper()
						while((ii==jj) or (ii==i) or (jj==j)):
							ii=ID[i].choose_keeper()
							jj=ID[j].choose_keeper()

						keeper_a=ID[ii]    # keeper_a and keeper_b objects/nodes assigned
						keeper_b=ID[jj]

						print("i: ",i," ; j: ",j)

						v1=keeper_a.keeper_checks_if_player_valid(i)   # keeper checks if its pllayer is valid
						v2=keeper_b.keeper_checks_if_player_valid(j)

						if v1 is False:
							print(i," is invalid")
							flag=False
							break
						if v2 is False:
							print(j," is invalid")
							continue

						print(i," and ",j," play the game!!!!!!!!!!!!!!!!!!!")

						ID[i].has_played_round=True
						ID[j].has_played_round=True

						if random.random() < 0.2:                            # Byzantine with probability 0.2
							print("Entering fake play @@@")
							win=0
							if random.random() < 0.5:                        # Select winners amongst players i and j with probability 0.5
								win=i
								#pow_fake=POW(tournament_no,round_no,i,j)
								ID[i].curr_score+=1
								k=ID[i].curr_score
								ID[i].score_keeper[k]=ii
								ID[ii].player_score[(i,k)]=pow

							else:
								win=j
								#pow_fake=POW(tournament_no,round_no,j,i)
								ID[j].curr_score+=1
								k=ID[j].curr_score
								ID[j].score_keeper[k]=jj
								ID[jj].player_score[(j,k)]=pow     # (Node,score):POW in player_score hash


							vald=random.randint(1001,1000+len(ID))		# Validator selected
							ID[win].score_validator[ID[win].curr_score]=vald	  # winner node's score_validator hash is- [new incremented score: validator id]

							verifier=random.randint(1001,1000+len(ID))             # Verifier selected
							while verifier==i or verifier==j:
								verifier=random.randint(1001,1000+len(ID))

							vv1=ID[verifier].verifier_checks_if_player_valid(i,win,j)	 # verifier queries if match was fair or not
							vv2=ID[verifier].verifier_checks_if_player_valid(j,win,i)	

							if vv1 is False:
								print("Verifier i found that node ",i," was bad inside!")
								ID[i].bad_count+=1
								ID[j].has_played_round=False
								ID[i].has_played_round=False
								ID[i].curr_score-=1  # as i was winner
								continue
							if vv2 is False:
								print("Verifier j found that node ",j," was bad inside!")
								ID[j].bad_count+=1	
								ID[j].has_played_round=False
								ID[i].has_played_round=False
								ID[j].curr_score-=1      # as j was winner
								continue							


						pairing_list.append((i,j))
						val=get_validator()
						while(val==i or val==j):
							val=get_validator()

						win=ID[val].play_game(i,j,ii,jj)  
						if win==i:
							ID[i].score_validator[ID[i].curr_score]=val
						else:
							ID[j].score_validator[ID[j].curr_score]=val	


						verifier=random.randint(1001,1000+len(ID))
						while verifier==i or verifier==j:
							verifier=random.randint(1001,1000+len(ID))

						vv1=ID[verifier].verifier_checks_if_player_valid(i,win,j)	
						vv2=ID[verifier].verifier_checks_if_player_valid(j,win,i)

						if vv1 is False:
							print("Verifier found that node ",i," was bad!")
							ID[i].bad_count+=1
						if vv2 is False:
							print("Verifier found that node ",j," was bad!")
							ID[j].bad_count+=1	                         # bad count incremented


						flag=False
						break

				if flag is False:     
					continue

			print("pairing_list: ",pairing_list)                # FINAL BLOCK PROPOSERS
			print("len(pairing_list):- ",len(pairing_list))
			round_no+=1
		tournament_no+=1

		time.sleep(5)

    # if random.random() < 0.2:
	#     j=random.randint(1001,1000+len(ID))
	#     while i==j:
	#         j=random.randint(1001,1000+len(ID))
	#     ID[j].has_played_round=False
	#     if round_no==0:
	#         ID[j].score_keeper={}
	#         ID[j].player_score={}
	#
	#
	#     pow_fake=POW(tournament_no,round_no-1,j,1001)		
	
    # if random.random() < 0.2:
	#j=random.randint(1001,1000+len(ID))