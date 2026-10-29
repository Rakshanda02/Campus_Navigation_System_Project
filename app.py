from flask import Flask, render_template, request
import heapq

app = Flask(__name__)

# Campus map: each location is a node, and each road is an edge.
# Distances are in meters. Keep roads in both directions where appropriate.
GRAPH = {
    "Main Gate": {"Library": 100, "Canteen": 150, "Admin Block": 220},
    "Library": {"Main Gate": 100, "Computer Lab": 80, "Admin Block": 120},
    "Canteen": {"Main Gate": 150, "Admin Block": 100, "Sports Ground": 200},
    "Computer Lab": {"Library": 80, "Science Block": 100},
    "Admin Block": {"Main Gate": 220, "Library": 120, "Canteen": 100, "Auditorium": 150},
    "Science Block": {"Computer Lab": 100, "Auditorium": 120},
    "Sports Ground": {"Canteen": 200, "Hostel": 180},
    "Auditorium": {"Admin Block": 150, "Science Block": 120, "Hostel": 250},
    "Hostel": {"Sports Ground": 180, "Auditorium": 250},
}

LOCATION_INFO = {
    "Main Gate": ("🚪", "Campus entrance"),
    "Library": ("📚", "Books, reading and study"),
    "Canteen": ("☕", "Food and refreshments"),
    "Computer Lab": ("💻", "Computers and practical sessions"),
    "Admin Block": ("🏢", "Office and administration"),
    "Science Block": ("🧪", "Science classrooms and labs"),
    "Sports Ground": ("🏟️", "Outdoor sports and activities"),
    "Auditorium": ("🎭", "Events and presentations"),
    "Hostel": ("🏠", "Student accommodation"),
}


def shortest_path(graph, start, destination):
    """Dijkstra's algorithm: returns shortest path and total distance."""
    distances = {place: float("inf") for place in graph}
    previous = {}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_place = heapq.heappop(priority_queue)

        if current_distance > distances[current_place]:
            continue
        if current_place == destination:
            break

        for neighbor, road_distance in graph[current_place].items():
            new_distance = current_distance + road_distance
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_place
                heapq.heappush(priority_queue, (new_distance, neighbor))

    if distances[destination] == float("inf"):
        return [], 0

    path = []
    place = destination
    while place != start:
        path.append(place)
        place = previous[place]
    path.append(start)
    path.reverse()
    return path, distances[destination]


@app.route("/", methods=["GET", "POST"])
def index():
    locations = list(GRAPH.keys())
    start = "Main Gate"
    destination = "Library"
    path = []
    distance = None
    error = None

    if request.method == "POST":
        start = request.form.get("start", "")
        destination = request.form.get("destination", "")
        if start not in GRAPH or destination not in GRAPH:
            error = "Please choose valid campus locations."
        elif start == destination:
            path = [start]
            distance = 0
        else:
            path, distance = shortest_path(GRAPH, start, destination)
            if not path:
                error = "No route was found between these locations."

    location_cards = [
        {"name": name, "icon": LOCATION_INFO[name][0], "description": LOCATION_INFO[name][1]}
        for name in locations
    ]
    return render_template(
        "index.html",
        locations=locations,
        location_cards=location_cards,
        start=start,
        destination=destination,
        path=path,
        distance=distance,
        error=error,
        graph=GRAPH,
    )


if __name__ == "__main__":
    app.run(debug=True)
