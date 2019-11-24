class Cell:
    def __init__(self, x, y, left, right, up, down):
        self.x = x
        self.y = y
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        self.map = {0: self.left, 1: self.right, 2: self.up, 3: self.down}


class Maze:
    def __init__(self, input_file):
        self.cells = None
        self.file = input_file
        self.matrix = None
        self.rows = 0
        self.columns = 0
    
    def parse_file(self):
        with open(self.file, 'r') as f:
            new_lines = []
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    new_lines.append(line)
            new_lines = [new_line.split() for new_line in new_lines]
            if len(new_lines[0]) == 1:
                new_lines = [list(map(int, new_line[0])) for new_line in new_lines]
            matrix = [[int(num) for num in new_line] for new_line in new_lines]
        self.matrix = matrix
        self.rows = len(self.matrix) - 1
        self.columns = len(self.matrix[0]) - 1
        self.cells = [[0 for j in range(self.columns)] for i in range(self.rows)]
    
    def parse_cells(self):
        for i in range(self.rows):
            for j in range(self.columns):
                left = self.matrix[i][j] == 0 or self.matrix[i][j] == 1
                up = self.matrix[i][j] == 0 or self.matrix[i][j] == 2
                right = self.matrix[i][j + 1] == 0 or self.matrix[i][j + 1] == 1
                down = self.matrix[i + 1][j] == 0 or self.matrix[i + 1][j] == 2
                cell = Cell(i, j, left, right, up, down)
                self.cells[i][j] = cell
    
    def getNumOfGates(self):
        num = 0
        for x in range(self.rows):
            for y in range(self.columns):
                cell = self.cells[x][y]
                if x == 0 and y == 0:
                    num += int(cell.left) + int(cell.up)
                    continue
                if x == 0 and y == self.columns - 1:
                    num += int(cell.up) + int(cell.right)
                    continue
                if x == self.rows - 1 and y == 0:
                    num += int(cell.left) + int(cell.down)
                    continue
                if x == self.rows - 1 and y == self.columns - 1:
                    num += int(cell.right) + int(cell.down)
                    continue
                if x == 0:
                    num += int(cell.up)
                    continue
                if x == self.rows - 1:
                    num += int(cell.down)
                    continue
                if y == 0:
                    num += int(cell.left)
                    continue
                if y == self.columns - 1:
                    num += int(cell.right)
                    continue
            return num
    
    def traverse(self):
        initial = [[0 for j in range(self.columns)] for i in range(self.rows)]
        color = 0
        cul_de_sac = 0
        for x in range(self.rows):
            for y in range(self.columns):
                cell = self.cells[x][y]
                if (x == 0 and y == 0) and (cell.left or cell.up) and initial[x][y] == 0:
                    color += 1
                    self.dfs(cell, initial, color)
                    continue
                if (x == 0 and y == self.columns - 1) and (cell.right or cell.up) and initial[x][
                    y] == 0:
                    color += 1
                    self.dfs(cell, initial, color)
                    continue
                if (x == self.rows - 1 and y == 0) and (cell.left or cell.down) and initial[x][
                    y] == 0:
                    color += 1
                    self.dfs(cell, initial, color)
                    continue
                if (x == self.rows - 1 and y == self.columns - 1) and (cell.right or cell.down) and \
                        initial[x][y] == 0:
                    color += 1
                    self.dfs(cell, initial, color)
                    continue
                if x == 0 and cell.up and initial[x][y] == 0:
                    color += 1
                    self.dfs(cell, initial, color)
                    continue
                if x == self.rows - 1 and cell.down and initial[x][y] == 0:
                    color += 1
                    self.dfs(cell, initial, color)
                    continue
                if y == 0 and cell.left and initial[x][y] == 0:
                    color += 1
                    self.dfs(cell, initial, color)
                    continue
                if y == self.columns - 1 and cell.right and initial[x][y] == 0:
                    color += 1
                    self.dfs(cell, initial, color)
                    continue
        return (initial, color)
    
    def dfs(self, startCell, initial, color):
        x = startCell.x
        y = startCell.y
        initial[x][y] = color
        if x == 0:
            if y != self.columns - 1:
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
        
        elif x == self.rows - 1:
            if startCell.up and initial[x - 1][y] == 0:
                initial[x - 1][y] = color
                self.dfs(self.cells[x - 1][y], initial, color)
            if y != self.columns - 1:
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
            if x != self.rows - 1:
                if startCell.down and initial[x + 1][y] == 0:
                    initial[x + 1][y] = color
                    self.dfs(self.cells[x + 1][y], initial, color)
        elif y == self.columns - 1:
            if startCell.left and initial[x][y - 1] == 0:
                initial[x][y - 1] = color
                self.dfs(self.cells[x][y - 1], initial, color)
            if x != 0:
                if startCell.up and initial[x - 1][y] == 0:
                    initial[x - 1][y] = color
                    self.dfs(self.cells[x - 1][y], initial, color)
            if x != self.rows - 1:
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
            if y == self.columns - 1:
                num += int(cell.right)
        elif x == self.rows - 1:
            if cell.down:
                num += 1
            if y == 0:
                num += int(cell.left)
            if y == self.columns - 1:
                num += int(cell.right)
        elif y == 0:
            num += int(cell.left)
        elif y == self.columns - 1:
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
        for x in range(self.rows):
            for y in range(self.columns):
                if (x != x0 or y != y0) and initial[x][y] == initial[x0][y0]:
                    num += 1
        return num
    
    def getPaths(self, initial):
        paths = 0
        cul_de_sacs = 0
        edges_points = [[(0, y1) for y1 in range(self.columns)] + [(self.rows - 1, y2) for y2 in range(self.columns)]
                        + [(x1, 0) for x1 in range(1, self.rows - 1)] + [(x2, self.columns - 1) for x2 in
                                                                         range(1, self.rows - 1)]][0]
        visited = [[0 for j in range(self.columns)] for i in range(self.rows)]
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
        belonging_group = [[None for c in range(self.columns)] for r in range(self.rows)]
        while True:
            changed = False
            for row, col in self.cells:
                # todo uncomment it when implemented the accessibility check
                # if not self.accessible[row][col]:
                #     continue
                
                if belonging_group[row][col] is not None:
                    continue
                
                neighbors = []
                cell = self.cells[row, col]
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
                    if not (0 <= neighbor_col < self.columns and 0 <= neighbor_row < self.rows):
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
            
            maze = [[False for c in range(self.columns)] for r in range(self.rows)]
            for group in culdesacs_groups:
                for row, col in group:
                    maze[row][col] = True
            for row in maze:
                for cell in row:
                    print("x" if cell else "o", end="")
                print()
            print()
            
            if not changed:
                break
        
        return culdesacs_groups, belonging_group


maze = Maze('.\\a2_sanity_check\\maze_2.txt')
maze.parse_file()
print(maze.matrix)
maze.parse_cells()
# print(maze.getNumOfInaccessiblePoints())
initial, color = maze.traverse()

for line in initial:
    print(line)
print(sum([sum([int(num == 0) for num in line]) for line in initial]))
print(color)
paths, cul_de_sacs = maze.getPaths(initial)
print("paths: ", paths)
print("cul_de_sacs: ", cul_de_sacs)
