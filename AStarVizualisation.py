import pygame
import math
from queue import PriorityQueue

# displaying
WID = 800
WIN = pygame.display.set_mode((WID, WID))
pygame.display.set_caption("A* Visualisation")

# colouring
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
PINK = (255, 0, 255)
GREY = (192, 192, 192)
AQUA = (64, 224, 208)


# visualisation tool
class Node:
    def __init__(self, row, col, width, t_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.t_rows = t_rows

    # position
    def get_pos(self):
        return self.row, self.col

    # check closed has this square been considered or checked
    def is_closed(self):
        return self.color == YELLOW

    # check if it is an open set
    def is_open(self):
        return self.color == GREEN

    # is this a barrier / wall
    def is_barrier(self):
        return self.color == GREY

    # start position
    def is_start(self):
        return self.color == BLUE

    # end position
    def is_end(self):
        return self.color == AQUA

    # reset to white
    def reset(self):
        self.color = WHITE

    # starts from start position
    def make_start(self):
        self.color = BLUE

    # closed makes to red square
    def make_closed(self):
        self.color = YELLOW

    # make open green
    def make_open(self):
        self.color = GREEN

    # make barrier grey
    def make_barrier(self):
        self.color = GREY

    # make the end turquoise
    def make_end(self):
        self.color = AQUA

    # make path purple
    def make_path(self):
        self.color = PINK

    # drawing on pygame rectangles
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    # updates neighbours
    def update_neighbors(self, grid):
        # neighbours list
        self.neighbors = []
        # checking if the row point is at is less than the total rows -1 to add one to the current row thus going down
        if self.row < self.t_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # going up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # going right
        if self.col < self.t_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # going left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    # less than handler for two spots being together
    def __lt__(self, other):
        return False


# heuristics function with manhattan distance etc.
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    # returning the absolute distance
    return abs(x1 - x2) + abs(y1 - y2)


# reconstructing the path
def reconstruct_path(came_from, current, draw):
    # while in list (came_from), make the path with draw
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


# AStar Algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    # add tot he priority queue
    open_set.put((0, count, start))
    # keeps track of where it has come from
    came_from = {}
    # table storing the g-scores
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0  # start g-score at 0
    # table for f-score
    f_score = {spot: float("inf") for row in grid for spot in row}
    # f-score will be the heuristic distance from h of the start position
    # estimates the distance for the end node (how far is it from the end point basically)
    f_score[start] = h(start.get_pos(), end.get_pos())

    # set to check if there is a value in the queue to keep track of items in the priority queue
    open_set_hash = {start}

    # while the open set is empty there is no path
    while not open_set.empty():
        # this allows the user to still quit if there is no end
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # current node is the start node
        current = open_set.get()[2]
        # removes the current node from the priority queue for no duplicates
        open_set_hash.remove(current)

        # check if this is the final node and then create the path
        if current == end:
            # show the shortest path
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        # looking at the neighbours of current node
        for neighbor in current.neighbors:
            # the current score +1 as we go one node over to the neighbour
            temp_g_score = g_score[current] + 1
            # if this is a better way to the end node, go this new way
            if temp_g_score < g_score[neighbor]:
                # update the came from value
                came_from[neighbor] = current
                # update g-score
                g_score[neighbor] = temp_g_score
                # update the heuristics score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                # if the neighbour is not in the open set hash, increment the count and add the neighbour to the set
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()
        # close if the current value is not the start node
        if current != start:
            current.make_closed()

    return False

# makes grid for app
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            # passing the wid and rows for appending
            spot = Node(i, j, gap, rows)
            grid[i].append(spot)
    # return the grid
    return grid


# makes the grid lines
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


# drawing function
def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


# where has the mouse clicked
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

# main class
def main(win, width):
    ROWS = 20   # rows needed
    grid = make_grid(ROWS, width)
    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)
        # loop and check what events are occurring
        for event in pygame.event.get():
            # if quitting the run ends
            if event.type == pygame.QUIT:
                run = False
            # if "left click" occurs add node
            if pygame.mouse.get_pressed()[0]:
                # get position clicked
                pos = pygame.mouse.get_pos()
                # gets the node that has been clicked
                row, col = get_clicked_pos(pos, ROWS, width)
                # index the row, column in the grid
                spot = grid[row][col]
                # if there is no start position in first, then add it first
                if not start and spot != end:
                    start = spot
                    start.make_start()
                # add the end position after the start position is made
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                # if the start and end have been added, then add the barrier node
                elif spot != end and spot != start:
                    spot.make_barrier()
            # if "right click" occurs remove clicked position
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None
            # if the space button is pressed start the algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            # updating all neighbours
                            spot.update_neighbors(grid)
                    # run a-star
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                # "c" clears the grid
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WID)
