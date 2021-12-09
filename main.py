import random
import numpy as np
import matplotlib.pyplot as plt

popDensity = 10000
infectionUpperBound = 0.95
recoveryRate = 0.0002
infectableDistance = 0.2
stepLength = 1
simClock = 0
latticeWidth = 100
latticeHeight = 100
# 9 Directions for 2D Walk
directions = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]

def walk():
    return random.choice(directions)

def generateRandomCoords():
    return (np.random.uniform(0, latticeWidth - 1), np.random.uniform(0, latticeHeight - 1))

def initPopulation():
    people = []
    for i in range(popDensity - 1):
        (x, y) = generateRandomCoords()    
        people.append(Person(i, x, y))

    infectedPerson = Person(i, latticeWidth / 2, latticeHeight / 2)
    infectedPerson.infected = True
    people.append(infectedPerson)

    return people

class Person:
    def __init__(self, id, x, y):
        self.__id = id
        self.__x = float(x)
        self.__y = float(y)
        self.immune = False
        self.infected = False
        # Five Percent Chance of Re-Infection
        self.canRelapse = True if np.random.uniform(1,20) == 1 else False

    def getCoords(self):
        return (self.__x, self.__y)

    def __setCoords(self, x, y):
        self.__x = x
        self.__y = y

    def __enforceBoundary(self, dx, dy):
        dx = dx if self.__x + dx < latticeWidth else -dx
        dy = dy if self.__y + dy < latticeHeight else -dy

        return (dx, dy)

    def updateInfected(self, people):
        # See if Anyone Will Infect Me
        if(self.infected == False):
            for person in people:
                if(person.infected == True and self.withinInfectibleDistance(person) == True):
                    self.infected = True
                    break

        # See if I Will Infect Anyone
        if(self.infected == True):
            for person in people:
                if(person.infected == False and self.withinInfectibleDistance(person) == True):
                    person.infected = True
                    
                    # TODO: See if Recursing Here is Necessary
                    # person.updateInfected(people)

    def takeStep(self):
        (dx, dy) = walk()

        dx *= stepLength
        dy *= stepLength

        (dx, dy) = self.__enforceBoundary(dx, dy)

        self.__setCoords(self.__x + dx, self.__y + dy)

    def withinInfectibleDistance(self, person):
        (otherX, otherY) = person.getCoords()
        
        return np.sqrt((otherX - self.__x)**2 + (otherY - self.__y)**2) <= 2

    def getId(self):
        return self.__id

def renderPopulation(people):
    peopleCoords = [person.getCoords() for person in people]
    xs = [coords[0] for coords in peopleCoords]
    ys = [coords[1] for coords in peopleCoords]
    labels = [int(person.infected == True) for person in people]

    plt.title("Population")
    plt.scatter(xs, ys, c=labels, s=2, cmap='bwr')
    plt.pause(0.05)

def __main__():
    global simClock
    people = initPopulation()
    infectedPercent = 1 / popDensity
    prevInfected = infectedPercent

    while(infectedPercent < infectionUpperBound):
        for i in range(len(people)):
            if(infectedPercent > infectionUpperBound):
                break

            person = people[i]

            person.takeStep()

            person.updateInfected(people)

            infectedPercent = [person.infected for person in people].count(True) / popDensity
            simClock += 1

            if(prevInfected != infectedPercent):
                prevInfected = infectedPercent
                renderPopulation(people)
    
    renderPopulation(people)
    plt.show()

if __name__ == '__main__':
    __main__()