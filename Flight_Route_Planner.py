import tkinter as tk
from tkinter import messagebox
import networkx as nx
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

root = tk.Tk()
root.title("Flight Route Planner")
root.geometry("600x500")

# Define constants and initialize the graph
FUEL_CONSUMPTION_RATE = 0.05
AVERAGE_SPEED = 850
G = nx.Graph()

edges = [
    ("JFK", "LAX", 3983),
    ("JFK", "ORD", 1180),
    ("ORD", "DFW", 1291),
    ("DFW", "LAX", 1984),
    ("MIA", "JFK", 1750),
    ("ATL", "JFK", 760),
    ("LAX", "SEA", 954),
    ("ORD", "MIA", 1190),
    ("DEN", "DFW", 620),
    ("BOS", "LAX", 2610),
    ("SEA", "SFO", 679),
    ("SFO", "ORD", 1846),
    ("PHX", "LAX", 370),
    ("IAH", "ORD", 925),
    ("DFW", "ATL", 730)
]

for (start, end, distance) in edges:
    weather_score = random.uniform(1, 10)  
    G.add_edge(
        start, end, 
        weight=distance, 
        fuel=distance * FUEL_CONSUMPTION_RATE, 
        time=distance / AVERAGE_SPEED, 
        weather=weather_score
    )


def find_optimal_path(start, end, factor="weight"):
    try:
        path = nx.dijkstra_path(G, source=start, target=end, weight=factor)
        path_length = nx.dijkstra_path_length(G, source=start, target=end, weight=factor)
        return path, path_length
    except nx.NetworkXNoPath:
        return None, None

# GUI Components
tk.Label(root, text="Starting Airport").pack(pady=5)
start_airport_entry = tk.Entry(root)
start_airport_entry.pack(pady=5)

tk.Label(root, text="Destination Airport").pack(pady=5)
end_airport_entry = tk.Entry(root)
end_airport_entry.pack(pady=5)

#  list of available airports to be displayed
available_airports_label = tk.Label(root, text="Available Airports: JFK, LAX, ORD, DFW, MIA, ATL, SEA, SFO, PHX, IAH, DEN, BOS", fg="blue")
available_airports_label.pack(pady=5)

# Optimization factor selection
tk.Label(root, text="Optimization Factor").pack(pady=5)
factor_var = tk.StringVar()
factor_var.set("distance")
tk.Radiobutton(root, text="Distance", variable=factor_var, value="distance").pack()
tk.Radiobutton(root, text="Fuel", variable=factor_var, value="fuel").pack()
tk.Radiobutton(root, text="Time", variable=factor_var, value="time").pack()
tk.Radiobutton(root, text="Weather", variable=factor_var, value="weather").pack()

tk.Label(root, text="Avoid Bad Weather (1-10)").pack(pady=5)
avoid_weather_entry = tk.Entry(root)
avoid_weather_entry.pack(pady=5)

result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, wraplength=350)
result_label.pack(pady=10)

graph_frame = tk.Frame(root)
graph_frame.pack(pady=10)

def find_route():
    start_airport = start_airport_entry.get().strip().upper()
    end_airport = end_airport_entry.get().strip().upper()
    factor = factor_var.get()
    

    avoid_weather_score = float(avoid_weather_entry.get().strip()) if avoid_weather_entry.get() else None

    if start_airport not in G.nodes or end_airport not in G.nodes:
        messagebox.showerror("Error", "Invalid airport codes!")
        return
    
    
    if avoid_weather_score is not None:
        for edge in G.edges(data=True):
            if edge[2]['weather'] > avoid_weather_score:
                G[edge[0]][edge[1]]['weight'] += 10  

    factor_map = {"distance": "weight", "fuel": "fuel", "time": "time", "weather": "weather"}
    optimal_path, path_length = find_optimal_path(start_airport, end_airport, factor=factor_map[factor])
    
    if optimal_path:
        unit = "km" if factor == "distance" else "liters" if factor == "fuel" else "hours" if factor == "time" else "weather score"
        result_text.set(f"Optimal Path: {' -> '.join(optimal_path)}\nTotal {factor.capitalize()}: {path_length:.2f} {unit}")
        
        
        fig, ax = plt.subplots()
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_weight="bold", ax=ax)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)
   
        path_edges = list(zip(optimal_path, optimal_path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=2, ax=ax)
        
        for widget in graph_frame.winfo_children():
            widget.destroy()  
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    else:
        result_text.set("No route found between the specified airports.")

def clear_inputs():
    start_airport_entry.delete(0, tk.END)
    end_airport_entry.delete(0, tk.END)
    avoid_weather_entry.delete(0, tk.END)
    result_text.set("") 
    for widget in graph_frame.winfo_children():
        widget.destroy() 


find_button = tk.Button(root, text="Find Route", command=find_route)
find_button.pack(pady=10)

clear_button = tk.Button(root, text="Clear Inputs", command=clear_inputs)
clear_button.pack(pady=10)

root.mainloop()