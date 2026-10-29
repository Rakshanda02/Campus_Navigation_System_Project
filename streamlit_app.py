import streamlit as st
import heapq

# Set page configuration
st.set_page_config(
    page_title="CampusWay — Campus Navigation System",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0d4b3e 0%, #167d66 60%, #1ea88a 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px rgba(22, 125, 102, 0.2);
    }
    
    .main-header h1 {
        color: white !important;
        font-weight: 800;
        font-size: 2.3rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    .main-header p {
        color: #d1fae5;
        font-size: 1.05rem;
        margin: 0;
    }
    
    .metric-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.15);
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.8rem;
        backdrop-filter: blur(8px);
    }
    
    .route-card {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.6rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        margin-bottom: 1.5rem;
    }
    
    .path-step {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
        padding: 0.75rem 1rem;
        background: #f8fafc;
        border-radius: 12px;
        border-left: 4px solid #10b981;
    }
    
    .step-number {
        background: #10b981;
        color: white;
        font-weight: 700;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        margin-right: 0.9rem;
    }
    
    .step-name {
        font-weight: 600;
        color: #1e293b;
        font-size: 1.02rem;
    }
    
    .distance-tag {
        margin-left: auto;
        color: #64748b;
        font-size: 0.88rem;
        font-weight: 600;
    }
    
    .place-item {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .place-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# Campus graph definition (meters)
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

# Graph Node 2D Positions for SVG Visualization
NODE_POSITIONS = {
    "Main Gate": (110, 310),
    "Library": (110, 180),
    "Computer Lab": (110, 60),
    "Canteen": (310, 310),
    "Admin Block": (310, 180),
    "Science Block": (310, 60),
    "Sports Ground": (510, 310),
    "Auditorium": (510, 140),
    "Hostel": (680, 230),
}


def shortest_path(graph, start, destination):
    """Dijkstra's shortest path algorithm"""
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


def render_campus_svg(path):
    """Generate an interactive visual SVG map of the campus and highlight shortest path"""
    path_edges = set()
    if path and len(path) > 1:
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            path_edges.add((u, v))
            path_edges.add((v, u))

    all_drawn_edges = set()
    edge_svg_lines = []

    # Draw roads (edges)
    for u, neighbors in GRAPH.items():
        for v, dist in neighbors.items():
            edge_key = tuple(sorted([u, v]))
            if edge_key in all_drawn_edges:
                continue
            all_drawn_edges.add(edge_key)

            x1, y1 = NODE_POSITIONS[u]
            x2, y2 = NODE_POSITIONS[v]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2

            is_path_edge = (u, v) in path_edges
            if is_path_edge:
                stroke_color = "#10b981"
                stroke_width = "6"
                stroke_dash = ""
                badge_bg = "#10b981"
                badge_text = "#ffffff"
            else:
                stroke_color = "#cbd5e1"
                stroke_width = "2.5"
                stroke_dash = "stroke-dasharray='4 4'"
                badge_bg = "#f1f5f9"
                badge_text = "#64748b"

            edge_svg_lines.append(f"""
                <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-linecap="round" {stroke_dash} />
                <rect x="{mx - 18}" y="{my - 11}" width="36" height="22" rx="6" fill="{badge_bg}" stroke="{stroke_color}" stroke-width="1.2" />
                <text x="{mx}" y="{my + 4}" fill="{badge_text}" font-size="10" font-weight="700" text-anchor="middle">{dist}m</text>
            """)

    # Draw nodes
    node_svg_elements = []
    path_set = set(path)
    for name, (x, y) in NODE_POSITIONS.items():
        icon, desc = LOCATION_INFO[name]
        is_start = path and name == path[0]
        is_dest = path and name == path[-1]
        is_in_path = name in path_set

        if is_start:
            fill_color = "#10b981"
            border_color = "#047857"
            text_color = "#047857"
            radius = 24
            badge = "START"
        elif is_dest:
            fill_color = "#ef4444"
            border_color = "#b91c1c"
            text_color = "#b91c1c"
            radius = 24
            badge = "END"
        elif is_in_path:
            fill_color = "#34d399"
            border_color = "#059669"
            text_color = "#065f46"
            radius = 20
            badge = None
        else:
            fill_color = "#f8fafc"
            border_color = "#94a3b8"
            text_color = "#334155"
            radius = 18
            badge = None

        node_svg_elements.append(f"""
            <g transform="translate({x}, {y})">
                <circle cx="0" cy="0" r="{radius + 4}" fill="none" stroke="{border_color}" stroke-width="2" stroke-opacity="0.3" />
                <circle cx="0" cy="0" r="{radius}" fill="{fill_color}" stroke="{border_color}" stroke-width="2.5" />
                <text x="0" y="5" font-size="16" text-anchor="middle">{icon}</text>
                <text x="0" y="{radius + 16}" font-size="11" font-weight="700" fill="{text_color}" text-anchor="middle">{name}</text>
        """)
        if badge:
            node_svg_elements.append(f"""
                <rect x="-20" y="{-radius - 14}" width="40" height="15" rx="4" fill="{border_color}" />
                <text x="0" y="{-radius - 3}" font-size="8.5" font-weight="800" fill="#ffffff" text-anchor="middle">{badge}</text>
            """)
        node_svg_elements.append("</g>")

    svg_content = f"""
    <div style="background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); border: 1.5px solid #e2e8f0; border-radius: 18px; padding: 15px; overflow-x: auto;">
        <svg viewBox="0 0 780 390" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                    <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#e2e8f0" stroke-width="0.8"/>
                </pattern>
            </defs>
            <rect width="780" height="390" fill="url(#grid)" rx="12" />
            {''.join(edge_svg_lines)}
            {''.join(node_svg_elements)}
        </svg>
    </div>
    """
    return svg_content


# Header Component
st.markdown("""
<div class="main-header">
    <h1>🧭 CampusWay Navigation</h1>
    <p>Find the shortest walking route across campus powered by Dijkstra's graph algorithm.</p>
    <div class="metric-badge">
        <span>● Active System</span> &nbsp;|&nbsp; 9 Campus Locations &nbsp;|&nbsp; Real-time Shortest Path
    </div>
</div>
""", unsafe_allow_html=True)

# Layout: Two columns (Sidebar/Left for inputs, Right for Map and Results)
col_input, col_display = st.columns([1, 2.2], gap="large")

locations = list(GRAPH.keys())

# Default selections in session state
if "start_loc" not in st.session_state:
    st.session_state.start_loc = "Main Gate"
if "dest_loc" not in st.session_state:
    st.session_state.dest_loc = "Library"

with col_input:
    st.subheader("📍 Route Planner")
    
    start = st.selectbox(
        "Starting Point",
        locations,
        index=locations.index(st.session_state.start_loc),
        key="start_select",
        format_func=lambda x: f"{LOCATION_INFO[x][0]}  {x}"
    )
    
    if st.button("⇅ Swap Locations", use_container_width=True):
        st.session_state.start_loc, st.session_state.dest_loc = st.session_state.dest_loc, st.session_state.start_loc
        st.rerun()
        
    destination = st.selectbox(
        "Destination",
        locations,
        index=locations.index(st.session_state.dest_loc),
        key="dest_select",
        format_func=lambda x: f"{LOCATION_INFO[x][0]}  {x}"
    )

    calculate = st.button("🚀 Find Shortest Route", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🏢 Campus Directory")
    for name, (icon, desc) in LOCATION_INFO.items():
        st.markdown(f"""
        <div class="place-item">
            <span style="font-size: 1.25rem; margin-right: 8px;">{icon}</span>
            <strong>{name}</strong>
            <div style="font-size: 0.85rem; color: #64748b; margin-top: 3px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

with col_display:
    if start == destination:
        st.info(f"You are already at **{start}**! Distance: 0 meters.")
        path = [start]
        total_dist = 0
    else:
        path, total_dist = shortest_path(GRAPH, start, destination)

    # Route Metrics
    if path and total_dist > 0:
        walking_mins = max(1, round(total_dist / 84))  # ~84 meters per min
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="🚶 Total Distance", value=f"{total_dist} meters")
        with m2:
            st.metric(label="⏱️ Walking Time", value=f"~{walking_mins} min")
        with m3:
            st.metric(label="🚩 Total Stops", value=f"{len(path)} places")

        st.markdown("### 🗺️ Visual Campus Map")
        st.markdown(render_campus_svg(path), unsafe_allow_html=True)

        st.markdown("### 📋 Step-by-Step Directions")
        for i in range(len(path)):
            place = path[i]
            icon, desc = LOCATION_INFO[place]
            if i < len(path) - 1:
                next_place = path[i + 1]
                leg_dist = GRAPH[place][next_place]
                st.markdown(f"""
                <div class="path-step">
                    <span class="step-number">{i + 1}</span>
                    <span style="font-size: 1.2rem; margin-right: 8px;">{icon}</span>
                    <span class="step-name">{place}</span>
                    <span class="distance-tag">Walk {leg_dist}m to {next_place} ➔</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="path-step" style="border-left-color: #ef4444; background: #fff1f2;">
                    <span class="step-number" style="background: #ef4444;">{i + 1}</span>
                    <span style="font-size: 1.2rem; margin-right: 8px;">{icon}</span>
                    <span class="step-name">{place}</span>
                    <span class="distance-tag" style="color: #b91c1c; font-weight: 700;">Arrived at Destination! 🎯</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("### 🗺️ Interactive Campus Map")
        st.markdown(render_campus_svg([]), unsafe_allow_html=True)

# Expandable Algorithm explanation
with st.expander("ℹ️ How Dijkstra's Algorithm Finds Your Shortest Path"):
    st.markdown(r"""
    **Dijkstra's Algorithm** finds the shortest path between nodes in a graph:
    1. **Initialization:** Set the starting point distance to 0 and all other campus nodes to infinity ($\infty$).
    2. **Priority Queue:** The start node is placed into a min-priority queue based on smallest cumulative distance.
    3. **Exploration:** Continuously extract the node with the lowest known distance.
    4. **Relaxation:** Inspect all connected roads. If a new path to a neighboring building is shorter, update the neighbor's distance and parent pointer.
    5. **Path Reconstruction:** Once destination is reached, trace back pointers from destination to start.
    """)
