import turtle
import tkinter as tk
import json
import math

# --- Tkinter Setup ---
root = tk.Tk()
root.title("Maze Editor")

frame_left = tk.Frame(root)
frame_left.pack(side="left", padx=10, pady=10)

frame_right = tk.Frame(root)
frame_right.pack(side="right", padx=10, pady=10)

canvas = turtle.ScrolledCanvas(frame_right, width=600, height=600)
canvas.pack()
screen = turtle.TurtleScreen(canvas)
screen.tracer(0)  # manual screen updates

drawer = turtle.RawTurtle(screen)
drawer.hideturtle()
drawer.speed(0)

preview_turtle = turtle.RawTurtle(screen)
preview_turtle.hideturtle()
preview_turtle.pensize(2)
preview_turtle.color("gray")

walls = []
clicks = []
selected_point = None
line_mode = tk.StringVar(value="straight")  # Default mode

start_pos = (-180, 180)
goal_pos = (180, -180)

# Draw start and goal markers
start_marker = turtle.RawTurtle(screen)
start_marker.hideturtle()
start_marker.penup()
start_marker.goto(start_pos)
start_marker.color("blue")
start_marker.dot(20)

goal_marker = turtle.RawTurtle(screen)
goal_marker.hideturtle()
goal_marker.penup()
goal_marker.goto(goal_pos)
goal_marker.color("green")
goal_marker.dot(20)

start_marker = turtle.RawTurtle(screen)
start_marker.shape("circle")
start_marker.color("green")
start_marker.penup()
start_marker.shapesize(0.8)

end_marker = turtle.RawTurtle(screen)
end_marker.shape("circle")
end_marker.color("red")
end_marker.penup()
end_marker.shapesize(0.8)

# --- UI Elements ---
maze_name_label = tk.Label(frame_left, text="Maze Name:")
maze_name_label.pack()

maze_name_entry = tk.Entry(frame_left)
maze_name_entry.pack(pady=5)
maze_name_entry.insert(0, "maze1")

line_toggle = tk.Checkbutton(
    frame_left,
    text="Allow Slanting Lines",
    variable=line_mode,
    onvalue="slant",
    offvalue="straight",
)
line_toggle.pack(pady=5)

status_label = tk.Label(frame_left, text="Click to draw walls (2 clicks per wall)")
status_label.pack(pady=5)

def preview_wall(x, y):
    """Draw a preview line following the mouse after first click."""
    preview_turtle.clear()
    if len(clicks) != 1:
        return

    x1, y1 = clicks[0]
    x2, y2 = x, y

    # Adjust for straight mode
    if line_mode.get() == "straight":
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        if dx > dy:
            y2 = y1
        else:
            x2 = x1

    preview_turtle.penup()
    preview_turtle.goto(x1, y1)
    preview_turtle.pendown()
    preview_turtle.goto(x2, y2)

def onclick(x, y):
    """Handle user clicks for wall placement."""
    global clicks, selected_point
    clicks.append((x, y))

    if len(clicks) == 2:
        x1, y1 = clicks[0]
        x2, y2 = clicks[1]

        if line_mode.get() == "straight":
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            if dx > dy:
                y2 = y1
            else:
                x2 = x1

        drawer.penup()
        drawer.goto(x1, y1)
        drawer.pendown()
        drawer.goto(x2, y2)
        walls.append([int(x1), int(y1), int(x2), int(y2)])

        clicks.clear()
        preview_turtle.clear()
        screen.update()

screen.onclick(onclick)

def motion_handler(event):
    """Track mouse motion for live wall preview."""
    if len(clicks) == 1:
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        # Convert Tkinter coords → Turtle coords
        x = event.x - width / 2
        y = height / 2 - event.y

        preview_wall(x, y)
        # Don’t call screen.update() directly — schedule safely
        root.after_idle(lambda: screen.update())

screen.cv.bind("<Motion>", motion_handler)

def undo_last_wall():
    """Remove the last wall drawn."""
    if walls:
        walls.pop()  # Remove last wall
        drawer.clear()
        preview_turtle.clear()
        
        # Redraw all remaining walls
        for x1, y1, x2, y2 in walls:
            drawer.penup()
            drawer.goto(x1, y1)
            drawer.pendown()
            drawer.goto(x2, y2)

        screen.update()
        status_label.config(text="↩️ Last wall removed.")
    else:
        status_label.config(text="⚠️ No walls to undo.")

undo_button = tk.Button(frame_left, text="Undo Last Wall", command=undo_last_wall)
undo_button.pack(pady=5)

def save_maze():
    """Save maze data as JSON."""
    name = maze_name_entry.get().strip()
    if not name:
        status_label.config(text="⚠️ Please enter a maze name before saving.")
        return

    maze_data = {
        "name": name,
        "walls": walls,
        "start": start_pos,
        "goal": goal_pos,
    }

    filename = f"{name}.json"
    with open(filename, "w") as f:
        json.dump(maze_data, f, indent=2)

    status_label.config(text=f"✅ Maze saved to {filename}")

save_button = tk.Button(frame_left, text="Save Maze", command=save_maze)
save_button.pack(pady=10)

screen.update()
root.mainloop()
