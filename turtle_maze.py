import turtle
import tkinter as tk
import time
import json

filename = r"maze.json"

# --- Main Tkinter window ---
root = tk.Tk()
root.title("Maze Solver with Block Commands")

# Layout: left side controls, right side turtle canvas
frame_left = tk.Frame(root)
frame_left.pack(side="left", padx=10, pady=10)

frame_right = tk.Frame(root)
frame_right.pack(side="right", padx=10, pady=10)

# --- Turtle Canvas inside Tkinter ---
canvas = turtle.ScrolledCanvas(frame_right, width=600, height=600)
canvas.pack()
screen = turtle.TurtleScreen(canvas)
screen.tracer(0)   # manual updates

# Maze drawing turtle
maze = turtle.RawTurtle(screen)
maze.speed(0)
maze.hideturtle()

# Walls list
walls = []

def draw_wall(x1, y1, x2, y2):
    maze.penup()
    maze.goto(x1, y1)
    maze.pendown()
    maze.goto(x2, y2)
    # walls.append((x1, y1, x2, y2))

# --- Draw Maze ---
def build_maze():
    walls.clear()
    maze.clear()
    # Border
    with open(filename, "r") as f:
        data = json.load(f)
    return data["walls"], tuple(data["start"]), tuple(data["goal"])

walls, start_pos, goal_pos = build_maze()
print(walls)

for wall in walls:
    draw_wall(wall[0],wall[1],wall[2],wall[3])


goal_marker = turtle.RawTurtle(screen)
goal_marker.shape("circle")
goal_marker.color("green")
goal_marker.penup()
goal_marker.goto(goal_pos)
goal_marker.stamp()   # draw goal once

# --- Player Turtle ---
player = turtle.RawTurtle(screen)
player.shape("turtle")
player.color("blue")
player.penup()
player.goto(start_pos)

# Show everything initially
screen.update()

# --- Collision Detection ---
def is_collision(x, y):
    for (x1, y1, x2, y2) in walls:
        if x1 == x2:  # vertical wall
            if abs(x - x1) < 5 and min(y1, y2) <= y <= max(y1, y2):
                return True
        if y1 == y2:  # horizontal wall
            if abs(y - y1) < 5 and min(x1, x2) <= x <= max(x1, x2):
                return True
    return False

# --- Tkinter Controls ---
label = tk.Label(frame_left, text="Enter commands:")
label.pack()

text_box = tk.Text(frame_left, height=15, width=25)
text_box.pack()

status_label = tk.Label(frame_left, text="Status: Ready")
status_label.pack()

def run_commands():
    # Reset player to start each run
    player.goto(start_pos)
    player.setheading(0)
    screen.update()

    commands = text_box.get("1.0", tk.END).strip().splitlines()
    for cmd in commands:
        parts = cmd.strip().split()
        if not parts:
            continue
        action = parts[0].upper()
        if action == "MOVE" and len(parts) == 2:
            try:
                dist = int(parts[1])
                step = 5
                for _ in range(abs(dist)//step):
                    player.forward(step if dist > 0 else -step)
                    screen.update()
                    time.sleep(0.02)   # <- add delay for smooth motion
                    if is_collision(player.xcor(), player.ycor()):
                        player.backward(step)
                        status_label.config(text="💥 Hit a wall!")
                        return
                    if player.distance(goal_pos) < 15:
                        status_label.config(text="🎉 Goal Reached!")
                        return
            except:
                pass
        elif action == "ROTATE" and len(parts) == 2:
            try:
                angle = int(parts[1])
                player.right(angle)
                screen.update()
                time.sleep(0.1)  # small delay so rotation is visible
            except:
                pass
    status_label.config(text="✅ Finished commands")

run_button = tk.Button(frame_left, text="Run", command=run_commands)
run_button.pack(pady=5)

root.mainloop()
