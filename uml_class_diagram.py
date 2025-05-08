def generate_class_diagram_html(functions, dependencies):
    """
    Creates a UML class diagram using HTML tables, similar to traditional UML notation.
    
    Args:
        functions (dict): Dictionary of class functions.
        dependencies (dict): Dictionary of class dependencies.
        
    Returns:
        tuple: (html, relationship_table) where html is the HTML for class diagrams and 
               relationship_table is a list of relationships for display in a table.
    """
    if not functions or not dependencies:
        return "No class data available", []
    
    import numpy as np
    
    # Filter to select top classes for better visualization
    MAX_CLASSES = 10
    if len(functions) > MAX_CLASSES:
        # Prioritize classes with relationships
        related_classes = set()
        for class_name, deps in dependencies.items():
            # Add this class
            related_classes.add(class_name)
            # Add parent class
            if deps.get('extends'):
                parent = deps.get('extends').split('.')[-1]
                related_classes.add(parent)
            # Add interfaces
            for interface in deps.get('implements', []):
                related_classes.add(interface.split('.')[-1])
            # Add some used classes
            for used in deps.get('uses', [])[:2]:  # Limit to 2 used classes
                related_classes.add(used.split('.')[-1])
        
        # If we still have too many, prioritize classes with more methods/attributes
        if len(related_classes) > MAX_CLASSES:
            class_size = {}
            for cls in related_classes:
                if cls in functions:
                    class_size[cls] = len(functions[cls])
                else:
                    class_size[cls] = 0
            
            selected_classes = sorted(class_size.items(), key=lambda x: x[1], reverse=True)[:MAX_CLASSES]
            selected_classes = [c[0] for c in selected_classes]
        else:
            selected_classes = list(related_classes)
            
        # Filter functions to only include selected classes
        filtered_functions = {k: v for k, v in functions.items() if k in selected_classes}
    else:
        filtered_functions = functions
        selected_classes = list(filtered_functions.keys())
    
    # Keep track of relationships for the table
    all_relationships = []
    
    # Define background colors for different class types
    class_colors = {
        'interface': '#D6EAF8',  # Light blue
        'abstract': '#FCF3CF',  # Light yellow
        'entity': '#D5F5E3',     # Light green
        'controller': '#FADBD8',  # Light red
        'service': '#E8DAEF',    # Light purple
        'default': '#F2F3F4'     # Light gray
    }
    
    # Build HTML for each class
    class_html = []
    
    # First pass: Extract attributes and methods for each class
    class_data = {}
    for class_name, methods in filtered_functions.items():
        # Get short class name for display
        short_name = class_name.split('.')[-1]
        
        # Skip if no methods
        if not methods:
            continue
            
        # Separate attributes and methods
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
            elif method_name.startswith('protected'):
                visibility = '#'  # Protected
            
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
                method_sig = f"{visibility}{method_name}({', '.join(params)}){': ' + return_type if return_type else ''}"
                class_methods.append(method_sig)
        
        # Store class data
        class_data[class_name] = {
            'short_name': short_name,
            'attributes': sorted(list(set(attributes))),  # Remove duplicates
            'methods': sorted(list(set(class_methods)))  # Remove duplicates
        }
    
    # Second pass: Determine class colors and create HTML
    for class_name, data in class_data.items():
        short_name = data['short_name']
        attributes = data['attributes']
        class_methods = data['methods']
        
        # Determine class color based on name/type
        color = class_colors['default']
        if 'Interface' in short_name or short_name.endswith('able'):
            color = class_colors['interface']
        elif 'Abstract' in short_name:
            color = class_colors['abstract']
        elif 'Entity' in short_name or 'Model' in short_name:
            color = class_colors['entity']
        elif 'Controller' in short_name:
            color = class_colors['controller']
        elif 'Service' in short_name:
            color = class_colors['service']
        
        # Build HTML table for this class
        table_html = f'''
        <table class="uml-class-table" style="border-collapse: collapse; border: 1px solid black; margin: 10px; float: left;">
            <tr>
                <th style="background-color: {color}; text-align: center; padding: 5px; border: 1px solid black; font-weight: bold;">{short_name}</th>
            </tr>
            <tr>
                <td style="border: 1px solid black; padding: 5px;">
                    {'<br>'.join(attributes) if attributes else '&nbsp;'}
                </td>
            </tr>
            <tr>
                <td style="border: 1px solid black; padding: 5px;">
                    {'<br>'.join(class_methods) if class_methods else '&nbsp;'}
                </td>
            </tr>
        </table>
        '''
        
        class_html.append(table_html)
    
    # Third pass: Extract relationships for display
    for class_name, deps in dependencies.items():
        # Skip if not in our selected classes
        if class_name not in selected_classes:
            continue
            
        short_name = class_name.split('.')[-1]
        
        # Add inheritance relationship
        parent_class = deps.get('extends', '')
        if parent_class:
            parent_short = parent_class.split('.')[-1]
            # Only add if both classes are in our diagram
            if parent_class in selected_classes or parent_short in [c.split('.')[-1] for c in selected_classes]:
                all_relationships.append({
                    'source': short_name,
                    'target': parent_short,
                    'type': 'Generalization',
                    'description': f"{short_name} extends {parent_short}"
                })
        
        # Add implementation relationships
        for interface in deps.get('implements', []):
            interface_short = interface.split('.')[-1]
            # Only add if interface is in our diagram
            if interface in selected_classes or interface_short in [c.split('.')[-1] for c in selected_classes]:
                all_relationships.append({
                    'source': short_name,
                    'target': interface_short,
                    'type': 'Implementation',
                    'description': f"{short_name} implements {interface_short}"
                })
        
        # Add association relationships
        for used_class in deps.get('uses', []):
            # Skip if already covered by inheritance or implementation
            if used_class == parent_class:
                continue
                
            if used_class in deps.get('implements', []):
                continue
                
            used_short = used_class.split('.')[-1]
            # Only add if used class is in our diagram
            if used_class in selected_classes or used_short in [c.split('.')[-1] for c in selected_classes]:
                # Check type of association (aggregation vs regular)
                is_aggregation = False
                
                # Check if this class has an attribute of the used class type
                for method in filtered_functions.get(class_name, []):
                    attr_name = method.get('name', '')
                    return_type = method.get('return_type', '')
                    if not method.get('parameters') and (used_short in return_type or used_short in attr_name):
                        is_aggregation = True
                        break
                
                rel_type = 'Aggregation' if is_aggregation else 'Association'
                all_relationships.append({
                    'source': short_name,
                    'target': used_short,
                    'type': rel_type,
                    'description': f"{short_name} {rel_type.lower()} {used_short}"
                })
    
    # Combine all class tables into a single HTML
    html = f'''
    <div style="display: flex; flex-wrap: wrap; justify-content: center;">
        {''.join(class_html)}
    </div>
    <div style="clear: both;"></div>
    <div style="font-size: 0.9em; margin-top: 20px; text-align: center;">
        UML Class Diagram - <b>JLens</b>
    </div>
    '''
    
    # Format relationships for the table
    relationship_table = []
    for rel in all_relationships:
        relationship_table.append(
            f"| {rel['source']} | {rel['type']} | {rel['target']} | {rel['description']} |"
        )
    
    return html, relationship_table