import math
import random
import numpy as np
from numpy import array
import matplotlib.pyplot as plt

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
                ", loc: " + format(self.location, ".2f") + \
                ", ldr: " + str(self.leader.id if self.leader else -1) + "]"

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

def locationCloserToLeader(person, leader, move_coefficient):
    if not leader:
        return person.location
    #print("loc " + str(person))
    person_loc = person.location
    leader_loc = leader.location
    if person_loc < leader_loc:
        return (leader_loc - person_loc) * move_coefficient + person_loc
    else:
        return (person_loc - leader_loc) * (1 - move_coefficient) + leader_loc

def getFollowerCount(person, people):
    return len([f for f in people if f.leader and f.leader.id == person.id])

def calculateSulprus(person, people, growth_rate, sulprus_modifier_rate_min, sulprus_modifier_rate_max):
    # find followers
    follower_count = getFollowerCount(person, people)
    amount_for_followers = (follower_count * person.sulprus * person.generosity)
    sulprus_after_growth =  person.sulprus * (1 + growth_rate)
    modifier_rate = 1 + random.uniform(sulprus_modifier_rate_min, sulprus_modifier_rate_max)
    sulprus_after_modifiers = sulprus_after_growth * modifier_rate
    return sulprus_after_modifiers - amount_for_followers

def printLeaders(people):
    leader_list = [(p.id, getFollowerCount(p, people)) for p in people]
    print(leader_list)

def visualizeLocationsWithDots(people, location_min, location_max):
    field_size = 100
    people_count_per_location = [0 for i in range(0, field_size)]
    for p in people:
        loc_in_field = int((p.location - location_min) / location_max * field_size)
        people_count_per_location[loc_in_field] += 1
    print("".join([(" " if i == 0 else ".") for i in people_count_per_location]))

def visualizeLocationsWithCounts(people, location_min, location_max):
    field_size = 100
    people_count_per_location = [0 for i in range(0, field_size)]
    for p in people:
        loc_in_field = int((p.location - location_min) / location_max * field_size)
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

def pstdev(nums):
    mean = sum(nums) / len(nums)
    return math.sqrt(sum([(i - mean) * (i - mean) for i in nums]) / len(nums))

def locationPStddev(people):
    locations = [p.location for p in people]
    # using pstdev instead of stdev because we have the whole population, not a sample
    return pstdev(locations)

class Metrics:
    def __init__(self):
        self.current_round = 0
        self.metric_names = []

    def init(self, rounds):
        self.data = [ {} for r in range(rounds)]

    def addMetricName(self, name):
        self.metric_names.append(name)

    def nextRound(self):
        self.current_round = self.current_round + 1

    def addMetric(self, name, value):
        self.data[self.current_round][name] = value

    def plot(self):
        print(self.data)
        rounds = np.arange(0, len(self.data), 1)

        plt.figure(1)
        for i, metric_name in enumerate(self.metric_names):
            subplot_num = 211 + i
            plt.subplot(subplot_num)
            plt.title(metric_name)
            values = [kv[metric_name] for kv in self.data]
            plt.ylim(0, max(values))
            plt.plot(rounds, array(values))
        plt.show()

class GuanziExperiment:
    def __init__(self, metrics):
        ## constants ##

        self.rounds = 100
        self.num_people = 50
        self.generosity_min = 0.01
        self.generosity_max = 0.10
        self.starting_sulprus_min = 1000
        self.starting_sulprus_max = 10000
        # sulprus growth every round
        self.growth_rate = 0.05
        # sulprus modifications due to random events
        self.sulprus_modifier_rate_min = -0.20
        self.sulprus_modifier_rate_max = 0.20
        # 1 dimensional space
        self.location_min = 0
        self.location_max = 1000
        # How much of the distance (as a percentage) to cover to the leader each round
        self.move_coefficient = 0.3

        ## variables ##
        self.metrics = metrics
        self.metrics.init(self.rounds)
        self.metrics.addMetricName("location_pstdev")
        # Start with |num_people| people
        self.people = [self.randomPerson(i) for i in range(0, self.num_people)]

    def randomPerson(self, id):
        return Person(id,
                      random.randint(self.starting_sulprus_min, self.starting_sulprus_max),
                      random.uniform(self.generosity_min, self.generosity_max),
                      random.randint(self.location_min, self.location_max),
                      None)

    def runRound(self):
        # people for t(n-1)
        old_people = self.people
        # people for t(n)
        new_people = []
        for old_person in old_people:
            new_leader = findLeaderToFollow(old_people, old_person)
            new_location = locationCloserToLeader(old_person, new_leader, self.move_coefficient)
            # TODO consistent fn name style
            new_sulprus = calculateSulprus(old_person, old_people, self.growth_rate, self.sulprus_modifier_rate_min, self.sulprus_modifier_rate_max)
            new_people.append(Person(old_person.id, new_sulprus, old_person.generosity, new_location, new_leader))
        self.people = new_people

        #various ways to look at the data
        #print(str(self.people))
        #visualizeLocationsWithDots(self.people)
        visualizeLocationsWithCounts(self.people, self.location_min, self.location_max)
        #printLevels(self.people)
        #printLeaders(self.people)
        #print(locationPStddev(self.people))
        self.metrics.addMetric("location_pstdev", locationPStddev(self.people))
        self.metrics.nextRound()

    def runAllRounds(self):
        for round in range(0, self.rounds):
            print("ROUND " + str(round))
            self.runRound()

metrics = Metrics()
exp = GuanziExperiment(metrics)
exp.runAllRounds()
metrics.plot()
 
