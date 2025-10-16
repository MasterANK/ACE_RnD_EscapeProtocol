import re

def expand_commands(command_str):
    tokens = command_str.replace("[", " [ ").replace("]", " ] ").split()
    stack = [[]]  # start with outer block

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.lower() == "repeat":
            count = int(tokens[i+1])
            i += 2  # skip 'repeat N'
            if tokens[i] != "[":
                raise ValueError("Expected '[' after repeat")
            stack.append(("REPEAT", count, []))  # mark as repeat block
        elif token == "[":
            pass  # handled above
        elif token == "]":
            block_type, count, block = stack.pop()
            if block_type != "REPEAT":
                raise ValueError("Unexpected closing bracket")
            stack[-1].extend(block * count)
        else:
            # If current top is a repeat block, add to its block
            if isinstance(stack[-1], tuple):
                block_type, count, block = stack.pop()
                block.append(token.upper())
                stack.append((block_type, count, block))
            else:
                stack[-1].append(token.upper())
        i += 1

    if len(stack) != 1:
        raise ValueError("Mismatched brackets")

    return stack[0]


# Same maze as before
maze = [
    "#########",
    "#S..#...#",
    "#.#.#.#E#",
    "#.#...#.#",
    "#.#####.#",
    "#.......#",
    "#########"
]

directions = [(-1,0), (0,1), (1,0), (0,-1)]
dir_names = ["N","E","S","W"]

# Find start
for r,row in enumerate(maze):
    for c,cell in enumerate(row):
        if cell == "S":
            player_pos = [r,c]
            player_dir = 1  # east
            break

def display_maze(pos):
    for r,row in enumerate(maze):
        row_str = ""
        for c,cell in enumerate(row):
            if [r,c]==pos:
                row_str += "P"
            else:
                row_str += cell
        print(row_str)
    print()

def move_forward(pos, direction):
    dr,dc = directions[direction]
    new_r,new_c = pos[0]+dr, pos[1]+dc
    if maze[new_r][new_c] != "#":
        return [new_r,new_c]
    else:
        print("Hit a wall!")
        return pos

# -------------------
# Main
# -------------------
user_program = "repeat 2 [F] R repeat 2 [F] L repeat 2 [F] L repeat 2 [F] R repeat 2 [F] R F"
commands = expand_commands(user_program)

print("Expanded:", "".join(commands))
print("\nInitial Maze:")
display_maze(player_pos)

for cmd in commands:
    if cmd == "F":
        player_pos = move_forward(player_pos, player_dir)
    elif cmd == "L":
        player_dir = (player_dir - 1) % 4
    elif cmd == "R":
        player_dir = (player_dir + 1) % 4

    display_maze(player_pos)

    if maze[player_pos[0]][player_pos[1]] == "E":
        print("🎉 You reached the exit!")
        break
