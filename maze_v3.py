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
    
    def wall_h(self, row, col):
        return self.matrix[row][col] in (1, 3)
    
    def wall_v(self, row, col):
        return self.matrix[row][col] in (2, 3)
    
    def con_u(self, row, col):
        return not self.wall_h(row, col)
    
    def con_d(self, row, col):
        return not self.wall_h(row + 1, col)
    
    def con_l(self, row, col):
        return not self.wall_v(row, col)
    
    def con_r(self, row, col):
        return not self.wall_v(row, col + 1)
    
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


def rev(direction):
    return {U: D, D: U, R: L, L: R}[direction]


# computing

def find_gates(maze: Maze):
    gates = []
    for row in range(maze.cell_row_count):
        if maze.con_l(row, 0):
            gates.append((row, 0, L))
        if maze.con_r(row, maze.cell_col_count - 1):
            gates.append((row, maze.cell_col_count - 1, R))
    for col in range(maze.cell_col_count):
        if maze.con_u(0, col):
            gates.append((0, col, U))
        if maze.con_d(maze.cell_row_count - 1, col):
            gates.append((maze.cell_row_count - 1, col, D))
    return tuple(gates)


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


def traverse_cells(maze: Maze, gates):
    all_areas = []
    belonging_area = full_array_2d(maze.cell_row_count, maze.cell_col_count, None)
    
    remained_gates = list(gates)
    while len(remained_gates) > 0:
        start_gate = remained_gates.pop()
        
        start_row, start_col, gate_direction = start_gate
        start_cell = start_row, start_col
        area_cells = [start_cell]
        area_gates = [start_gate]
        area_path = [start_cell]
        area_culdesacs_blocks = []
        new_area = [area_cells, area_gates, area_path, area_culdesacs_blocks]
        belonging_area[start_row][start_col] = new_area
        all_areas.append(new_area)
        
        gate_node = [None, rev(gate_direction), []]
        start_node = [(start_row, start_col), gate_direction, []]
        
        route = [gate_node, start_node]
        while len(route) > 1:
            # 变到下一个方向并读取当前节点
            this_node = route[-1]
            this_node[1] = (this_node[1] + 1) % 4
            (this_row, this_col), this_direction, this_records = this_node
            
            # 如果方向与来时的方向相同，则回溯
            last_node = route[-2]
            entering_direction = rev(last_node[1])
            if this_direction == entering_direction:
                # 给父节点一个 record
                this_record = None
                if all(record is not None for record in this_records):
                    # 自己是死胡同，要在 records 里加上 block
                    merged_block = max(this_records, key=len)
                    if len(merged_block) == 0:
                        merged_block = [(this_row, this_col)]
                        area_culdesacs_blocks.append(merged_block)
                    else:
                        for block in this_records:
                            if block is merged_block:
                                continue
                            if len(block) == 0:
                                continue
                            area_culdesacs_blocks.remove(block)
                            merged_block.extend(block)
                        merged_block.append((this_row, this_col))
                    this_record = merged_block
                last_node[2].append(this_record)
                
                # 如果正在追踪path，要缩回来
                if len(area_gates) == 1:
                    area_path.pop()
                
                # 回缩route
                route.pop()
                continue
            
            # 前进，找下一个cell的坐标
            next_cell = None
            next_gate = None
            if this_direction == U:
                if this_row == 0:
                    if maze.con_u(this_row, this_col):
                        next_gate = (this_row, this_col, U)
                elif maze.con_u(this_row, this_col):
                    next_cell = (this_row - 1, this_col)
            elif this_direction == L:
                if this_col == 0:
                    if maze.con_l(this_row, this_col):
                        next_gate = (this_row, this_col, L)
                elif maze.con_l(this_row, this_col):
                    next_cell = (this_row, this_col - 1)
            elif this_direction == D:
                if this_row == maze.cell_row_count - 1:
                    if maze.con_d(this_row, this_col):
                        next_gate = (this_row, this_col, D)
                elif maze.con_d(this_row, this_col):
                    next_cell = (this_row + 1, this_col)
            elif this_direction == R:
                if this_col == maze.cell_col_count - 1:
                    if maze.con_r(this_row, this_col):
                        next_gate = (this_row, this_col, R)
                elif maze.con_r(this_row, this_col):
                    next_cell = (this_row, this_col + 1)
            
            # 如果该方向走不通，需要考虑是否是gate
            if next_cell is None:
                if next_gate is not None:
                    this_records.append(None)
                    area_gates.append(next_gate)
                    remained_gates.remove(next_gate)
                else:
                    this_records.append([])
                continue
            
            # 如果走得通，看有没有咬自己
            next_row, next_col = next_cell
            if belonging_area[next_row][next_col] is new_area:
                # 如果咬自己，给record加一个None
                this_records.append(None)
                continue
            # 如果不是自己，就注册加入
            belonging_area[next_row][next_col] = new_area
            area_cells.append(next_cell)
            
            # 创建新的节点
            next_node = [next_cell, rev(this_direction), []]
            
            # 如果正在追踪path，则跟着前进
            if len(area_gates) == 1:
                area_path.append(next_cell)
            
            # 进行下一次循环
            route.append(next_node)
    
    return all_areas


# utils


def full_array_2d(row_count, col_count, value=None):
    matrix = []
    for row in range(row_count):
        matrix_row = []
        for col in range(col_count):
            matrix_row.append(value)
        matrix.append(matrix_row)
    return matrix


# main

def main():
    maze = Maze('./a2_sanity_check/maze_2.txt')
    print("the maze looks like:")
    print(maze)
    
    gates = find_gates(maze)
    print("number of gates:", len(gates))
    
    pillar_groups = traverse_pillars(maze)
    # print("number of connected groups of pillars:", len(pillar_groups))
    
    wall_group_count = sum(len(g) > 1 for g in pillar_groups)
    print("number of connected walls:", wall_group_count)
    
    open_areas = traverse_cells(maze, gates)
    
    open_square = sum(len(cells) for cells, _, _, _ in open_areas)
    inner_square = maze.cell_row_count * maze.cell_col_count - open_square
    print("number of inner points:", inner_square)
    
    open_area_count = len(open_areas)
    print("number of accessible area:", open_area_count)
    
    culdesacs_block_count = sum(len(blocks) for _, _, _, blocks in open_areas)
    print("number of culdesfcs block:", culdesacs_block_count)
    
    path_count = sum(len(gates) == 2 for _, gates, _, _ in open_areas)
    print("number of path:", path_count)


if __name__ == '__main__':
    main()
