# maze

class Maze:
    
    def __init__(self, filename):
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
            
            row_count = len(matrix) - 1
            if row_count < 0:
                row_count = 0
            
            if row_count > 0:
                col_count = (len(matrix[0]) - 1)
                if col_count < 0:
                    col_count = 0
            else:
                col_count = 0
        self.matrix = matrix
        self.row_count = row_count
        self.col_count = col_count
    
    def wall_indices(self):
        for row in range(self.row_count + 1):
            for col in range(self.col_count + 1):
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
        for row in range(self.row_count):
            for col in range(self.col_count):
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
        chars_img = full_array_2d((self.row_count + 1) * 2, (self.col_count + 1) * 2, '┼')
        for row in range(self.row_count + 1):
            for col in range(self.col_count + 1):
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


# computing

def find_gates(maze: Maze):
    gates = []
    lobbies = []
    for row in range(maze.row_count):
        if not maze.wall_v(row, 0):
            gates.append((row, 0, 1))
            lobbies.append((row, 0))
        if not maze.wall_v(row, maze.col_count):
            gates.append((row, maze.col_count, 1))
            lobbies.append((row, maze.col_count - 1))
    for col in range(maze.col_count):
        if not maze.wall_h(0, col):
            gates.append((0, col, 0))
            lobbies.append((0, col))
        if not maze.wall_h(maze.row_count, col):
            gates.append((maze.row_count, col, 0))
            lobbies.append((maze.row_count - 1, col))
    return tuple(gates), tuple(set(lobbies))


def group_connected_walls(maze: Maze):
    groups = []
    belonging_group = full_array_3d(maze.row_count + 1, maze.col_count + 1, 2, None)
    for first_row, first_col, first_hv in maze.wall_indices():
        if not maze.wall(first_row, first_col, first_hv):
            continue
        if belonging_group[first_row][first_col][first_hv] is not None:
            continue
        
        new_group = [(first_row, first_col, first_hv)]
        groups.append(new_group)
        belonging_group[first_row][first_col][first_hv] = new_group
        first_node = [(first_row, first_col, first_hv), (neighbor_walls(maze, first_row, first_col, first_hv)), -1]
        
        route = [first_node]
        while True:
            if len(route) == 0:
                break
            this_node = route[-1]
            
            this_node[2] += 1
            (this_row, this_col, this_hv), options, index = this_node
            if not index < len(options):
                route.pop()
                continue
            next_row, next_col, next_hv = options[index]
            
            this_group = belonging_group[this_row][this_col][this_hv]
            next_group = belonging_group[next_row][next_col][next_hv]
            if next_group is this_group:
                continue
            
            if next_group is not None:
                if len(this_group) >= len(next_group):
                    bigger_group, smaller_group = this_group, next_group
                else:
                    bigger_group, smaller_group = next_group, this_group
                groups.remove(smaller_group)
                bigger_group.extend(smaller_group)
                for row, col, hv in smaller_group:
                    belonging_group[row][col][hv] = bigger_group
                continue
            
            this_group.append((next_row, next_col, next_hv))
            belonging_group[next_row][next_col][next_hv] = this_group
            
            next_options = neighbor_walls(maze, next_row, next_col, next_hv)
            next_node = [(next_row, next_col, next_hv), next_options, -1]
            route.append(next_node)
    
    return groups


def group_connected_cells(maze: Maze):
    groups = []
    belonging_group = full_array_2d(maze.row_count, maze.col_count, None)
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
            
            if next_group is not None:
                if len(this_group) >= len(next_group):
                    bigger_group, smaller_group = this_group, next_group
                else:
                    bigger_group, smaller_group = next_group, this_group
                groups.remove(smaller_group)
                bigger_group.extend(smaller_group)
                for row, col in smaller_group:
                    belonging_group[row][col] = bigger_group
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


# computing old
# todo 这些函数还没转换，无法使用新的maze工作

def traverse(self):
    initial = [[0 for j in range(self.col_count)] for i in range(self.row_count)]
    color = 0
    cul_de_sac = 0
    for x in range(self.row_count):
        for y in range(self.col_count):
            cell = self.cells[x][y]
            if (x == 0 and y == 0) and (cell.left or cell.up) and initial[x][y] == 0:
                color += 1
                self.dfs(cell, initial, color)
                continue
            if (x == 0 and y == self.col_count - 1) and (cell.right or cell.up) and initial[x][
                y] == 0:
                color += 1
                self.dfs(cell, initial, color)
                continue
            if (x == self.row_count - 1 and y == 0) and (cell.left or cell.down) and initial[x][
                y] == 0:
                color += 1
                self.dfs(cell, initial, color)
                continue
            if (x == self.row_count - 1 and y == self.col_count - 1) and (cell.right or cell.down) and \
                    initial[x][y] == 0:
                color += 1
                self.dfs(cell, initial, color)
                continue
            if x == 0 and cell.up and initial[x][y] == 0:
                color += 1
                self.dfs(cell, initial, color)
                continue
            if x == self.row_count - 1 and cell.down and initial[x][y] == 0:
                color += 1
                self.dfs(cell, initial, color)
                continue
            if y == 0 and cell.left and initial[x][y] == 0:
                color += 1
                self.dfs(cell, initial, color)
                continue
            if y == self.col_count - 1 and cell.right and initial[x][y] == 0:
                color += 1
                self.dfs(cell, initial, color)
                continue
    return (initial, color)


def dfs(self, startCell, initial, color):
    x = startCell.x
    y = startCell.y
    initial[x][y] = color
    if x == 0:
        if y != self.col_count - 1:
            if startCell.right and initial[x][y + 1] == 0:
                initial[x][y + 1] = color
                self.dfs(self.cells[x][y + 1], initial, color)
        if startCell.down and initial[x + 1][y] == 0:
            initial[x + 1][y] = color
            self.dfs(self.cells[x + 1][y], initial, color)
        if y != 0:
            if startCell.left and initial[x][y - 1] == 0:
                initial[x][y - 1] = color
                self.dfs(self.cells[x][y - 1], initial, color)
    
    elif x == self.row_count - 1:
        if startCell.up and initial[x - 1][y] == 0:
            initial[x - 1][y] = color
            self.dfs(self.cells[x - 1][y], initial, color)
        if y != self.col_count - 1:
            if startCell.right and initial[x][y + 1] == 0:
                initial[x][y + 1] = color
                self.dfs(self.cells[x][y + 1], initial, color)
        if y != 0:
            if startCell.left and initial[x][y - 1] == 0:
                initial[x][y - 1] = color
                self.dfs(self.cells[x][y - 1], initial, color)
    elif y == 0:
        if startCell.right and initial[x][y + 1] == 0:
            initial[x][y + 1] = color
            self.dfs(self.cells[x][y + 1], initial, color)
        if x != 0:
            if startCell.up and initial[x - 1][y] == 0:
                initial[x - 1][y] = color
                self.dfs(self.cells[x - 1][y], initial, color)
        if x != self.row_count - 1:
            if startCell.down and initial[x + 1][y] == 0:
                initial[x + 1][y] = color
                self.dfs(self.cells[x + 1][y], initial, color)
    elif y == self.col_count - 1:
        if startCell.left and initial[x][y - 1] == 0:
            initial[x][y - 1] = color
            self.dfs(self.cells[x][y - 1], initial, color)
        if x != 0:
            if startCell.up and initial[x - 1][y] == 0:
                initial[x - 1][y] = color
                self.dfs(self.cells[x - 1][y], initial, color)
        if x != self.row_count - 1:
            if startCell.down and initial[x + 1][y] == 0:
                initial[x + 1][y] = color
                self.dfs(self.cells[x + 1][y], initial, color)
    else:
        if startCell.left and initial[x][y - 1] == 0:
            initial[x][y - 1] = color
            self.dfs(self.cells[x][y - 1], initial, color)
        if startCell.right and initial[x][y + 1] == 0:
            initial[x][y + 1] = color
            self.dfs(self.cells[x][y + 1], initial, color)
        if startCell.up and initial[x - 1][y] == 0:
            initial[x - 1][y] = color
            self.dfs(self.cells[x - 1][y], initial, color)
        if startCell.down and initial[x + 1][y] == 0:
            initial[x + 1][y] = color
            self.dfs(self.cells[x + 1][y], initial, color)


# 给定边界坐标，判断是否能出迷宫, 并返回能出的通道数
def is_out(self, x, y):
    num = 0
    cell = self.cells[x][y]
    if x == 0:
        if cell.up:
            num += 1
        if y == 0:
            num += int(cell.left)
        if y == self.col_count - 1:
            num += int(cell.right)
    elif x == self.row_count - 1:
        if cell.down:
            num += 1
        if y == 0:
            num += int(cell.left)
        if y == self.col_count - 1:
            num += int(cell.right)
    elif y == 0:
        num += int(cell.left)
    elif y == self.col_count - 1:
        num += cell.right
    return num


def getGates(self, x0, y0, initial, edges_points):
    gates = []
    for point in edges_points:
        x = point[0]
        y = point[1]
        if x != x0 & y != y0 and self.is_out(x, y) and initial[
            x][y] == initial[x0][y0]:
            gates.append(point)
    return gates


def getOtherPoints(self, x0, y0, initial):
    num = 0
    for x in range(self.row_count):
        for y in range(self.col_count):
            if (x != x0 or y != y0) and initial[x][y] == initial[x0][y0]:
                num += 1
    return num


def getPaths(self, initial):
    paths = 0
    cul_de_sacs = 0
    edges_points = \
        [[(0, y1) for y1 in range(self.col_count)] + [(self.row_count - 1, y2) for y2 in range(self.col_count)]
         + [(x1, 0) for x1 in range(1, self.row_count - 1)] + [(x2, self.col_count - 1) for x2 in
                                                               range(1, self.row_count - 1)]][0]
    visited = [[0 for j in range(self.col_count)] for i in range(self.row_count)]
    for point in edges_points:
        x = point[0]
        y = point[1]
        visited[x][y] = 1
        outs = self.is_out(x, y)
        if initial[x][y] == 0:
            continue
        if outs == 0:
            cul_de_sacs += 1
            continue
        if outs > 1:
            paths += 1
        gates = self.getGates(x, y, initial, edges_points)
        if len(gates) == 0:
            if self.getOtherPoints(x, y, initial):
                cul_de_sacs += 1
            continue
        if len(gates) == 1:
            paths += 1
            otherPoints = self.getOtherPoints(x, y, initial)
            
            if self.getOtherPoints(x, y, initial) > 1:
                cul_de_sacs += 1
            continue
    return (paths, cul_de_sacs)


def compute_culdesacs(self):
    culdesacs_groups = []
    belonging_group = [[None for c in range(self.col_count)] for r in range(self.row_count)]
    while True:
        changed = False
        for cell in self.cells:
            row = cell.y
            col = cell.x
            
            # todo uncomment it when implemented the accessibility check
            # if not self.accessible[row][col]:
            #     continue
            
            if belonging_group[row][col] is not None:
                continue
            
            neighbors = []
            if cell.up:
                neighbors.append((row - 1, col))
            if cell.down:
                neighbors.append((row + 1, col))
            if cell.right:
                neighbors.append((row, col + 1))
            if cell.left:
                neighbors.append((row, col - 1))
            
            neighbor_culdesacs_groups = []
            for neighbor_row, neighbor_col in neighbors:
                if not (0 <= neighbor_col < self.col_count and 0 <= neighbor_row < self.row_count):
                    continue
                neighbor_caldesacs_group = belonging_group[neighbor_row][neighbor_col]
                if neighbor_caldesacs_group is not None:
                    neighbor_culdesacs_groups.append(neighbor_caldesacs_group)
                    break
            
            if not len(neighbor_culdesacs_groups) >= len(neighbors) - 1:
                continue
            
            if len(neighbor_culdesacs_groups) == 0:
                merged_group = [(row, col)]
                culdesacs_groups.append(merged_group)
                belonging_group[row][col] = merged_group
                changed = True
            else:
                merged_group = max(neighbor_culdesacs_groups, key=lambda g: len(g))
                for group in neighbor_culdesacs_groups:
                    if group is merged_group:
                        continue
                    culdesacs_groups.remove(group)
                    merged_group.extend(group)
                    for removed_row, removed_col in group:
                        belonging_group[removed_row][removed_col] = merged_group
                
                merged_group.append((row, col))
        
        if not changed:
            break
    
    return culdesacs_groups, belonging_group


# maze utils

def neighbor_walls(maze: Maze, row, col, hv):
    neighbors = []
    if hv == 0:
        neighbors.append((row, col, 1))
        if col < maze.col_count:
            neighbors.append((row, col + 1, 1))
        if row > 0:
            neighbors.append((row - 1, col, 1))
            if col < maze.col_count:
                neighbors.append((row - 1, col + 1, 1))
        if col > 0:
            neighbors.append((row, col - 1, 0))
        if col < maze.col_count:
            neighbors.append((row, col + 1, 0))
    else:
        neighbors.append((row, col, 0))
        if row < maze.row_count:
            neighbors.append((row + 1, col, 0))
        if col > 0:
            neighbors.append((row, col - 1, 0))
            if row < maze.row_count:
                neighbors.append((row + 1, col - 1, 0))
        if row > 0:
            neighbors.append((row - 1, col, 1))
        if row < maze.row_count:
            neighbors.append((row + 1, col, 1))
    neighbors = filter(lambda pos: maze.wall(*pos), neighbors)
    return tuple(neighbors)


def neighbor_cells(maze: Maze, row, col):
    neighbors = []
    if row > 0 and maze.con_u(row, col):
        neighbors.append((row - 1, col))
    if row < maze.row_count - 1 and maze.con_d(row, col):
        neighbors.append((row + 1, col))
    if col > 0 and maze.con_l(row, col):
        neighbors.append((row, col - 1))
    if col < maze.col_count - 1 and maze.con_r(row, col):
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
    
    wall_groups = group_connected_walls(maze)
    print("number of connected walls:", len(wall_groups))
    
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
