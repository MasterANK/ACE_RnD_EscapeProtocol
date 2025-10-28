import json

maze_files = [
    r"src/mazes/MAZENF.json",
    r"src/mazes/maze2.json",
    r"src/mazes/ACE.json",
    r"src/mazes/VIPS.json",
    r"src/mazes/vscodelogo.json",
    r"src/mazes/Valo.json",
    r"src/mazes/netflix.json",
    r"src/mazes/CAT.json",
    r"src/mazes/EF.json",
    r"src/mazes/Polygon.json",
    r"src/mazes/geminimaze.json",
    r"src/mazes/chatgptmaze.json",
    r"src/mazes/Minecraft.json",
    r"src/mazes/Vision.json",
    r"src/mazes/jack.json",
    r"src/mazes/dragon.json",
    r"src/mazes/Birb.json"
]

for i in maze_files:
    with open(i, "r") as f:
        data = json.load(f)
print("Completed")