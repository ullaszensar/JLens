import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import random

def visualize_project_structure(structure):
    """
    Creates a visualization of the project structure.
    
    Args:
        structure (dict): The hierarchical structure of the project.
        
    Returns:
        go.Figure: A Plotly figure representing the project structure.
    """
    if not structure:
        return go.Figure()
    
    # Function to flatten the hierarchical structure into parent-child pairs
    def get_edges(node, parent=None):
        edges = []
        node_id = node.get('path', node.get('name', ''))
        
        if parent:
            edges.append((parent, node_id))
        
        if 'children' in node:
            for child in node['children']:
                edges.extend(get_edges(child, node_id))
        
        return edges
    
    # Function to get all nodes with their attributes
    def get_nodes(node):
        nodes = []
        node_id = node.get('path', node.get('name', ''))
        node_name = node.get('name', '')
        node_type = node.get('type', 'directory')
        
        nodes.append((node_id, {'name': node_name, 'type': node_type}))
        
        if 'children' in node:
            for child in node['children']:
                nodes.extend(get_nodes(child))
        
        return nodes
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for node_id, attrs in get_nodes(structure):
        G.add_node(node_id, **attrs)
    
    # Add edges
    G.add_edges_from(get_edges(structure))
    
    # Use spring layout instead of graphviz (which requires pygraphviz)
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Create node traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Get node attributes
        attrs = G.nodes[node]
        node_name = attrs.get('name', node)
        node_type = attrs.get('type', 'directory')
        
        # Create node text for hover info
        node_text.append(f"{node_name}<br>Type: {node_type}")
        
        # Set color based on node type
        if node_type == 'file':
            if node_name.endswith('.java'):
                node_color.append('#1f77b4')  # Java files
            else:
                node_color.append('#ff7f0e')  # Other files
        else:
            node_color.append('#2ca02c')  # Directories
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=10,
            line_width=2))
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='Project Structure',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    return fig

def visualize_api_calls(apis):
    """
    Creates a visualization of API endpoints and their relationships.
    
    Args:
        apis (list): List of API endpoints.
        
    Returns:
        go.Figure: A Plotly figure representing the API calls.
    """
    if not apis:
        return go.Figure()
    
    # Convert APIs to DataFrame for easier handling
    if isinstance(apis, list):
        api_df = pd.DataFrame(apis)
    else:
        api_df = apis
    
    # Create a graph of API relationships
    G = nx.DiGraph()
    
    # Group APIs by class
    for class_name, group in api_df.groupby('class'):
        G.add_node(class_name, type='class')
        
        # Add API endpoints as nodes
        for _, api in group.iterrows():
            endpoint = f"{api['http_method']} {api['path']}"
            G.add_node(endpoint, type='endpoint', method=api['http_method'])
            G.add_edge(class_name, endpoint)
    
    # Use a spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Create edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Set node properties based on type
        node_type = G.nodes[node].get('type', 'unknown')
        
        if node_type == 'class':
            node_text.append(f"Class: {node}")
            node_color.append('#2ca02c')  # Green for classes
            node_size.append(15)
        else:
            method = G.nodes[node].get('method', 'GET')
            color_map = {
                'GET': '#1f77b4',  # Blue
                'POST': '#ff7f0e',  # Orange
                'PUT': '#9467bd',  # Purple
                'DELETE': '#d62728'  # Red
            }
            node_color.append(color_map.get(method, '#7f7f7f'))
            node_size.append(10)
            node_text.append(f"API: {node}")
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=2))
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='API Relationships',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    return fig

def visualize_flow(dependencies):
    """
    Visualizes the flow and dependencies between classes.
    
    Args:
        dependencies (dict): Dictionary of class dependencies.
        
    Returns:
        go.Figure: A Plotly figure representing the project flow.
    """
    if not dependencies:
        return go.Figure()
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes and edges from dependencies
    for class_name, deps in dependencies.items():
        # Add the class as a node
        package = deps.get('package', '')
        G.add_node(class_name, package=package)
        
        # Add dependencies as edges
        for used_class in deps.get('uses', []):
            G.add_edge(class_name, used_class)
    
    # Use a spring layout with some separation
    pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
    
    # Create edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        if edge[0] in pos and edge[1] in pos:  # Check if positions exist
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    # Group nodes by package
    packages = {}
    for node in G.nodes():
        if node in pos:  # Check if position exists
            package = G.nodes[node].get('package', 'default')
            if package not in packages:
                packages[package] = []
            packages[package].append(node)
    
    # Create node traces for each package (to have different colors)
    node_traces = []
    for package, nodes in packages.items():
        node_x = []
        node_y = []
        node_text = []
        
        for node in nodes:
            if node in pos:  # Check if position exists
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Create node text
                short_name = node.split('.')[-1]
                node_text.append(f"Class: {short_name}<br>Package: {package}")
        
        # Generate a consistent color for the package
        r, g, b = random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)
        color = f'rgb({r},{g},{b})'
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            name=package,
            marker=dict(
                color=color,
                size=10,
                line_width=2))
        
        node_traces.append(node_trace)
    
    # Create figure with all traces
    fig = go.Figure(data=[edge_trace] + node_traces,
                 layout=go.Layout(
                    title='Project Flow and Dependencies',
                    titlefont_size=16,
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    return fig
