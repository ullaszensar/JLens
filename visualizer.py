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
    Visualizes the logical flow and dependencies between classes using a flow diagram.
    
    Args:
        dependencies (dict): Dictionary of class dependencies.
        
    Returns:
        go.Figure: A Plotly figure representing the project's logical flow.
    """
    if not dependencies:
        return go.Figure()
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Group nodes by package
    packages = {}
    
    # Add nodes and edges from dependencies
    for class_name, deps in dependencies.items():
        # Try to extract package info
        parts = class_name.split('.')
        package = '.'.join(parts[:-1]) if len(parts) > 1 else 'default'
        
        # Track packages for better visualization
        if package not in packages:
            packages[package] = []
        packages[package].append(class_name)
        
        # Add the class as a node with package info
        G.add_node(class_name, package=package)
        
        # Add inheritance and implementation edges with special types
        if 'extends' in deps and deps['extends']:
            G.add_edge(class_name, deps['extends'], relationship='extends')
        
        if 'implements' in deps:
            for interface in deps['implements']:
                G.add_edge(class_name, interface, relationship='implements')
        
        # Add dependencies as standard edges
        for used_class in deps.get('uses', []):
            # Skip edges already created by extends/implements
            if 'extends' in deps and used_class == deps['extends']:
                continue
            if 'implements' in deps and used_class in deps['implements']:
                continue
                
            G.add_edge(class_name, used_class, relationship='uses')
    
    # Try to use a hierarchical layout for better flow visualization
    try:
        # Try to use graphviz's dot algorithm for a top-down view
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    except:
        # Fallback to spring layout with some tuning
        pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
    
    # Create edge traces with different colors/styles by relationship type
    edge_traces = []
    
    # Track which relationship types we've added for legend purposes
    relationship_types = set()
    
    for edge in G.edges(data=True):
        source, target, data = edge
        if source not in pos or target not in pos:  # Skip if nodes don't have positions
            continue
            
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        
        # Get relationship type
        relationship = data.get('relationship', 'uses')
        relationship_types.add(relationship)
        
        # Choose style based on relationship type
        if relationship == 'extends':
            edge_color = 'rgba(255, 0, 0, 0.6)'  # Red for inheritance
            width = 2
            dash = None
        elif relationship == 'implements':
            edge_color = 'rgba(0, 0, 255, 0.6)'  # Blue for implementation 
            width = 2
            dash = 'dash'
        else:  # uses
            edge_color = 'rgba(128, 128, 128, 0.6)'  # Gray for usage
            width = 1
            dash = None
        
        # Create custom arrow shapes using scatter with markers
        # Draw line
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=width, color=edge_color, dash=dash),
            hoverinfo='text',
            text=f"{source.split('.')[-1]} {relationship} {target.split('.')[-1]}",
            mode='lines',
            showlegend=relationship not in relationship_types,
            name=relationship.capitalize())
        
        edge_traces.append(edge_trace)
        
        # Mark the relationship as added for legend purposes
        relationship_types.discard(relationship)
    
    # Assign colors to packages for better grouping
    package_colors = {}
    colorscale = px.colors.qualitative.Pastel
    for i, package in enumerate(packages.keys()):
        package_colors[package] = colorscale[i % len(colorscale)]
    
    # Create node traces for each package
    node_traces = []
    for package, nodes in packages.items():
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        for node in nodes:
            if node in pos:  # Check if position exists
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Determine node color, size and shape based on class type
                short_name = node.split('.')[-1]
                
                if 'Controller' in short_name:
                    node_type = 'Controller'
                    node_size.append(15)
                elif 'Service' in short_name:
                    node_type = 'Service'
                    node_size.append(12)
                elif 'Repository' in short_name or 'DAO' in short_name:
                    node_type = 'Repository'
                    node_size.append(12)
                elif 'Model' in short_name or 'DTO' in short_name or 'Entity' in short_name:
                    node_type = 'Model'
                    node_size.append(10)
                elif 'Interface' in short_name or short_name.endswith('able'):
                    node_type = 'Interface'
                    node_size.append(10)
                else:
                    node_type = 'Class'
                    node_size.append(10)
                
                # Create descriptive hover text
                hover_text = f"<b>{short_name}</b><br>Type: {node_type}<br>Package: {package}"
                
                # Add class methods if present in the dependencies
                if node in dependencies and 'methods' in dependencies[node]:
                    methods = dependencies[node]['methods']
                    if methods:
                        hover_text += f"<br>Methods: {', '.join(methods[:3])}"
                        if len(methods) > 3:
                            hover_text += f" (+{len(methods)-3} more)"
                
                node_text.append(hover_text)
                node_color.append(package_colors[package])
        
        # Create a node trace for this package
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[n.split('.')[-1] for n in nodes if n in pos],  # Display short class names
            textposition='bottom center',
            hovertext=node_text,
            marker=dict(
                color=node_color,
                size=node_size,
                line_width=1,
                line=dict(color='black')),
            name=package,
            showlegend=True,
            textfont=dict(size=8))
        
        node_traces.append(node_trace)
    
    # Create figure with all traces
    fig = go.Figure(data=edge_traces + node_traces,
                 layout=go.Layout(
                    title=dict(text='Logical Flow Diagram', font=dict(size=18)),
                    showlegend=True,
                    legend=dict(
                        title="Components & Relationships",
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    annotations=[
                        dict(
                            text="Node colors represent packages; sizes represent importance in architecture",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.5, y=-0.1,
                            font=dict(size=10)
                        )
                    ]
                 ))
    
    return fig

def generate_class_diagram(functions, dependencies):
    """
    Creates a UML class diagram visualization similar to standard UML diagrams.
    
    Args:
        functions (dict): Dictionary of class functions.
        dependencies (dict): Dictionary of class dependencies.
        
    Returns:
        tuple: (go.Figure, list) A Plotly figure representing the UML class diagram and a list of relationships for the table.
    """
    if not functions or not dependencies:
        return go.Figure(), []
    
    import numpy as np
    
    # Filter to select top classes for better visualization
    # If too many classes, select a subset for clearer visualization
    MAX_CLASSES = 15
    if len(functions) > MAX_CLASSES:
        # Prioritize classes with relationships
        related_classes = set()
        for class_name, deps in dependencies.items():
            # Add this class
            related_classes.add(class_name)
            # Add parent class
            if deps.get('extends'):
                related_classes.add(deps.get('extends').split('.')[-1])
            # Add interfaces
            for interface in deps.get('implements', []):
                related_classes.add(interface.split('.')[-1])
            # Add some used classes
            for used in deps.get('uses', [])[:3]:  # Limit to 3 used classes
                related_classes.add(used.split('.')[-1])
        
        # If we still have too many, truncate
        if len(related_classes) > MAX_CLASSES:
            selected_classes = list(related_classes)[:MAX_CLASSES]
        else:
            selected_classes = list(related_classes)
            
        # Filter functions to only include selected classes
        filtered_functions = {k: v for k, v in functions.items() if k in selected_classes}
    else:
        filtered_functions = functions
    
    # Create a directed graph for the class relationships
    G = nx.DiGraph()
    
    # Keep track of relationships for the table
    all_relationships = []
    
    # Add classes as nodes with their attributes and methods
    for class_name, methods in filtered_functions.items():
        if not methods:
            continue
            
        # Separate attributes and methods based on naming conventions
        attributes = []
        class_methods = []
        
        for method in methods:
            method_name = method.get('name', '')
            return_type = method.get('return_type', '')
            params = method.get('parameters', [])
            
            # Add visibility prefix based on Java conventions
            visibility = '+'  # Default to public
            if method_name.startswith('_'):
                visibility = '-'  # Private
            
            # Determine if this is a field/attribute (no parameters, not void)
            if not params and method_name not in ['hashCode', 'toString', 'equals', 'main']:
                if (not method_name.startswith('get') and 
                    not method_name.startswith('set') and 
                    not method_name.startswith('is')):
                    attributes.append(f"{visibility}{method_name}: {return_type}")
                else:
                    # This could be a getter/setter, let's extract the field name
                    if method_name.startswith('get') or method_name.startswith('set'):
                        field_name = method_name[3:]
                        field_name = field_name[0].lower() + field_name[1:]
                        attributes.append(f"{visibility}{field_name}: {return_type}")
                    elif method_name.startswith('is'):
                        field_name = method_name[2:]
                        field_name = field_name[0].lower() + field_name[1:]
                        attributes.append(f"{visibility}{field_name}: boolean")
            else:
                # This is a method
                method_sig = f"{visibility}{method_name}({', '.join(params)}): {return_type}"
                class_methods.append(method_sig)
        
        # Add class to graph
        G.add_node(class_name, 
                   attributes=attributes, 
                   methods=class_methods)
    
    # Add relationships between classes
    for class_name, deps in dependencies.items():
        if class_name not in G:
            continue
            
        # Add inheritance relationship
        parent_class = deps.get('extends', '')
        if parent_class:
            parent_class_short = parent_class.split('.')[-1]
            if parent_class_short in G and class_name != parent_class_short:
                G.add_edge(class_name, parent_class_short, 
                           relationship_type='generalizes', 
                           label='extends',
                           description=f"{class_name} extends {parent_class_short}")
                all_relationships.append({
                    'source': class_name,
                    'target': parent_class_short,
                    'type': 'Generalization',
                    'description': f"{class_name} extends {parent_class_short}"
                })
        
        # Add implementation relationships
        for interface in deps.get('implements', []):
            interface_short = interface.split('.')[-1]
            if interface_short in G and class_name != interface_short:
                G.add_edge(class_name, interface_short, 
                          relationship_type='implements', 
                          label='implements',
                          description=f"{class_name} implements {interface_short}")
                all_relationships.append({
                    'source': class_name,
                    'target': interface_short,
                    'type': 'Implementation',
                    'description': f"{class_name} implements {interface_short}"
                })
        
        # Add association relationships (uses)
        for used_class in deps.get('uses', []):
            # Skip if already added as inheritance or implementation
            if used_class == parent_class:
                continue
                
            if used_class in deps.get('implements', []):
                continue
                
            used_class_short = used_class.split('.')[-1]
            if used_class_short in G and class_name != used_class_short:
                # Check if this might be a composition or aggregation
                relationship_type = 'associates with'
                
                # Simple heuristic - if class has a field of the used class type, 
                # it's likely an aggregation/composition
                found_attribute = False
                for attr in G.nodes[class_name].get('attributes', []):
                    if used_class_short in attr:
                        found_attribute = True
                        relationship_type = 'aggregates'
                        break
                        
                G.add_edge(class_name, used_class_short, 
                          relationship_type=relationship_type, 
                          label='uses',
                          description=f"{class_name} {relationship_type} {used_class_short}")
                
                rel_type = 'Aggregation' if relationship_type == 'aggregates' else 'Association'
                all_relationships.append({
                    'source': class_name,
                    'target': used_class_short,
                    'type': rel_type,
                    'description': f"{class_name} {relationship_type} {used_class_short}"
                })
    
    # If the graph is empty, return empty results
    if len(G.nodes()) == 0:
        return go.Figure(), []
        
    # Now draw the UML diagram using a better approach with shapes and annotations
    fig = go.Figure()
    
    # Positioning classes on the plot
    try:
        # Try using graphviz for proper hierarchical layout
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=BT')
    except:
        # Fallback to spring layout
        pos = nx.spring_layout(G, k=3.0, iterations=50, seed=42)
    
    # Normalize positions
    pos_values = list(pos.values())
    if not pos_values:
        return go.Figure(), []
        
    pos_array = np.array(pos_values)
    min_x, min_y = pos_array.min(axis=0)
    max_x, max_y = pos_array.max(axis=0)
    width = max_x - min_x
    height = max_y - min_y
    
    # Calculate class box sizes
    class_boxes = {}
    for class_name, node_attrs in G.nodes(data=True):
        # Count number of attributes and methods
        num_attrs = len(node_attrs.get('attributes', []))
        num_methods = len(node_attrs.get('methods', []))
        
        # Calculate box size proportional to content
        box_height = 30 + 20 * (num_attrs + num_methods)  # Base height + rows
        box_width = 160  # Fixed width but could adjust based on content
        
        class_boxes[class_name] = {
            'width': box_width,
            'height': box_height,
            'attrs': node_attrs.get('attributes', []),
            'methods': node_attrs.get('methods', [])
        }
    
    # Draw class boxes
    for class_name, box_info in class_boxes.items():
        x, y = pos[class_name]
        # Scale to 0-1 range
        x_normalized = (x - min_x) / width if width > 0 else 0.5
        y_normalized = (y - min_y) / height if height > 0 else 0.5
        
        # Calculate box corners in normalized coordinates
        half_width = box_info['width'] / 2 / 1000  # Scale to 0-1 range
        half_height = box_info['height'] / 2 / 1000  # Scale to 0-1 range
        
        # Define colors based on class type (could enhance based on stereotypes)
        if any('interface' in attr.lower() for attr in box_info['attrs']):
            fill_color = 'rgba(200, 230, 255, 0.8)'  # Light blue for interfaces
        elif 'abstract' in class_name.lower() or class_name.startswith('Abstract'):
            fill_color = 'rgba(255, 230, 200, 0.8)'  # Light orange for abstract classes
        else:
            fill_color = 'rgba(255, 255, 230, 0.8)'  # Light yellow for concrete classes
            
        # Draw the class box
        fig.add_shape(
            type="rect",
            x0=x_normalized - half_width,
            y0=y_normalized - half_height,
            x1=x_normalized + half_width,
            y1=y_normalized + half_height,
            line=dict(color="black", width=2),
            fillcolor=fill_color,
            layer="below"
        )
        
        # Draw divider lines in the class box
        attrs_y = y_normalized - half_height + 20/1000
        
        # Add class name
        fig.add_annotation(
            x=x_normalized,
            y=y_normalized - half_height + 10/1000,
            text=f"<b>{class_name}</b>",
            showarrow=False,
            font=dict(size=10),
            xref="paper",
            yref="paper"
        )
        
        # Add divider after class name
        fig.add_shape(
            type="line",
            x0=x_normalized - half_width,
            y0=attrs_y,
            x1=x_normalized + half_width,
            y1=attrs_y,
            line=dict(color="black", width=1),
            layer="below"
        )
        
        # Add attributes
        attr_spacing = 15/1000
        current_y = attrs_y + attr_spacing
        for i, attr in enumerate(box_info['attrs'][:5]):  # Limit to 5 attributes
            fig.add_annotation(
                x=x_normalized,
                y=current_y,
                text=attr,
                showarrow=False,
                font=dict(size=8),
                xref="paper",
                yref="paper"
            )
            current_y += attr_spacing
        
        # If there are more attrs, add a placeholder
        if len(box_info['attrs']) > 5:
            fig.add_annotation(
                x=x_normalized,
                y=current_y,
                text=f"...({len(box_info['attrs']) - 5} more)",
                showarrow=False,
                font=dict(size=8, color="gray"),
                xref="paper",
                yref="paper"
            )
            current_y += attr_spacing
        
        # Add divider before methods
        methods_y = current_y
        fig.add_shape(
            type="line",
            x0=x_normalized - half_width,
            y0=methods_y,
            x1=x_normalized + half_width,
            y1=methods_y,
            line=dict(color="black", width=1),
            layer="below"
        )
        
        # Add methods
        current_y = methods_y + attr_spacing
        for i, method in enumerate(box_info['methods'][:5]):  # Limit to 5 methods
            fig.add_annotation(
                x=x_normalized,
                y=current_y,
                text=method,
                showarrow=False,
                font=dict(size=8),
                xref="paper",
                yref="paper"
            )
            current_y += attr_spacing
            
        # If there are more methods, add a placeholder
        if len(box_info['methods']) > 5:
            fig.add_annotation(
                x=x_normalized,
                y=current_y,
                text=f"...({len(box_info['methods']) - 5} more)",
                showarrow=False,
                font=dict(size=8, color="gray"),
                xref="paper",
                yref="paper"
            )
    
    # Draw relationships
    for source, target, edge_data in G.edges(data=True):
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        # Normalize to 0-1 range
        x0_norm = (x0 - min_x) / width if width > 0 else 0.5
        y0_norm = (y0 - min_y) / height if height > 0 else 0.5
        x1_norm = (x1 - min_x) / width if width > 0 else 0.5
        y1_norm = (y1 - min_y) / height if height > 0 else 0.5
        
        relationship_type = edge_data.get('relationship_type', 'associates with')
        
        # Set line style based on relationship type
        if relationship_type == 'generalizes':
            # Inheritance - solid line with triangle arrowhead
            line_style = dict(color='black', width=2)
            marker_end = "triangle-up"
        elif relationship_type == 'implements':
            # Interface implementation - dashed line with triangle arrowhead
            line_style = dict(color='black', width=2, dash='dash')
            marker_end = "triangle-up"
        elif relationship_type == 'aggregates':
            # Aggregation - solid line with diamond arrowhead
            line_style = dict(color='black', width=1.5)
            marker_end = "diamond"
        else:
            # Association - solid thin line with arrow
            line_style = dict(color='black', width=1)
            marker_end = "arrow"
            
        # Draw the relationship line
        fig.add_trace(go.Scatter(
            x=[x0_norm, x1_norm],
            y=[y0_norm, y1_norm],
            mode='lines',
            line=line_style,
            hoverinfo='text',
            text=edge_data.get('description', f"{source} -> {target}"),
            showlegend=False
        ))
        
        # Draw arrowheads or special markers for relationship types
        # Calculate the direction of the edge
        dx = x1_norm - x0_norm
        dy = y1_norm - y0_norm
        
        # Calculate the position for the arrowhead (slightly before the target)
        arrow_length = 0.02
        norm = np.sqrt(dx**2 + dy**2)
        
        # Initialize defaults
        arrowhead_x = x1_norm
        arrowhead_y = y1_norm
        unit_x = 0
        unit_y = 0
        
        if norm > 0:
            unit_x = dx / norm
            unit_y = dy / norm
            arrowhead_x = x1_norm - unit_x * arrow_length
            arrowhead_y = y1_norm - unit_y * arrow_length
        
        # Add arrowhead or relationship marker
        if marker_end == "triangle-up":
            # Create a triangle for generalization or implementation
            fig.add_trace(go.Scatter(
                x=[arrowhead_x, x1_norm + (y0_norm - y1_norm) * 0.01, x1_norm - (y0_norm - y1_norm) * 0.01, arrowhead_x],
                y=[arrowhead_y, y1_norm - (x1_norm - x0_norm) * 0.01, y1_norm + (x1_norm - x0_norm) * 0.01, arrowhead_y],
                fill="toself",
                mode="lines",
                line=dict(color="black"),
                fillcolor="white",
                hoverinfo="none",
                showlegend=False
            ))
        elif marker_end == "diamond" and norm > 0:
            # Create a diamond for aggregation only if we have valid direction
            mid_x = (x0_norm + x1_norm) / 2
            mid_y = (y0_norm + y1_norm) / 2
            diamond_size = 0.015
            perp_x = -unit_y * diamond_size if unit_y else 0
            perp_y = unit_x * diamond_size if unit_x else 0
            
            fig.add_trace(go.Scatter(
                x=[mid_x - perp_x, mid_x + unit_x * diamond_size, 
                   mid_x + perp_x, mid_x - unit_x * diamond_size, mid_x - perp_x],
                y=[mid_y - perp_y, mid_y + unit_y * diamond_size, 
                   mid_y + perp_y, mid_y - unit_y * diamond_size, mid_y - perp_y],
                fill="toself",
                mode="lines",
                line=dict(color="black"),
                fillcolor="white",
                hoverinfo="none",
                showlegend=False
            ))
    
    # Generate a table of relationships
    relationship_table = []
    for rel in all_relationships:
        relationship_table.append(
            f"| {rel['source']} | {rel['type']} | {rel['target']} | {rel['description']} |"
        )
    
    # Set layout
    fig.update_layout(
        title=dict(text='UML Class Diagram', font=dict(size=18)),
        showlegend=False,
        plot_bgcolor='rgba(255, 255, 255, 1)',
        margin=dict(b=20, l=20, r=20, t=50),
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            constrain="domain"
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            scaleanchor="x", 
            scaleratio=1  # Keep aspect ratio to avoid distortion
        ),
        annotations=[
            dict(
                x=0.5,
                y=-0.05,
                xref="paper",
                yref="paper",
                text="Relationship types: ▲ Inheritance, ◇ Aggregation, → Association",
                showarrow=False,
                font=dict(size=10)
            )
        ]
    )
    
    # Return both the figure and relationship data for table creation
    return fig, relationship_table

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
