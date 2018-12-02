import random

NUM_PEOPLE = 50

ROUNDS = 100

GENEROSITY_MIN = 0.01
GENEROSITY_MAX = 0.10

STARTING_SULPRUS_MIN = 1000
STARTING_SULPRUS_MAX = 10000

GROWTH_RATE = 0.05

# sulprus modifications due to random events
SULPRUS_MODIFIER_RATE_MIN = -0.20
SULPRUS_MODIFIER_RATE_MAX = 0.20

# 1 dimensional space
LOCATION_MIN = 0
LOCATION_MAX = 1000

# How much of the distance (as a percentage) to cover to the leader each round
MOVE_COEFFICIENT = 0.3

class Person:
    def __init__(self, id, sulprus, generosity, location, leader):
        self.id = id
        self.sulprus = sulprus
        self.generosity = generosity
        self.location = location
        self.leader = leader
    def __repr__(self):
        return "[ id: " + str(self.id) + \
                ", s:" + format(self.sulprus, ".2f") + \
                ", g: " + format(self.generosity, ".2f") + \
                ", lo: " + format(self.location, ".2f") + \
                ", le: " + str(self.leader.id if self.leader else -1) + "]"

def randomPerson(id):
    return Person(id,
                  random.randint(STARTING_SULPRUS_MIN, STARTING_SULPRUS_MAX),
                  random.uniform(GENEROSITY_MIN, GENEROSITY_MAX),
                  random.randint(LOCATION_MIN, LOCATION_MAX),
                  None)

def findLeaderToFollow(people, person):
    # sort |people| array by distance to |person|
    sorted_by_distance = sorted(people, key=lambda p: abs(person.location - p.location))
    #print("self + " + str(person))
    #print(sorted_by_distance)
    # find better leader

    previous_leader = person.leader

    # If leader follows you, they're not your leader any more (avoid cycles)
    if previous_leader and previous_leader.leader == person:
        previous_leader = None

    #print("prev " + str(previous_leader))
    previous_leader_score = person.leader.sulprus * person.leader.generosity if person.leader else 0
    #print("prev_sc " + str(previous_leader_score))

    for p in sorted_by_distance:
        if p != person and p.leader != person and (p.generosity * p.sulprus) > previous_leader_score:
            #print( "newleader: " + str(p))
            # New leader was found
            return p
    # keep the previous leader
    return None
            
def locationCloserToLeader(person, leader):
    if not leader:
        return person.location
    #print("loc " + str(person))
    person_loc = person.location
    leader_loc = leader.location
    if person_loc < leader_loc:
        return (leader_loc - person_loc) * MOVE_COEFFICIENT + person_loc
    else:
        return (person_loc - leader_loc) * (1 - MOVE_COEFFICIENT) + leader_loc

def modify_sulprus(sulprus):
    return sulprus * (1 + random.uniform(SULPRUS_MODIFIER_RATE_MIN, SULPRUS_MODIFIER_RATE_MAX))

def getFollowerCount(person, people):
    return len([f for f in people if f.leader and f.leader.id == person.id])

def calculate_sulprus(person, people):
    # find followers
    follower_count = getFollowerCount(person, people)
    amount_for_followers = (follower_count * person.sulprus * person.generosity)
    sulprus_after_modifiers = modify_sulprus(person.sulprus * (1 + GROWTH_RATE))
    return sulprus_after_modifiers - amount_for_followers

# Start with NUM_PEOPLE people
people = [randomPerson(i) for i in range(0, NUM_PEOPLE)]

def printLeaders(people):
    leader_list = [(p.id, getFollowerCount(p, people)) for p in people]
    print(leader_list)

def visualizeLocationsWithDots(people):
    field_size = 300
    people_count_per_location = [0 for i in range(0, field_size)]
    for p in people:
        loc_in_field = int((p.location - LOCATION_MIN) / LOCATION_MAX * field_size)
        people_count_per_location[loc_in_field] += 1
    print("".join([(" " if i == 0 else ".") for i in people_count_per_location]))

def visualizeLocationsWithCounts(people):
    field_size = 300
    people_count_per_location = [0 for i in range(0, field_size)]
    for p in people:
        loc_in_field = int((p.location - LOCATION_MIN) / LOCATION_MAX * field_size)
        people_count_per_location[loc_in_field] += 1
    print("".join([(" " if i == 0 else ("-" + str(i) + "-")) for i in people_count_per_location]))

def getLevelInHierarchy(person):
    # no leader means level = 0
    level = 0
    while person.leader != None:
        level += 1
        person = person.leader
    return level

def printLevels(people):
    for p in people:
        level = getLevelInHierarchy(p)
        print (str(p) + " -> " + str(level))

for round in range(0, ROUNDS):
    print("ROUND " + str(round))

    # people for t(n-1)
    old_people = people
    # people for t(n)
    new_people = []
    for old_person in old_people:
        new_leader = findLeaderToFollow(old_people, old_person)
        new_location = locationCloserToLeader(old_person, new_leader)
        new_sulprus = calculate_sulprus(old_person, old_people)
        # every ten rounds
        #if round % 10 == 0:
        #    new_sulprus = new_sulprus - 2000
        new_people.append(Person(old_person.id, new_sulprus, old_person.generosity, new_location, new_leader))
    people = new_people

    #various ways to look at the data
    #print(str(people))
    #visualizeLocationsWithDots(people)
    visualizeLocationsWithCounts(people)
    #printLevels(people)
    #printLeaders(people)