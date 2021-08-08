We have 3 files- 
1) stake_in_colosseum_byzantine_case: Here, Byzantine case of 1 node declaring itself winner in Colosseum match, i.e, fake PoW case is handled. 
Run it like normal python program. Results of matches across tournaments are printed on screen. 

2) stake_in_colosseum_non_byzantine_case : Here, normal match are pllayed, assuming no Bynzatine nodes. Results are logged.
Run like normal python program. 

3) stake_in_colosseum_byzantine_case_2 : Same as stake_in_colosseum_byzantine_case.py, but here, number of nodes is 128, and alpha is 4. You can change alpha from line 9; and change the '129' in line 271 and 273 to be (2^(z)+1) to set number of players to be (2^(z)). Thus, alpha and number_of_players can be changed.


