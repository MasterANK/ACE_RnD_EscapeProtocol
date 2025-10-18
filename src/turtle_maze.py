import turtle
import tkinter as tk
import time
import json
import math
import tkinter.messagebox as msg

filename = r"src/mazes/maze1.json"

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
    """
    Checks for collision against any wall (horizontal, vertical, or slant) 
    by calculating the distance from the player point (x, y) to the wall segment.
    """
    # Player radius or collision buffer
    THRESHOLD = 5 

    for x1, y1, x2, y2 in walls:
        dx = x2 - x1
        dy = y2 - y1
        len_sq = dx*dx + dy*dy

        # If the segment is a point (shouldn't happen), check point distance
        if len_sq == 0:
            if math.hypot(x - x1, y - y1) < THRESHOLD:
                return True
            continue

        # Calculate t: The projection factor of vector AP onto vector AB
        # P = (x, y), A = (x1, y1), B = (x2, y2)
        # t = ((P - A) . (B - A)) / |B - A|^2
        t = ((x - x1) * dx + (y - y1) * dy) / len_sq

        # Clamp t to the [0, 1] range to ensure the closest point is on the segment
        t = max(0, min(1, t))

        # Closest point on the segment (closest_x, closest_y)
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # Calculate distance from player (x, y) to the closest point on the wall
        distance = math.hypot(x - closest_x, y - closest_y)

        if distance < THRESHOLD:
            return True
            
    return False

# --- Tkinter Controls ---
label = tk.Label(frame_left, text="Enter commands:")
label.pack()

text_box = tk.Text(frame_left, height=15, width=25)
text_box.pack()

status_label = tk.Label(frame_left, text="Status: Ready")
status_label.pack()

# --- Scoring variables ---
move_count = 0
total_distance = 0.0
start_time = time.time()

def run_commands():
    # Reset player to start each run
    player.clear()
    player.penup()
    player.goto(start_pos)
    player.pendown()
    player.setheading(0)
    screen.update()

    commands = text_box.get("1.0", tk.END).strip().splitlines()

    move_count = 0
    total_distance = 0

    for cmd in commands:
        parts = cmd.strip().split()
        if not parts:
            continue
        action = parts[0].upper()
        move_count += 1
        if action == "MOVE" and len(parts) == 2:
            try:
                dist = int(parts[1])
                total_distance += dist
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
                        end_time = time.time()
                        elapsed = end_time - start_time
                        score = (elapsed * 0.5) + (move_count * 2) + (total_distance * 0.1)
                        status_label.config(text=f"🎉 Goal Reached! ,\n \
                                             ⏱ Time: {elapsed:.2f}s\n🚶 Moves: {move_count}\n📏 Distance: {int(total_distance)}\n🏆 Score: {score:.2f}")
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

def show_mouse_position(event):
    canvas_width = screen.window_width()
    canvas_height = screen.window_height()

    # Convert tkinter canvas coords (top-left origin)
    # to turtle coords (center origin, y increasing upward)
    x = event.x - canvas_width / 2
    y = canvas_height / 2 - event.y

    coord_label.config(text=f"🖱️ Mouse: ({int(x)}, {int(y)})")


coord_label = tk.Label(frame_left, text="🖱️ Mouse: (0, 0)")
coord_label.pack(pady=5)

canvas.bind("<Motion>", show_mouse_position)

#INSTRUCTION PANEL
def show_instructions():
    instructions = """
📘 **MAZE SOLVER INSTRUCTIONS**

Welcome to the Maze Solver challenge! 🧩  
Your goal is to **navigate the blue turtle 🐢** from the **start point** to the **green goal 🟢**
using text-based movement commands — without hitting any walls.

───────────────────────────────
🧭 **COMMANDS**
───────────────────────────────
➡️  MOVE <distance>  
  Moves the turtle forward by the given number of pixels.

↩️  ROTATE <angle>  
  Rotates the turtle clockwise by the given number of degrees.

───────────────────────────────
💻 **EXAMPLES**
───────────────────────────────
MOVE 100  
ROTATE 90  
MOVE 50  
ROTATE 45  
MOVE 70  

Tip 🪄:  
You can use multiple lines — one command per line!

───────────────────────────────
🎯 **GOAL**
───────────────────────────────
✅ Reach the green circle without touching any walls.  
💥 Colliding with a wall ends your attempt.  
🏁 The faster you reach the goal with fewer moves and less distance, the higher your score!

───────────────────────────────
🕹️ **SCORING SYSTEM**
───────────────────────────────
🏆 Final Score is calculated from:
- ⏱️ Time taken  
- 🚶 Number of moves (commands)  
- 📏 Total distance traveled  

Higher scores = better performance!

───────────────────────────────
💡 **HINTS**
───────────────────────────────
- Try smaller moves for precision.
- Use right angles (90°) for sharp turns.
- Plan your path before executing commands.

Good luck, maze solver! 🎉
"""
    # Use a Toplevel window for better formatting than simple messagebox
    help_window = tk.Toplevel()
    help_window.title("📘 Maze Solver Instructions")
    help_window.geometry("500x600")
    help_window.resizable(False, True)

    text_widget = tk.Text(help_window, wrap="word", font=("Consolas", 11), bg="#f8f9fa")
    text_widget.insert("1.0", instructions)
    text_widget.config(state="disabled")
    text_widget.pack(expand=True, fill="both", padx=10, pady=10)

    scrollbar = tk.Scrollbar(help_window, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=scrollbar.set)

help_button = tk.Button(frame_left, text="❓ Help / Instructions", command=show_instructions)
help_button.pack(pady=5)

root.mainloop()
