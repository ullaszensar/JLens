import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import random
import re
from plotly.subplots import make_subplots

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
                    title=dict(text='Project Structure', font=dict(size=16)),
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
                    title=dict(text='API Relationships', font=dict(size=16)),
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
                    title=dict(text='Project Flow and Dependencies', font=dict(size=16)),
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    return fig

def generate_class_diagram(functions, dependencies):
    """
    Creates a UML-like class diagram visualization.
    
    Args:
        functions (dict): Dictionary of class functions.
        dependencies (dict): Dictionary of class dependencies.
        
    Returns:
        go.Figure: A Plotly figure representing the class diagram.
    """
    if not functions or not dependencies:
        return go.Figure()
    
    # Create a directed graph for the class diagram
    G = nx.DiGraph()
    
    # Add classes as nodes with their methods
    for class_name, methods in functions.items():
        method_list = []
        for method in methods:
            method_signature = f"{method['name']}({', '.join(method['parameters'])}): {method['return_type']}"
            method_list.append(method_signature)
        
        # Create a label with class name and methods
        label = f"{class_name}\n"
        if method_list:
            label += "---\n" + "\n".join(method_list[:5])  # Show just a few methods to keep diagram readable
            if len(method_list) > 5:
                label += f"\n...({len(method_list) - 5} more)"
        
        G.add_node(class_name, label=label)
    
    # Add relationships from dependencies
    for class_name, deps in dependencies.items():
        if class_name in G:  # Only process classes that are in our functions
            for used_class in deps.get('uses', []):
                # Extract the class name from fully qualified name
                used_class_short = used_class.split('.')[-1]
                relationship_type = 'uses'
                
                # Check if this is an inheritance relationship
                if deps.get('extends', '') == used_class_short:
                    relationship_type = 'extends'
                
                # Check if this is an implementation relationship
                if used_class_short in deps.get('implements', []):
                    relationship_type = 'implements'
                
                # Only add edge if both classes are in our graph
                if used_class_short in G and class_name != used_class_short:
                    G.add_edge(class_name, used_class_short, relationship=relationship_type)
    
    # Use hierarchical layout for better UML diagram appearance
    pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)
    
    # Create edges with different styles based on relationship type
    edge_traces = []
    
    for src, dst, data in G.edges(data=True):
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        
        # Set line style based on relationship
        relationship = data.get('relationship', 'uses')
        if relationship == 'extends':
            line_style = dict(color='red', width=2)
        elif relationship == 'implements':
            line_style = dict(color='blue', width=2, dash='dash')
        else:
            line_style = dict(color='gray', width=1)
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=line_style,
            hoverinfo='text',
            text=relationship,
            mode='lines')
        
        edge_traces.append(edge_trace)
    
    # Create node boxes for classes
    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        text=[G.nodes[node]['label'] for node in G.nodes()],
        mode='markers+text',
        textposition='top center',
        marker=dict(
            color='lightblue',
            size=30,
            line=dict(color='black', width=1)),
        hoverinfo='text')
    
    # Create the figure
    fig = go.Figure(data=edge_traces + [node_trace],
                 layout=go.Layout(
                    title=dict(text='Class Diagram', font=dict(size=16)),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    return fig

def generate_sequence_diagram(apis, functions):
    """
    Creates a sequence diagram visualization focusing on API flows.
    
    Args:
        apis (list): List of API endpoints.
        functions (dict): Dictionary of class functions.
        
    Returns:
        go.Figure: A Plotly figure representing the sequence diagram.
    """
    if not apis or not functions:
        return go.Figure()
    
    # Select a few representative APIs to visualize (to avoid overcrowding)
    if len(apis) > 5:
        selected_apis = apis[:5]  # Take just the first 5 APIs
    else:
        selected_apis = apis
    
    # Create a figure with a timeline layout
    fig = go.Figure()
    
    # Calculate height based on the number of components
    height = max(600, 200 * len(selected_apis))
    
    # Define components (actors in sequence diagram)
    components = ['Client']
    for api in selected_apis:
        components.append(api['class'])
    
    # Make components unique
    components = list(dict.fromkeys(components))
    
    # Define x positions for each component
    x_positions = {comp: i/(len(components)-1) if len(components) > 1 else 0.5 for i, comp in enumerate(components)}
    
    # Add component labels at the top
    for comp, x_pos in x_positions.items():
        fig.add_annotation(
            x=x_pos,
            y=1.05,
            text=comp,
            showarrow=False,
            font=dict(size=12, color='black'),
            xref='paper',
            yref='paper'
        )
        
        # Add vertical lifelines
        fig.add_shape(
            type='line',
            x0=x_pos,
            y0=0,
            x1=x_pos,
            y1=1,
            line=dict(color='gray', width=1, dash='dash'),
            xref='paper',
            yref='paper'
        )
    
    # Add sequence flows for each API
    for i, api in enumerate(selected_apis):
        # Y position for this sequence (normalized between 0 and 1)
        y_pos = 1 - (i + 1) / (len(selected_apis) + 1)
        
        # Client to Controller message
        fig.add_shape(
            type='line',
            x0=x_positions['Client'],
            y0=y_pos,
            x1=x_positions[api['class']],
            y1=y_pos,
            line=dict(color='blue', width=2, dash='solid'),
            xref='paper',
            yref='paper'
        )
        
        # Add message label
        mid_x = (x_positions['Client'] + x_positions[api['class']]) / 2
        fig.add_annotation(
            x=mid_x,
            y=y_pos + 0.02,
            text=f"{api['http_method']} {api['path']}",
            showarrow=False,
            font=dict(size=10),
            xref='paper',
            yref='paper'
        )
        
        # Return message
        fig.add_shape(
            type='line',
            x0=x_positions[api['class']],
            y0=y_pos - 0.05,
            x1=x_positions['Client'],
            y1=y_pos - 0.05,
            line=dict(color='green', width=2, dash='solid'),
            xref='paper',
            yref='paper'
        )
        
        # Add return label
        fig.add_annotation(
            x=mid_x,
            y=y_pos - 0.07,
            text="Response",
            showarrow=False,
            font=dict(size=10),
            xref='paper',
            yref='paper'
        )
    
    # Set layout
    fig.update_layout(
        title=dict(text='Sequence Diagram', font=dict(size=16)),
        showlegend=False,
        height=height,
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1])
    )
    
    return fig

def generate_functional_flow(apis, functions, batch_processes):
    """
    Creates a functional flow diagram showing the business logic flow.
    
    Args:
        apis (list): List of API endpoints.
        functions (dict): Dictionary of class functions.
        batch_processes (list): List of batch processes.
        
    Returns:
        go.Figure: A Plotly figure representing the functional flow.
    """
    # Create a directed graph for the functional flow
    G = nx.DiGraph()
    
    # Group APIs by functionality (using path patterns)
    api_groups = {}
    for api in apis:
        # Extract main resource from path (e.g., /users/123 -> users)
        path = api['path']
        parts = path.strip('/').split('/')
        if parts:
            resource = parts[0]
            if resource not in api_groups:
                api_groups[resource] = []
            api_groups[resource].append(api)
    
    # Add API groups as nodes
    for resource, apis_list in api_groups.items():
        label = f"{resource.title()} API\n({len(apis_list)} endpoints)"
        G.add_node(resource, type='api', label=label)
    
    # Add service classes as nodes
    for class_name, methods in functions.items():
        if 'Service' in class_name:
            short_name = class_name.split('.')[-1]
            G.add_node(short_name, type='service', label=short_name)
            
            # Try to link services to API groups
            for resource in api_groups.keys():
                # If the service name contains the resource name, add an edge
                if resource.lower() in short_name.lower():
                    G.add_edge(resource, short_name)
    
    # Add repository/DAO classes
    for class_name, methods in functions.items():
        if 'Repository' in class_name or 'DAO' in class_name:
            short_name = class_name.split('.')[-1]
            G.add_node(short_name, type='repository', label=short_name)
            
            # Link repositories to services
            for svc_node in [n for n, d in G.nodes(data=True) if d.get('type') == 'service']:
                # If the repository relates to a service by name
                if any(part.lower() in svc_node.lower() for part in short_name.split('Repository')[0].split('DAO')[0].split('_')):
                    G.add_edge(svc_node, short_name)
    
    # Add batch processes
    for i, batch in enumerate(batch_processes):
        if 'class' in batch:
            batch_name = f"Batch: {batch['class']}"
            G.add_node(batch_name, type='batch', label=batch_name)
            
            # Try to link batch to repositories
            for repo_node in [n for n, d in G.nodes(data=True) if d.get('type') == 'repository']:
                G.add_edge(batch_name, repo_node)
    
    # If graph is empty, add placeholder
    if not G.nodes():
        return go.Figure(layout=go.Layout(
            title=dict(text="No data available for Functional Flow Diagram", font=dict(size=16))))
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=100, seed=42)
    
    # Create edges
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
    
    # Create nodes
    node_traces = []
    
    # Define colors for different node types
    colors = {
        'api': 'rgba(31, 119, 180, 0.8)',  # Blue
        'service': 'rgba(255, 127, 14, 0.8)',  # Orange
        'repository': 'rgba(44, 160, 44, 0.8)',  # Green
        'batch': 'rgba(214, 39, 40, 0.8)'  # Red
    }
    
    # Group nodes by type
    for node_type, color in colors.items():
        nodes = [n for n, d in G.nodes(data=True) if d.get('type') == node_type]
        if not nodes:
            continue
            
        node_x = []
        node_y = []
        node_text = []
        
        for node in nodes:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(G.nodes[node].get('label', node))
        
        trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition='bottom center',
            name=node_type.capitalize(),
            marker=dict(
                color=color,
                size=20,
                line=dict(color='black', width=1)),
            hoverinfo='text')
        
        node_traces.append(trace)
    
    # Create the figure
    fig = go.Figure(data=[edge_trace] + node_traces,
                 layout=go.Layout(
                    title=dict(text='Functional Flow Diagram', font=dict(size=16)),
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
