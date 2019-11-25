# maze

class Maze:
    
    def __init__(self, filename):
        # read the matrix
        with open(filename, 'r') as file:
            matrix = []
            for row_string in file:
                row_string = row_string.strip()
                if not row_string:
                    continue
                row = []
                for char in row_string:
                    if char == ' ':
                        continue
                    wall_num = int(char)
                    if wall_num not in (0, 1, 2, 3):
                        raise RuntimeError("Illegal format!")
                    row.append(wall_num)
                row = tuple(row)
                matrix.append(row)
                if len(row) != len(matrix[0]):
                    raise RuntimeError("Illegal format!")
            matrix = tuple(matrix)
        
        # compute size
        pillar_row_count = len(matrix)
        if pillar_row_count > 0:
            pillar_col_count = len(matrix[0])
        else:
            pillar_col_count = 0
        
        # attributes assignment
        self.matrix = matrix
        self.pillar_row_count = pillar_row_count
        self.pillar_col_count = pillar_col_count
        self.cell_row_count = max(pillar_row_count - 1, 0)
        self.cell_col_count = max(pillar_col_count - 1, 0)
    
    def pillar_indices(self):
        for row in range(self.pillar_row_count):
            for col in range(self.pillar_col_count):
                yield row, col
    
    def wall_indices(self):
        for row in range(self.cell_row_count + 1):
            for col in range(self.cell_col_count + 1):
                for hv in range(2):
                    yield row, col, hv
    
    def wall(self, row, col, hv):
        if hv == 0:
            return self.wall_h(row, col)
        elif hv == 1:
            return self.wall_v(row, col)
        else:
            raise RuntimeError("the parameter hv should be 0 (horizontal) or 1 (vertical).")
    
    def wall_h(self, row, col):
        return self.matrix[row][col] in (1, 3)
    
    def wall_v(self, row, col):
        return self.matrix[row][col] in (2, 3)
    
    def wall_u(self, row, col):
        return self.wall_h(row, col)
    
    def wall_d(self, row, col):
        return self.wall_u(row + 1, col)
    
    def wall_l(self, row, col):
        return self.wall_v(row, col)
    
    def wall_r(self, row, col):
        return self.wall_l(row, col + 1)
    
    def cell_indices(self):
        for row in range(self.cell_row_count):
            for col in range(self.cell_col_count):
                yield row, col
    
    def con_u(self, row, col):
        return not self.wall_u(row, col)
    
    def con_d(self, row, col):
        return not self.wall_d(row, col)
    
    def con_l(self, row, col):
        return not self.wall_l(row, col)
    
    def con_r(self, row, col):
        return not self.wall_r(row, col)
    
    def __str__(self):
        chars_img = full_array_2d((self.cell_row_count + 1) * 2, (self.cell_col_count + 1) * 2, '┼')
        for row in range(self.cell_row_count + 1):
            for col in range(self.cell_col_count + 1):
                x = col * 2 + 1
                y = row * 2 + 1
                chars_img[y][x] = ' '
                if self.wall_h(row, col):
                    chars_img[y - 1][x] = '─'
                else:
                    chars_img[y - 1][x] = ' '
                
                if self.wall_v(row, col):
                    chars_img[y][x - 1] = '│'
                else:
                    chars_img[y][x - 1] = ' '
        string = ""
        for line in chars_img:
            for item in line[:-1]:
                string += item
            string += "\n"
        return string


# directions

U = 0
L = 1
D = 2
R = 3


# computing

def find_gates(maze: Maze):
    gates = []
    lobbies = []
    for row in range(maze.cell_row_count):
        if not maze.wall_v(row, 0):
            gates.append((row, 0, 1))
            lobbies.append((row, 0))
        if not maze.wall_v(row, maze.cell_col_count):
            gates.append((row, maze.cell_col_count, 1))
            lobbies.append((row, maze.cell_col_count - 1))
    for col in range(maze.cell_col_count):
        if not maze.wall_h(0, col):
            gates.append((0, col, 0))
            lobbies.append((0, col))
        if not maze.wall_h(maze.cell_row_count, col):
            gates.append((maze.cell_row_count, col, 0))
            lobbies.append((maze.cell_row_count - 1, col))
    return tuple(gates), tuple(set(lobbies))


def traverse_pillars(maze: Maze):
    groups = []
    belonging_group = full_array_2d(maze.pillar_row_count, maze.pillar_col_count, None)
    for start_row, start_col in maze.pillar_indices():
        if belonging_group[start_row][start_col] is not None:
            continue
        new_group = [(start_row, start_col)]
        belonging_group[start_row][start_col] = new_group
        groups.append(new_group)
        
        start_node = [start_row, start_col, -1]
        route = [start_node]
        while len(route) > 0:
            this_node = route[-1]
            this_node[2] += 1
            this_row, this_col, this_direction = this_node
            this_group = belonging_group[this_row][this_col]
            if this_direction == U:
                next_row = this_row - 1
                next_col = this_col
                if not next_row >= 0:
                    continue
                if not maze.wall_v(next_row, next_col):
                    continue
            elif this_direction == L:
                next_row = this_row
                next_col = this_col - 1
                if not next_col >= 0:
                    continue
                if not maze.wall_h(next_row, next_col):
                    continue
            elif this_direction == D:
                next_row = this_row + 1
                next_col = this_col
                if not next_row < maze.pillar_row_count:
                    continue
                if not maze.wall_v(this_row, this_col):
                    continue
            elif this_direction == R:
                next_row = this_row
                next_col = this_col + 1
                if not next_col < maze.pillar_col_count:
                    continue
                if not maze.wall_h(this_row, this_col):
                    continue
            else:
                route.pop()
                continue
            
            if belonging_group[next_row][next_col] is this_group:
                continue
            this_group.append((next_row, next_col))
            belonging_group[next_row][next_col] = this_group
            
            next_node = [next_row, next_col, -1]
            route.append(next_node)
    return groups


# computing old v2

def group_connected_cells(maze: Maze):
    class CellArea:
        def __init__(self):
            self.cells = []
    
    groups = []
    belonging_group = full_array_2d(maze.cell_row_count, maze.cell_col_count, None)
    for first_row, first_col in maze.cell_indices():
        if belonging_group[first_row][first_col] is not None:
            continue
        
        new_group = [(first_row, first_col)]
        groups.append(new_group)
        belonging_group[first_row][first_col] = new_group
        first_node = [(first_row, first_col), (neighbor_cells(maze, first_row, first_col)), -1]
        
        route = [first_node]
        while True:
            if len(route) == 0:
                break
            this_node = route[-1]
            
            this_node[2] += 1
            (this_row, this_col), options, index = this_node
            if not index < len(options):
                route.pop()
                continue
            next_row, next_col = options[index]
            
            this_group = belonging_group[this_row][this_col]
            next_group = belonging_group[next_row][next_col]
            if next_group is this_group:
                continue
            
            this_group.append((next_row, next_col))
            belonging_group[next_row][next_col] = this_group
            
            next_options = neighbor_cells(maze, next_row, next_col)
            next_node = [(next_row, next_col), next_options, -1]
            route.append(next_node)
    return groups


def split_by_accessibility(cell_groups, lobbies):
    accessible_groups = []
    inaccessible_groups = []
    for cell_group in cell_groups:
        if any(cell in lobbies for cell in cell_group):
            accessible_groups.append(cell_group)
        else:
            inaccessible_groups.append(cell_group)
    return accessible_groups, inaccessible_groups


# maze utils

def neighbor_walls(maze: Maze, row, col, hv):
    neighbors = []
    if hv == 0:
        neighbors.append((row, col, 1))
        if col < maze.cell_col_count:
            neighbors.append((row, col + 1, 1))
        if row > 0:
            neighbors.append((row - 1, col, 1))
            if col < maze.cell_col_count:
                neighbors.append((row - 1, col + 1, 1))
        if col > 0:
            neighbors.append((row, col - 1, 0))
        if col < maze.cell_col_count:
            neighbors.append((row, col + 1, 0))
    else:
        neighbors.append((row, col, 0))
        if row < maze.cell_row_count:
            neighbors.append((row + 1, col, 0))
        if col > 0:
            neighbors.append((row, col - 1, 0))
            if row < maze.cell_row_count:
                neighbors.append((row + 1, col - 1, 0))
        if row > 0:
            neighbors.append((row - 1, col, 1))
        if row < maze.cell_row_count:
            neighbors.append((row + 1, col, 1))
    neighbors = filter(lambda pos: maze.wall(*pos), neighbors)
    return tuple(neighbors)


def neighbor_cells(maze: Maze, row, col):
    neighbors = []
    if row > 0 and maze.con_u(row, col):
        neighbors.append((row - 1, col))
    if row < maze.cell_row_count - 1 and maze.con_d(row, col):
        neighbors.append((row + 1, col))
    if col > 0 and maze.con_l(row, col):
        neighbors.append((row, col - 1))
    if col < maze.cell_col_count - 1 and maze.con_r(row, col):
        neighbors.append((row, col + 1))
    return neighbors


# utils


def full_array_2d(row_count, col_count, value=None):
    matrix = []
    for row in range(row_count):
        matrix_row = []
        for col in range(col_count):
            matrix_row.append(value)
        matrix.append(matrix_row)
    return matrix


def full_array_3d(row_count, col_count, chan_count, value=None):
    matrix = []
    for row in range(row_count):
        matrix_row = []
        for col in range(col_count):
            item = []
            for chan in range(chan_count):
                item.append(value)
            matrix_row.append(item)
        matrix.append(matrix_row)
    return matrix


# main

def main():
    maze = Maze('./a2_sanity_check/maze_2.txt')
    print("the maze looks like:")
    print(maze)
    
    gates, lobbies = find_gates(maze)
    print("number of gates:", len(gates))
    # print("number of lobbies:", len(lobbies))
    
    pillar_groups = traverse_pillars(maze)
    print("number of connected groups of pillars:", len(pillar_groups))
    print("number of connected walls:", sum(len(g) > 1 for g in pillar_groups))
    
    cell_groups = group_connected_cells(maze)
    print("number of connected cells:", len(cell_groups))
    
    accessible_groups, inaccessible_groups = split_by_accessibility(cell_groups, lobbies)
    print("number of inner points:", sum(len(g) for g in inaccessible_groups))
    print("number of accessible area:", len(accessible_groups))
    
    # # print(Maze.getNumOfInaccessiblePoints())
    # initial, color = maze.traverse()
    #
    # for line in initial:
    #     print(line)
    # print(sum([sum([int(num == 0) for num in line]) for line in initial]))
    # print(color)
    # paths, cul_de_sacs = maze.getPaths(initial)
    # print("paths: ", paths)
    # print("cul_de_sacs: ", cul_de_sacs)


if __name__ == '__main__':
    main()
