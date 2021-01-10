import string
import random
import json

# Path to roles.json
ROLECONFIG = "C:\\Users\\Николай\\Desktop\\projects\\mafiabot\\game\\roles.json"

def generate_code(length):
    dic = string.ascii_uppercase + string.digits
    if type(length) == int:
        result = ''.join(random.choice(dic) for a in range(length))
        return result
    else:
        raise TypeError('Code length should be integer')


'''
    This class contains information about role properties
    in particular game. It also stores the information about
    number of players with this role.

    Quantity of Role object will be tremendous if more than 2 games is played at
    the same time. FIXME?
'''
class Role:
    def __init__(self, name, necessary, display_name=None, sleepless=False, hostile=False, minPlayers=5):
        self.name = name
        self.display_name = display_name
        self.sleepless = sleepless
        self.hostile = hostile
        self.necessary = necessary
        self.minPlayers = minPlayers

    def setAmount(self, amount):
        self.amount = amount

    def __repr__(self):
        return f'<Role object {self.name}>'


'''
    This class contain information about the player in the 
    particular game. It is not a core Discord user class
    substitute.
'''
class Player:
    def __init__(self, pid, name):
        self.id = pid
        self.order = 0
        self.name = name
        self.roundsSurvived = 0
        self.alive = True
        self.role = None
    
    def __repr__(self):
        return f'<Player:{self.id} {self.name}>'

'''
    This class contains information about a single game.
    It holds info about number of rounds passed, minimum and
    maximum player number, room size, etc.
'''
class Game:

    def __init__(self, minPlayers=5, maxPlayers=20, roleconfig=ROLECONFIG):
        self.id = generate_code(6) # FIXME

        self.rounds = 0

        self.players = []
        self.minPlayers = minPlayers
        self.maxPlayers = maxPlayers

        self.size = 0
        self.ready = False
        
        # State 0 — In lobby
        # State 1 - In game
        # State 2 - Finished
        self.state = 0

        self.readRolesConfig(roleconfig)

    def addPlayer(self, player):
        if self.state in (2, 1):
            raise Exception('This game is already finished or started.')
        if type(player) is not Player:
            raise TypeError('Trying to add a non-player instance!')
        if self.size == self.maxPlayers:
            raise Exception('Too many players!')

        self.players.append(player)
        self.size = len(self.players)

    def removePlayer(self, player):
        if self.state in (2, 1):
            raise Exception('This game is already finished or started.')
        if type(player) is not Player:
            raise TypeError('Trying to remove a non-player instance!')

        self.players.remove(player)
        self.size = len(self.players)

    def readRolesConfig(self, filename='roles.json'):
        with open(filename, 'r', encoding='utf-8') as file:
            rolesConf = json.load(file)
        

        r = {}
        for role in rolesConf:
            roleData = rolesConf[role]
            roleObj = Role(role, roleData['necessary'], roleData['display_name'], roleData['sleepless'],
                        roleData['hostile'], roleData['minPlayers'])

            # Amount of players with this role is zero by default
            roleObj.setAmount(0)

            if roleData.get("basic"):
                self.basicRole = roleObj
            else:
                r[role] = roleObj

        self.roles = r

    def setRole(self, rolename, amount):
        if rolename not in self.roles:
            raise Exception('This role is unknown!')
        if self.roles[rolename].minPlayers > self.size:
            raise Exception('Not enough players to add this role!')
        
        self.roles[rolename].amount = amount
        self._checkRoles()

    def getRoles(self):
        result = {}
        for role in self.roles:
            roleObj = self.roles[role]
            result[roleObj.name] = roleObj.amount
        return result

    def assignRoles(self):

        if self.state == 2:
            raise Exception('This game has already finished!')
        if self.minPlayers > self.size:
            raise Exception('Not enough players!')
        if not self.ready:
            raise Exception('Not enough necessary roles!')

        

        # This is the index for players list
        increment = 0

        # Firstly, we set all non-basic roles one by one.
        # But we need to shuffle players first.
        random.shuffle(self.players)
        for role in self.roles:
            
            roleObj = self.roles[role]
            left = roleObj.amount

            while left > 0:
                player = self.players[increment]
                player.role = roleObj
                left -= 1
                increment += 1

        # Other players get their basic role
        while increment < self.size:
            player = self.players[increment]
            player.role = self.basicRole
            increment += 1

        # Now we set the order number, also shuffled
        numbersPool = list(range(1, self.size+1))
        random.shuffle(numbersPool)
        for index, player in enumerate(self.players):
            player.order = numbersPool[index]

        # Not necessary, just for pretty-print
        self.players.sort(key=lambda x: x.order)

        for p in self.players:
            print(f'Order: {p.order} (ID{p.id}) | ROLE: {p.role.name}')


    def _checkRoles(self):
        ready = True
        for role in self.roles:
            roleObj = self.roles[role]
            if not roleObj.amount and roleObj.necessary and roleObj != self.basicRole:
                ready = False
        self.ready = ready



### Test unit ###

game = Game()

# Adding dummies
for i in range(10):
    game.addPlayer(Player(i, generate_code(6)))

# Setting the amount of players with non-basic roles.
# TODO: Use object instead of role name
# TODO: Game configs
game.setRole('mafia', 0)
game.setRole('detective', 3)

# Assign order numbers and roles according to game settings.
game.assignRoles()
