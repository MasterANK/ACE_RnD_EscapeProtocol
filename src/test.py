import sys
import importlib
import json
import os
import requests

maze_files = [
    r"src/mazes/MAZENF.json",
    r"src/mazes/maze2.json",
    r"src/mazes/ACE.json",
    r"src/mazes/VIPS.json",
    r"src/mazes/vscodelogo.json",
    r"src/mazes/Valo.json",
    r"src/mazes/netflix.json",
    r"src/mazes/CAT.json",
    r"src/mazes/HarryPotter.json",
    r"src/mazes/Polygon.json",
    r"src/mazes/geminimaze.json",
    r"src/mazes/chatgptmaze.json",
    r"src/mazes/Minecraft.json",
    r"src/mazes/Vision.json",
    r"src/mazes/jack.json",
    r"src/mazes/dragon.json",
    r"src/mazes/Birb.json"
]

def check_python_version():
    print("🧠 Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python {sys.version.split()[0]} detected. Please use 3.8 or higher.")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible.")
    return True

def check_module(module_name):
    try:
        importlib.import_module(module_name)
        print(f"✅ Module '{module_name}' found.")
        return True
    except ImportError:
        print(f"❌ Module '{module_name}' is missing. Try installing it using:")
        print(f"   pip install {module_name}")
        return False

def check_turtle_graphics():
    print("🎨 Testing turtle graphics window...")
    try:
        import turtle
        screen = turtle.Screen()
        screen.title("Graphics Test")
        turtle.hideturtle()
        screen.update()
        screen.bye()
        print("✅ Turtle graphics working fine.")
        return True
    except Exception as e:
        print(f"❌ Turtle graphics failed: {e}")
        return False

def check_maze_files():
    print("🗂️ Checking for maze files...")
    found = False
    for file in maze_files:
        try:
            with open(file, "r") as f:
                json.load(f)
            print(f"✅ Valid maze file found: {file}")
            found = True
        except json.JSONDecodeError:
            print(f"⚠️ {file} is not a valid JSON maze file.")
        except Exception as e:
            print(e)
    if not found:
        print("❌ No valid maze files found in the directory.")
    return found

def check_api_connection(test_url="https://www.google.com", api_url="https://ace-rnd-escapeprotocol.onrender.com/leaderboard"):
    print("🌐 Checking internet and API connectivity...")
    try:
        # Step 1: Check general internet access
        r = requests.get(test_url, timeout=5)
        if r.status_code == 200:
            print("✅ Internet connection working.")
        else:
            print(f"⚠️ Internet access seems unstable (Status {r.status_code})")

        # Step 2: If API URL is provided, check it as well
        if api_url:
            print(f"🔗 Checking API connection: {api_url}")
            api_resp = requests.get(api_url, timeout=10)
            if api_resp.status_code == 200:
                print("✅ API connection successful.")
            else:
                print(f"⚠️ API responded with status: {api_resp.status_code}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Network/API check failed: {e}")
        return False

def run_all_checks():
    print("🔍 Running Maze System Check...\n")
    checks = [
        check_python_version(),
        check_module("tkinter"),
        check_module("turtle"),
        check_module("json"),
        check_module("requests"),
        check_turtle_graphics(),
        check_maze_files(),
        check_api_connection(),
    ]
    print("\n📊 Summary:")
    if all(checks):
        print("✅ All systems operational! You’re ready to play.")
    else:
        print("⚠️ Some checks failed. Please fix the above issues before running the maze.")

if __name__ == "__main__":
    run_all_checks()
