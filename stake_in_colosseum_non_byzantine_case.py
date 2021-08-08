import logging
import random

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


players = {}
tournaments = {}

N_PLAYERS = 64
N_TOURNAMENTS = 4
ALPHA = 4
MAGIC_NO = 42           # Used as PoW, just a random number
                        # TODO: Change to randomly generated or something


class Tournament:

    def __init__(self, ID):
        self.id = ID                    # Tournament ID
        self.byzantine_players = []     # Current banned players
        self.round_no = 1


    def play(self):
        """
        Play the entire tournament

        Play for alpha no. of rounds, then allow the remaining layers to propose a block
        """

        # Initialize tournament
        logger.debug(f"{'#'*20} Initializing players for tournament {self.id} {'#'*20}")
        for p_id in players.keys():
            players[p_id].initTournament()

        # Play rounds
        logger.debug(f"Starting Rounds!")
        while self.round_no <= ALPHA:
            self.initRound()
            self.playRound()
            self.round_no+=1

        # Propose blocks
        logger.debug(f"Proposing blocks!")
        while True:
            p_id, _ = self.selectPlayer()
            if p_id is None:
                break

            players[p_id].proposeBlock()


    def initRound(self):
        """
        Init round for all players

        Currently only sets the players to not be paired with anyone
        """
        for p_id in players.keys():
            players[p_id].initRound()


    def playRound(self):
        """
        Play 1 complete round, by pairing players until not possible
        Single player left without any opponent automatically proceeds to next round
        """
        logger.info(f"Tournament - {self.id}, Round - {self.round_no}")

        matches = 0

        while True:
            p1_id, k1_id = self.selectPlayer()
            if p1_id is None:
                # No more pairs possible
                break

            logger.debug(f"Player 1 {p1_id}, Keeper 1 {k1_id}")

            # Mark this player as playing
            players[p1_id].isPairedInCurrTournament = True

            # Guaranteed that match is gonna be played
            matches+=1

            p2_id, k2_id = self.selectPlayer()
            if p2_id is None:
                # Single player remaining, mark as won and proceed to next round
                logger.info(f"Single player {p1_id} remaining")

                validator_id = self.getRandomPlayer([p1_id])
                self.markWinner(validator_id, (p1_id, k1_id))
                break

            logger.debug(f"Player 2 {p2_id}, Keeper 1 {k2_id}")
            players[p2_id].isPairedInCurrTournament = True

            # Select validator
            validator_id = self.getRandomPlayer([p1_id, p2_id])

            winner_pair = self.playMatch(validator_id, (p1_id, k1_id), (p2_id, k2_id))
            self.markWinner(validator_id, winner_pair)

        logger.info(f"Round {self.round_no}, {matches} matches completed")
        if self.byzantine_players:
            logger.debug(f"Byzantine players: {self.byzantine_players}")


    def selectPlayer(self):
        """
        Selects a valid player to play in the current round

        Player selected should have wins = round_no-1 and shouldn't be playing already
        Additionally, it should be valid player which is decided by the keeper (generated here)

        Returns:
            tuple: pair of (player_id, keeper_id), both None if not possible
        """
        for p_id, player in players.items():
            if p_id not in self.byzantine_players and \
                not player.isPairedInCurrTournament and player.wins==self.round_no-1:
                # Player is not paired currently, and has required wins
                # Validate using keeper
                keeper_id = self.getRandomPlayer([p_id])

                # logger.debug(f"ID: {p_id}, Keeper: {keeper_id}")
                if players[keeper_id].validatePlayer(p_id):
                    return (p_id, keeper_id)
                else:
                    # Byzantine player
                    self.byzantine_players.append(p_id)
                    continue

        return (None, None)


    def getRandomPlayer(self, denylist = []):
        """
        Get a random player id from the current players
        Optional argument of list of player IDs which can't be used
        """
        while True:
            player_id = random.choice(list(players.keys()))
            if player_id not in denylist:
                break

        return player_id

    def playMatch(self, validator_id, player_keeper_1, player_keeper_2):
        """
        Play a match, and decide the winner

        Args:
            validator_id (int): Validator ID for the match
            player_keeper_1 (tuple): Tuple of 1st (player_id, keeper_id)
            player_keeper_2 (tuple): Tuple of 2nd (player_id, keeper_id)

        Returns:
            tuple: Winner pair of (player_id, keeper_id)
        """
        logger.info(f"Validator: {validator_id}, PK1: {player_keeper_1}, PK2: {player_keeper_2}")
        # !!! TODO
        return player_keeper_1

    def markWinner(self, validator_id, player_keeper_pair):
        """
        Grant Proof-of-Win to the keeper, and player stores the Keeper_id

        Args:
            validator (int): Validator ID for the match
            player_keeper_1 (tuple): Tuple of winner (player_id, keeper_id)
        """
        logger.info(f"Winner - {player_keeper_pair}")
        p_id, k_id = player_keeper_pair
        players[k_id].storePoW(p_id, self.id, self.round_no, MAGIC_NO)
        players[p_id].storeKeeper(k_id, self.id, self.round_no)



class Node:
    def __init__(self, id, stake = 0):
        """
        Create Player Node with id & stake

        Args:
            id (int): Player id
            stake (int): Stake of the player, default 0
        """
        self.id = id
        self.stake = 1
        self.ps = 0                 # Used for some distance measurement to decide winner?
        self.isPairedInCurrTournament = False

        # PoW for past players with current player as keeper
        # [(player_id, tournament_no, round_no, PoW)]
        self.POW_list = []
        self.score_keeper = {}      # TODO: No idea what is this
        self.player_score = []      # List of (keeper_id, tournament_no, round_no) for which this player won
        self.wins = 0               # Count of no. of ins in curr_tournament

    def initTournament(self):
        """
        New tournament, set number of wins = 0
        """
        self.wins = 0

    def initRound(self):
        """
        New round, not paired currently
        """
        self.isPairedInCurrTournament = False


    def validatePlayer(self, player_id):
        """
        Validate player by querying past keepers. Current player is acting as a keeper

        Args:
            player_id (int): ID of player to be validated
        """
        player = players[player_id]

        for k_id, t_no, round_no in player.player_score:
            PoW = players[k_id].getPoW(player_id, t_no, round_no)

            # TODO: Change to random string or something
            if PoW != MAGIC_NO:
                logger.info(f"Invalid Player {player_id}, match - {k_id, t_no, round_no}"
                            f", PoW - {PoW} != {MAGIC_NO}")
                return False

        return True


    def getPoW(self, player_id, tournament_id, round_no):
        """
        Get PoW of a player of past match for which current player acted as keeper
        """
        for p_id, t_id, r_no, PoW in self.POW_list:
            if p_id==player_id and t_id==tournament_id and r_no==round_no:
                return PoW

        return None

    def storePoW(self, player_id, tournament_id, round_no, PoW):
        """
        Store PoW of the player it acted as keeper for
        """
        self.POW_list.append((player_id, tournament_id, round_no, PoW))

    def storeKeeper(self, keeper_id, tournament_id, round_no):
        """
        Player won, so store the id of keeper which has the PoW for the specific match

        Also increments the no. of wins in current tournament
        """
        self.player_score.append((keeper_id, tournament_id, round_no))
        self.wins+=1

    def proposeBlock(self):
        """
        Yay!
        """
        logging.info(f"Player {self.id} proposing block!")


def main():

    # Create players
    for i in range(N_PLAYERS):
        players[i] = Node(i)

    # Play some tournaments
    for tournament_no in range(N_TOURNAMENTS):
        tournaments[tournament_no] = Tournament(tournament_no)
        tournaments[tournament_no].play()


if __name__ == "__main__":
    main()
