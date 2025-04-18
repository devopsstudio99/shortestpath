import os
os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'

# นำเข้าแพคเกจอื่นๆ ตามปกติ
import numpy as np
import matplotlib
matplotlib.use('Agg')  # ต้องระบุก่อน import pyplot

from flask import Flask, render_template, request, jsonify
import networkx as nx
import json
import random
import matplotlib
matplotlib.use('Agg')  # ต้องระบุก่อน import pyplot
import matplotlib.pyplot as plt
import os
import io
import base64
from PIL import Image

app = Flask(__name__)

def generate_random_graph(num_nodes=10):
    """สร้างกราฟแบบสุ่มที่มีโหนดตามที่กำหนด"""
    G = nx.Graph()
    
    # เพิ่มโหนด
    for i in range(num_nodes):
        G.add_node(i)
    
    # สร้างเส้นเชื่อมแบบวงแหวน (เพื่อให้มั่นใจว่าทุกโหนดเชื่อมถึงกัน)
    for i in range(num_nodes):
        next_node = (i + 1) % num_nodes
        weight = random.randint(1, 10)
        G.add_edge(i, next_node, weight=weight)
    
    # เพิ่มเส้นเชื่อมแบบสุ่ม
    for i in range(num_nodes):
        # แต่ละโหนดจะเชื่อมกับโหนดอื่นๆ อีก 1-3 โหนด
        num_edges = random.randint(1, 3)
        potential_targets = list(range(num_nodes))
        potential_targets.remove(i)  # ไม่เชื่อมกับตัวเอง
        
        # กรองโหนดที่เชื่อมอยู่แล้ว
        for neighbor in list(G.neighbors(i)):
            if neighbor in potential_targets:
                potential_targets.remove(neighbor)
        
        # เพิ่มขอบใหม่
        for _ in range(min(num_edges, len(potential_targets))):
            if not potential_targets:
                break
            target = random.choice(potential_targets)
            potential_targets.remove(target)
            weight = random.randint(1, 10)
            G.add_edge(i, target, weight=weight)
    
    # แปลงกราฟเป็นรูปแบบ JSON ที่จะส่งไปยังหน้าเว็บ
    graph_data = {
        "nodes": [],
        "links": []
    }
    
    # เพิ่มโหนด
    for node in G.nodes():
        graph_data["nodes"].append({"id": node, "name": f"Node {node}"})
    
    # เพิ่มเส้นเชื่อม
    for u, v, data in G.edges(data=True):
        graph_data["links"].append({
            "source": u,
            "target": v,
            "weight": data["weight"]
        })
    
    return G, graph_data

def find_shortest_path(graph, start, end):
    """หาเส้นทางที่สั้นที่สุดด้วยอัลกอริทึม Dijkstra"""
    try:
        path = nx.dijkstra_path(graph, start, end, weight='weight')
        length = nx.dijkstra_path_length(graph, start, end, weight='weight')
        
        # สร้าง path edges สำหรับไฮไลท์
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        
        return {
            "path": path,
            "path_edges": path_edges,
            "length": length
        }
    except nx.NetworkXNoPath:
        return {
            "path": [],
            "path_edges": [],
            "length": -1
        }

def draw_graph_image(G, path_edges=None, start=None, end=None):
    """วาดกราฟและส่งเป็นรูปภาพ"""
    plt.figure(figsize=(10, 8))
    
    # กำหนดตำแหน่งโหนด
    pos = nx.spring_layout(G, seed=42)
    
    # วาดโหนดทั้งหมด
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=500)
    
    # วาดโหนดเริ่มต้นและสิ้นสุด (ถ้ามี)
    if start is not None and end is not None:
        nx.draw_networkx_nodes(G, pos, nodelist=[start, end], node_color='green', node_size=500)
    
    # วาดเส้นเชื่อมทั้งหมด
    nx.draw_networkx_edges(G, pos, width=1, alpha=0.5)
    
    # วาดเส้นทางที่สั้นที่สุด (ถ้ามี)
    if path_edges:
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=3, edge_color='red')
    
    # แสดงชื่อของโหนด
    nx.draw_networkx_labels(G, pos, font_size=12)
    
    # แสดงน้ำหนักของเส้นเชื่อม
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    plt.axis('off')
    plt.tight_layout()
    
    # บันทึกภาพลงในไฟล์ชั่วคราว
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    
    # แปลงเป็น base64 สำหรับใช้ใน HTML
    img_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return img_base64

@app.route('/')
def index():
    # สร้างกราฟใหม่เมื่อโหลดหน้าเว็บ
    global G
    G, graph_data = generate_random_graph()
    
    # วาดกราฟและส่งไปยังหน้าเว็บ
    img_base64 = draw_graph_image(G)
    
    return render_template('index.html', 
                           graph_data=json.dumps(graph_data),
                           nodes=range(len(G.nodes)),
                           graph_image=img_base64)

@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.get_json()
    start = int(data['start'])
    end = int(data['end'])
    
    # หาเส้นทางที่สั้นที่สุด
    result = find_shortest_path(G, start, end)
    
    # วาดกราฟใหม่พร้อมเส้นทาง
    img_base64 = draw_graph_image(G, result["path_edges"], start, end)
    
    return jsonify({
        'path': result["path"],
        'length': result["length"],
        'graph_image': img_base64
    })

@app.route('/new_graph', methods=['POST'])
def new_graph():
    global G
    G, graph_data = generate_random_graph()
    
    # วาดกราฟใหม่
    img_base64 = draw_graph_image(G)
    
    return jsonify({
        'graph_data': graph_data,
        'graph_image': img_base64
    })

if __name__ == '__main__':
    # สร้างกราฟครั้งแรก
    G, _ = generate_random_graph()
    app.run(host='0.0.0.0', port=5000, debug=True)
