from catan_board import CatanBoard
from catan_player import CatanPlayer
from catan_statuses import CatanStatuses
from catan_cards import CatanCards
from catan_building import CatanBuilding

import random
import math

class CatanGame:
	
	# initializes the Catan game
	def __init__(self, num_of_players, on_win):
		
		# creates a board
		self.board = CatanBoard(game=self);
		
		# creates players
		self.players = []
		for i in range(num_of_players):
			self.players.append(CatanPlayer(num=i, game=self))
		
		self.on_win = on_win
		
		# creates a new Developement deck
		self.dev_deck = []
		for i in range(14):
			
			if i < 2:
				self.dev_deck.append(CatanCards.DEV_ROAD)
				self.dev_deck.append(CatanCards.DEV_MONOPOLY)
				self.dev_deck.append(CatanCards.DEV_YOP)
				
			if i < 5:
				self.dev_deck.append(CatanCards.DEV_VP)
				
			self.dev_deck.append(CatanCards.DEV_KNIGHT)
			
		# random.shuffle(self.dev_deck)
	
	# creates a new settlement belong to the player at the coodinates
	def add_settlement(self, player, r, i):
	
		# builds the settlement
		return self.players[player].build_settlement(settle_r=r, settle_i=i)
			
	# builds a road going from point start to point end
	def add_road(self, player, start, end):
		
		return self.players[player].build_road(start=start, end=end)
			
	# builds a new developement cards for the player
	def build_dev(self, player):
		
		# makes sure there is still at least one development card left
		if len(self.dev_deck) < 1:
			return CatanStatuses.ERR_DECK
			
		# makes sure the player has the right cards
		needed_cards = [
			CatanCards.CARD_WHEAT,
			CatanCards.CARD_ORE,
			CatanCards.CARD_SHEEP
		]
		if not self.players[player].has_cards(needed_cards):
			return CatanStatuses.ERR_CARDS
			
		# removes the cards
		self.players[player].remove_cards(needed_cards)
		
		# gives the player a dev card
		self.players[player].add_dev_card(self.dev_deck[0])
		
		# removes that dev card from the deck
		del self.dev_deck[0]
	
	# gives players the proper cards for a given roll
	def add_yield_for_roll(self, roll):
	
		self.board.add_yield(roll)
	
	# trades cards (given in an array) between two players	
	def trade(self, player_one, player_two, cards_one, cards_two):
	
		# check if they players have the cards they are trading
		# Needs to do this before deleting because one might have the cards while the other does not
		if not self.players[player_one].has_cards(cards_one):
			return CatanStatuses.ERR_CARDS
			
		elif not self.players[player_two].has_cards(cards_two):
			return CatanStatuses.ERR_CARDS
			
		else:
			# removes the cards
			self.players[player_one].remove_cards(cards_one)
			self.players[player_two].remove_cards(cards_two)
			
			# add the new cards	
			self.players[player_one].add_cards(cards_two)
			self.players[player_two].add_cards(cards_one)
			
			return CatanStatuses.ALL_GOOD
	
	# moves the robber
	def move_robber(self, r, i):
		self.board.move_robber(r, i)
	
	# trades cards from a player to the bank
	# either by 4 for 1 or using a harbor
	def trade_to_bank(self, player, cards, request):
		
		# makes sure the player has the cards
		if not (self.players[player]).has_cards(cards):
			return CatanStatuses.ERR_CARDS
		
		# checks all the cards are the same type
		card_type = cards[0]
		for c in cards[1:]:
			if c != card_type:
				return CatanStatuses.ERR_CARDS
		
		# if there are not four cards
		if len(cards) != 4:
			
			has_harbor = False
			# checks if the player has a settlement on the right type of harbor
			harbors = self.players[player].get_harbors()
			
			for h in harbors:
				if h == card_type:
					has_harbor = True
					break
					
			if not has_harbor:
				return CatanStatuses.ERR_HARBOR
				
					
		# removes cards
		(self.players[player]).remove_cards(cards)
		
		# adds the new card
		(self.players[player]).add_cards([request])
		
		return CatanStatuses.ALL_GOOD
		
	# gives the longest road to the correct player
	def set_longest_road(self):
		
		longest = 0
		owner = None
		
		for p in self.players:
			
			if p.longest_road_length > longest and p.longest_road_length > 4:
				
				longest = p.longest_road_length
				
				owner = self.players.index(p)
				
		return owner
		
	# changes a settlement on the board for a city
	def add_city(self, player, r, i):
	
		return self.board.upgrade_settlement(player, r, i)
		
	# uses a developement card
	def use_dev_card(self, player, card, args):
		
		# checks the player has the development card
		if not self.players[player].has_dev_cards([card]):
			return CatanStatuses.ERR_CARDS
		
		if card == CatanCards.DEV_ROAD:	
			
			# checks the correct arguments are given
			road_names = [
				"road_one",
				"road_two"
			]	
			for r in road_names:
				if not r in args:
					return CatanStatuses.ERR_INPUT
					
				else:
					if not "start" in args[r] or not "end" in args[r]:
						return CatanStatuses.ERR_INPUT
						
			# checks the road location is valid
			
			# whether the other road is completely isolated but is connected to this road
			other_road_is_isolated = False
			
			for r in road_names:

				location_status = self.players[player].road_location_is_valid(args[r]['start'], args[r]['end'])
				
				# if the road location is not OK
				# since the player can build two roads, some 
				# locations that would be invalid are valid depending on the other road location
				if not location_status == CatanStatuses.ALL_GOOD:
				
					# checks if it is isolated, but would be connected to the other road
					if location_status == CatanStatuses.ERR_ISOLATED:
						
						# if the other road is also isolated, just return an error
						if other_road_is_isolated:
							return location_status
						
						# checks if the two roads are connected 
						# (since the other one is connected, this road is connected through it)
						road_points = [
							"start",
							"end"
						]
						roads_are_connected = False
						for p_one in road_points:
							for p_two in road_points:
								if args["road_one"][p_one] == args['road_two'][p_two]:
									other_road_is_isolated = True
									
									# doesn't return an isolated error
									roads_are_connected = True
						
						if not roads_are_connected:			
							return location_status
					else:
						return location_status
				
			# builds the roads
			for r in road_names:
				self.board.add_road(CatanBuilding(point_one=args[r]["start"], point_two=args[r]["end"], owner=player, type=CatanBuilding.BUILDING_ROAD))	
				
			return CatanStatuses.ALL_GOOD
			
		elif card == CatanCards.DEV_KNIGHT:
			pass
			
		elif card == CatanCards.DEV_MONOPOLY:
			pass
			
		elif card == CatanCards.DEV_VP:
			pass
			
		elif card == CatanCards.DEV_YOP:
			pass
			
		else:
			# error here
			pass
		
		# applies the action
		
		# removes the card
		
		return CatanStatuses.ALL_GOOD
		
	# simulates 2 dice rolling
	def get_roll(self):
		return round(random.random() * 6) + round(random.random() * 6)
	
# creates a new game for debugging
if __name__ == "__main__":

	def win(player):
		print("Player %s wins!" % player)
		
	# creates a new game with three players
	c = CatanGame(num_of_players=6, on_win=win)
	
	# gives player 4 a settlement
	(c.players[4]).add_cards([
		CatanCards.CARD_WOOD,
		CatanCards.CARD_BRICK,
		CatanCards.CARD_WHEAT,
		CatanCards.CARD_SHEEP
	])
	
	status = c.add_settlement(player=4, r=3, i=0)
	
	if status != CatanStatuses.ALL_GOOD:
		print("Failed to build settlement with code %s" % status)
	# gives player 4 a six long road segment
	for i in range(6):
		(c.players[4]).add_cards([
			CatanCards.CARD_WOOD,
			CatanCards.CARD_BRICK
		])
		
		status = c.add_road(player=4, start=[3, i], end=[3, i + 1])
	
		if status != CatanStatuses.ALL_GOOD:
			print("Exited with status %s on loop %s" % (status, i))
	
	# prints player 4's longest road
	print("Printing Player 4's longest road")
	print((c.players[4]).longest_road_length)
	
	# prints the longest road owner
	print("The longest road belongs to player:")
	print(c.set_longest_road())
	
	# gives player 5 a settlement
	(c.players[5]).add_cards([
		CatanCards.CARD_WOOD,
		CatanCards.CARD_BRICK,
		CatanCards.CARD_WHEAT,
		CatanCards.CARD_SHEEP
	])
	
	stat = c.add_settlement(player=5, r=4, i=2)
	print("Player 5 building settlement is %s" % stat)
	
	# gives player 5 a 10 long looping road segment
	points = []
	for count in range(10):
		(c.players[5]).add_cards([
			CatanCards.CARD_WOOD,
			CatanCards.CARD_BRICK
		])
		
		r = math.floor(count / 5) + 4
		
		i = int(5 - math.fabs(count - 4))
		
		points.append([r, i])
	
	for index in range(len(points)):
	
		end_index = (index + 1) % len(points)
		status = c.add_road(player=5, start=points[index], end=points[end_index])
	
		if status != CatanStatuses.ALL_GOOD:
			print("Exited with status %s on loop %s when building a road from %s, %s to %s, %s" 
			% (status, index, points[index][0], points[index][1], points[end_index][0], points[end_index][1]))
	
	print("Longest road owner is now %s" % c.set_longest_road())
	print("Player 5's longest road is %s" % (c.players[5]).longest_road_length)
	
	(c.players[1]).add_cards([
		CatanCards.CARD_WOOD,
		CatanCards.CARD_WHEAT,
		CatanCards.CARD_BRICK,
		CatanCards.CARD_SHEEP
	])
	
	c.add_settlement(player=1, r=1, i=3)
	
	c.move_robber(r=0, i=1)
	print("Player 1 cards before")
	CatanPlayer.print_cards((c.players[1]).cards)
	
	c.add_yield_for_roll(3)
	print("Player 1 cards after")
	CatanPlayer.print_cards((c.players[1]).cards)
	
	# moves the robber away
	c.move_robber(r=0, i=0)
	
	# gives player 1 a city
	(c.players[1]).add_cards([
		CatanCards.CARD_WHEAT,
		CatanCards.CARD_WHEAT,
		CatanCards.CARD_ORE,
		CatanCards.CARD_ORE,
		CatanCards.CARD_ORE
	])
	
	status = c.add_city(player=1, r=1, i=3)
	print("Status for upgrading a city is %s. Cards are below:" % status)
	CatanPlayer.print_cards(c.players[1].cards)
	
	# checks the city gives twice the nubmer of cards
	c.add_yield_for_roll(3)
	
	CatanPlayer.print_cards(c.players[1].cards)
	
	# gives player 1 a developement card
	(c.players[1]).add_cards([
		CatanCards.CARD_WHEAT,
		CatanCards.CARD_ORE,
		CatanCards.CARD_SHEEP
	])
	
	c.build_dev(player=1)
	
	print(c.players[1].dev_cards)
	
	build_res = c.use_dev_card(player=1, card=CatanCards.DEV_ROAD, args={
		"road_one": {
			"start": [1, 3],
			"end":	[1, 2]
		},
		"road_two": {
			"start": [1, 2],
			"end": [1, 1]
		}
	})
	
	if build_res == CatanStatuses.ALL_GOOD:
		print("Successfully used a build road dev card")
		
	else:
		print("Build road unsuccessfull with error %s" % build_res)