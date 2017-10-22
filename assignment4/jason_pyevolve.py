import os  # JT+
import random

from pyevolve import Consts
from pyevolve import Crossovers
from pyevolve import G1DList
from pyevolve import GSimpleGA

random.seed(1024)
from math import sqrt

PIL_SUPPORT = None

try:
    from PIL import Image, ImageFont, ImageDraw

    PIL_SUPPORT = True
except:
    PIL_SUPPORT = False

cm = []
coords = []
# CITIES = 100
CITIES = 48  # JT+

WIDTH = 1024
HEIGHT = 768
LAST_SCORE = -1


def cartesian_matrix(coords):
    """

    :param coords:
    :return:
    """
    matrix = {}
    for i, (x1, y1) in enumerate(coords):
        for j, (x2, y2) in enumerate(coords):
            dx, dy = x1 - x2, y1 - y2
            dist = sqrt(dx * dx + dy * dy)
            matrix[i, j] = dist
    return matrix


def tour_length(matrix, tour):
    """ Returns the total length of the tour """
    total = 0
    t = tour.getInternalList()
    for i in range(CITIES):
        j = (i + 1) % CITIES
        total += matrix[t[i], t[j]]
    return total


def write_tour_to_img(coords, tour, img_file):
    """ The function to plot the graph """
    padding = 20
    coords = [(x + padding, y + padding) for (x, y) in coords]
    maxx, maxy = 0, 0
    for x, y in coords:
        maxx, maxy = max(x, maxx), max(y, maxy)
    maxx += padding
    maxy += padding
    img = Image.new("RGB", (int(maxx), int(maxy)), color=(255, 255, 255))
    font = ImageFont.load_default()
    d = ImageDraw.Draw(img)
    num_cities = len(tour)
    for i in range(num_cities):
        j = (i + 1) % num_cities
        city_i = tour[i]
        city_j = tour[j]
        x1, y1 = coords[city_i]
        x2, y2 = coords[city_j]
        d.line((int(x1), int(y1), int(x2), int(y2)), fill=(0, 0, 0))
        d.text((int(x1) + 7, int(y1) - 5), str(i), font=font, fill=(32, 32, 32))

    for x, y in coords:
        x, y = int(x), int(y)
        d.ellipse((x - 5, y - 5, x + 5, y + 5), outline=(0, 0, 0), fill=(196, 196, 196))
    del d
    img.save(img_file, "PNG")
    print "The plot was saved into the %s file." % (img_file,)


def G1DListTSPInitializator(genome, **args):
    """ The initializator for the TSP """
    lst = [i for i in xrange(genome.getListSize())]
    random.shuffle(lst)
    genome.setInternalList(lst)


def readCityCoordinatesFromFile(fileName="/Users/jasontellis/Google Drive/cs256/hw/assignment4/att48.tsp"):
    """
    Read cities' Co-ordinates from given file

    :param fileName: Name of file
    :return: A list of co-ordinates
    """

    DATASET_START_INDEX = 7  # First 6 lines of file are metadata
    cityCoordinates = []
    lineIndex = 0

    if os.path.isfile(fileName):

        with open(fileName, 'rb') as fileHandle:

            for line in fileHandle:

                lineIndex += 1
                if lineIndex >= DATASET_START_INDEX:  # Skip copying first 6 lines of metadata
                    cityIndex, xCoord, yCoord = line.split()
                    xCoord = (int)(xCoord)
                    yCoord = (int)(yCoord)
                    cityCoordinates.append((xCoord, yCoord))

    else:
        print("Invalid filename")
    return cityCoordinates


def main_run():
    global cm, coords, WIDTH, HEIGHT

    # coords = [(random.randint(0, WIDTH), random.randint(0, HEIGHT))
    #               for i in xrange(CITIES)]  #JT-

    coords = readCityCoordinatesFromFile()  # JT+

    cm = cartesian_matrix(coords)
    genome = G1DList.G1DList(len(coords))

    genome.evaluator.set(lambda chromosome: tour_length(cm, chromosome))
    genome.crossover.set(Crossovers.G1DListCrossoverEdge)
    genome.initializator.set(G1DListTSPInitializator)

    ga = GSimpleGA.GSimpleGA(genome)
    ga.setGenerations(1000)
    ga.setMinimax(Consts.minimaxType["minimize"])
    ga.setCrossoverRate(1.0)
    ga.setMutationRate(0.02)
    ga.setPopulationSize(80)

    ga.evolve(freq_stats=500)
    best = ga.bestIndividual()

    if PIL_SUPPORT:
        write_tour_to_img(coords, best, "tsp_result.png")
    else:
        print "No PIL detected, cannot plot the graph !"


if __name__ == "__main__":
    main_run()
