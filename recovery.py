import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

# Lattice is 1 sq. km, so each tick is 1/100 km, or 10m
popDensity = 10000
latticeWidth = 100
latticeHeight = 100

# 9 Directions for 2D Walk
directions = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]

# Simulation Parameters
infectionUpperBound = 0.95
recoveryRate = 0.0002
infectableDistance = 0.2 # 6 Feet (10m * 0.2)
stepLength = 0.15 # 5 Feet (10m * 0.15)

# Counters & State
simClock = 0
peopleCoords = list()
peopleCoordsX = np.zeros((popDensity))
peopleCoordsY = np.zeros((popDensity))
peopleLabels = np.zeros((popDensity))
distTree = None
casesOverTime = list()
peopleRecovered = list()
numberInfected = 0
numberImmune = 0
recoveryTime = 5
retainImmunity = False

def walk():
    return random.choice(directions)

def generateRandomCoords():
    return (np.random.uniform(0, latticeWidth - 1), np.random.uniform(0, latticeHeight - 1))

def initPopulation():
    global numberInfected
    people = []
    for i in range(popDensity - 1):
        (x, y) = generateRandomCoords()
        peopleCoords.append((x, y))
        peopleCoordsX[i] = x
        peopleCoordsY[i] = y
        people.append(Person(i, x, y))
    
    i += 1
    x = latticeWidth / 2
    y = latticeHeight / 2

    infectedPerson = Person(i, x, y)
    infectedPerson.infected = True

    peopleCoords.append((x, y))
    peopleCoordsX[i] = x
    peopleCoordsY[i] = y
    peopleLabels[i] = 1
    numberInfected += 1

    people.append(infectedPerson)
    return people

class Person:
    def __init__(self, id, x, y):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.immune = False
        self.infected = False
        self.newlyInfected = False
        self.prevInfected = False
        self.recoverTime = -1
        # Five Percent Chance of Re-Infection
        self.canRelapse = True if np.random.uniform(1,20) == 1 else False

    def getCoords(self):
        return (self.x, self.y)

    def __setCoords(self, x, y):
        self.x = x
        self.y = y
        peopleCoords[self.id] = (self.x, self.y)
        peopleCoordsX[self.id] = self.x
        peopleCoordsY[self.id] = self.y

    def __enforceBoundary(self, dx, dy):
        dx = dx if self.x + dx < latticeWidth and self.x + dx > 0 else -dx
        dy = dy if self.y + dy < latticeHeight and self.y + dy > 0 else -dy

        return (dx, dy)

    def takeStep(self):
        (dx, dy) = walk()

        dx *= stepLength
        dy *= stepLength

        (dx, dy) = self.__enforceBoundary(dx, dy)

        self.__setCoords(self.x + dx, self.y + dy)

def updateInfected(people):
    # Look At Everyone Around Us Within Infectible Distance to See Who We Infect
    global numberInfected
    visited = set()
    for idx in range(len(people)):
        person = people[idx]
        if person.infected is True and idx not in visited:
            res = distTree.query_ball_point(peopleCoords[idx], r=infectableDistance)

            for neighbor in res:
                if people[neighbor].infected is False and people[neighbor].immune is False:
                    visited.add(neighbor)
                    people[neighbor].infected = True
                    people[neighbor].prevInfected = True
                    people[neighbor].newlyInfected = True
                    numberInfected += 1
                    peopleLabels[neighbor] = 1


def immune(people):
    global simClock
    global recoveryTime
    global retainImmunity
    #See if any newly infected will recover in RecoveryTime 
    for i in range(len(people)):
        person = people[i]
        if person.infected is True and person.newlyInfected is True and random.randint(0,100) < 2:
          person.immune = True
          person.recoverTime = simClock + recoveryTime #Set the time the person will either become immune or recover
        if person.infected is True and person.immune is True and person.recoverTime == simClock:
            person.infected = False
            if retainImmunity is False and person.canRelapse is True:
                person.immune = False
                peopleLabels[i] = 0
            if retainImmunity is True:
                peopleLabels[i] = 0
        person.newlyInfected = False  


def render(infectedPercent):
    plt.cla()
    plt.title(f"Population at t={simClock}: {round(infectedPercent * 100, 2)}%")
    plt.scatter(peopleCoordsX, peopleCoordsY, c=peopleLabels, s=2, cmap='bwr')

    plt.pause(0.05)

def __main__():
    global simClock
    global distTree
    global numberInfected
    people = initPopulation()

    distTree = cKDTree(peopleCoords, leafsize=2)
    
    infectedPercent = 1 / popDensity

    while(infectedPercent < infectionUpperBound):
        for i in range(len(people)):
            if(infectedPercent > infectionUpperBound):
                break

            person = people[i]

            person.takeStep()

        updateInfected(people)
        
        immune(people)

        numberInfected = [person.infected for person in people].count(True)
        casesOverTime.append(numberInfected)
        infectedPercent =  numberInfected / popDensity
        
        numberRecovered = [person.infected is False and person.prevInfected is True for person in people].count(True)
        peopleRecovered.append(numberRecovered)
        
        simClock += 1

        print(simClock)
        if(simClock % 10 == 0):
            render(infectedPercent)

    render(infectedPercent)

    plt.figure(2)
    plt.title("Cases Over Time")
    plt.plot(casesOverTime)
    
    plt.figure(3)
    plt.title("People Recovered Over Time")
    plt.plot(peopleRecovered)

    plt.show()


if __name__ == '__main__':
    __main__()