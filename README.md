# CampusWay — Campus Navigation System Using Graphs

A beginner-friendly Python web project that finds the shortest route between campus locations using **Dijkstra's algorithm**.

## Features
- Modern, responsive campus navigation interface
- Choose a starting point and destination
- Shortest route and total distance in meters
- Nine example campus locations
- Graph represented with a Python dictionary
- Route planner swap button
- Built with Python + Flask, HTML templates, and CSS

## 1. Install Python
Install Python 3.10 or newer from https://www.python.org/downloads/ .
During installation on Windows, tick **Add Python to PATH**.

## 2. Open the project folder
Extract the ZIP file. Open the `campus_navigation_system` folder in VS Code, or open a terminal in that folder.

## 3. Create a virtual environment (recommended)
Windows:
```bash
python -m venv venv
venv\\Scripts\\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install the dependency
```bash
pip install -r requirements.txt
```

## 5. Run the website
```bash
python app.py
```

The terminal will show a local address, usually `http://127.0.0.1:5000`. Open that address in your browser.

To stop the server, return to the terminal and press `Ctrl+C`.

## How the algorithm works
1. Set the starting location's distance to 0 and all other distances to infinity.
2. Put the start location in a priority queue.
3. Repeatedly visit the location with the smallest known distance.
4. Check its neighboring locations and update distances if a shorter route is found.
5. Reconstruct the route from the destination back to the start.

## Customize the campus
Edit the `GRAPH` dictionary in `app.py`. Each location is a node, each connection is an edge, and each number is the distance in meters. For an undirected road, add the connection in both locations' dictionaries.

## Important note
This is a student project/demo. The distances are sample values and do not represent a real campus survey. The map illustration is decorative; the route result comes from the graph data.
