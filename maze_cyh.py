class Cell:
    def __init__(self, x, y, left, right, up, down):
        self.x = x
        self.y = y
        self.left = left
        self.right = right
        self.up = up
        self.down = down


class Maze:
    def __init__(self, input_file):
        self.cells = []
        self.file = input_file
        self.matrix = None

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

    def parse_cells(self):
        row = len(self.matrix) - 1
        column = len(self.matrix[0]) - 1
        for i in range(row):
            for j in range(column):
                left = self.matrix[i][j] == 0 or self.matrix[i][j] == 1
                up = self.matrix[i][j] == 0 or self.matrix[i][j] == 2
                right = self.matrix[i][j + 1] == 0 or self.matrix[i][j + 1] == 1
                down = self.matrix[i + 1][j] == 0 or self.matrix[i + 1][j] == 2
                cell = Cell(i, j, left, right, up, down)
                self.cells.append(cell)

    def getNumOfGates(self):
        num = 0
        for cell in self.cells:
            if cell.x == 0 and cell.y == 0:
                num += int(cell.left) + int(cell.up)
                continue
            if cell.x == 0 and cell.y == len(self.matrix[0]) - 2:
                num += int(cell.up) + int(cell.right)
                continue
            if cell.x == len(self.matrix) - 2 and cell.y == 0:
                num += int(cell.left) + int(cell.down)
                continue
            if cell.x == len(self.matrix) - 2 and cell.y == len(self.matrix[0]) - 2:
                num += int(cell.right) + int(cell.down)
                continue
            if cell.x == 0:
                num += int(cell.up)
                continue
            if cell.x == len(self.matrix) - 2:
                num += int(cell.down)
                continue
            if cell.y == 0:
                num += int(cell.left)
                continue
            if cell.y == len(self.matrix[0]) - 2:
                num += int(cell.right)
                continue
        return num


maze = Maze('.\\a2_sanity_check\\labyrinth.txt')
maze.parse_file()
print(maze.matrix)
maze.parse_cells()
print(maze.getNumOfGates())
