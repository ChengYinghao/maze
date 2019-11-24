class Maze:
    def __init__(self, filename):
        self.walls = self.parse_file(filename)
        self.row_count = len(self.walls) - 1
        self.col_count = len(self.walls[0]) - 1
        
        self.accessible = None
    
    def can_u(self, row, col):
        return self.walls[row][col][0]
    
    def can_d(self, row, col):
        return self.walls[row + 1][col][0]
    
    def can_r(self, row, col):
        return self.walls[row][col + 1][1]
    
    def can_l(self, row, col):
        return self.walls[row][col][1]
    
    @property
    def cells(self):
        for row in range(self.row_count):
            for col in range(self.col_count):
                yield row, col
    
    @staticmethod
    def parse_file(filename):
        with open(filename, 'r') as file:
            walls = []
            for row_string in file:
                row_string = row_string.strip()
                if not row_string:
                    continue
                wall_row = []
                for char in row_string:
                    if char == ' ':
                        continue
                    wall_num = int(char)
                    wall_num_map = {0: (False, False), 1: (True, False), 2: (False, True), 3: (True, True)}
                    wall_h, wall_v = wall_num_map[wall_num]
                    wall_row.append((wall_h, wall_v))
                wall_row = tuple(wall_row)
                walls.append(wall_row)
                if len(wall_row) != len(walls[0]):
                    raise RuntimeError("Illegal format!")
            walls = tuple(walls)
            return walls
    
    def compute_accessible(self):
        # todo need to implement the accessibility check
        pass
    
    def compute_culdesacs_groups(self):
        culdesacs_groups = []
        belonging_group = [[None for c in range(self.col_count)] for r in range(self.row_count)]
        while True:
            changed = False
            for row, col in self.cells:
                # todo uncomment it when implemented the accessibility check
                # if not self.accessible[row][col]:
                #     continue
                
                if belonging_group[row][col] is not None:
                    continue
                
                neighbors = []
                if self.can_u(row, col):
                    neighbors.append((row - 1, col))
                if self.can_d(row, col):
                    neighbors.append((row + 1, col))
                if self.can_r(row, col):
                    neighbors.append((row, col + 1))
                if self.can_l(row, col):
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
            
            # culdesacs = [
            #     [
            #         (belonging_group[r][c] is not None)
            #         for c in range(maze.col_count)]
            #     for r in range(maze.row_count)]
            # for row in culdesacs:
            #     for cell in row:
            #         print("x" if cell else "o", end="")
            #     print()
            # print()
            
            if not changed:
                break
        
        return culdesacs_groups, belonging_group


maze = Maze('.\\a2_sanity_check\\maze_1.txt')
maze.compute_accessible()
_, belonging_group = maze.compute_culdesacs_groups()

culdesacs = [
    [
        (belonging_group[r][c] is not None)
        for c in range(maze.col_count)]
    for r in range(maze.row_count)]
for row in culdesacs:
    for cell in row:
        print("x" if cell else "o", end="")
    print()
print()
