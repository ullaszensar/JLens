import streamlit as st
import os
import tempfile
import zipfile
import shutil
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from java_parser import JavaProjectParser
from visualizer import (
    visualize_project_structure, visualize_api_calls, visualize_flow,
    generate_class_diagram, generate_sequence_diagram, generate_functional_flow
)
from uml_class_diagram import generate_class_diagram_html
from utils import (
    create_data_tables, get_file_content, get_csv_download_link,
    get_json_download_link, get_figure_download_link, format_tree_data_for_csv
)

# Set page configuration
st.set_page_config(
    page_title="JLens - Zensar Diamond Team",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Default values for analysis options
analyze_apis = False
analyze_functions = False
analyze_batch = False
analyze_flow = False

# App title and description
st.title("🔍 JLens - Zensar Diamond Team")
st.subheader("Java J2EE Project Scanner & Analyzer")
st.markdown("""
    Upload your Java J2EE project (ZIP file) to analyze its structure, APIs, functions, and batch processes.
    JLens will provide visualizations and insights into your project's architecture.
""")

# Sidebar for file upload and options
with st.sidebar:
    st.header("Upload Project")
    uploaded_file = st.file_uploader("Choose a ZIP file containing your Java J2EE project", type=["zip"])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        # Analysis options
        st.header("Analysis Options")
        analyze_apis = st.checkbox("Analyze APIs", value=True, key="analyze_apis")
        analyze_functions = st.checkbox("Analyze Functions", value=True, key="analyze_functions")
        analyze_batch = st.checkbox("Analyze Batch Processes", value=True, key="analyze_batch")
        analyze_flow = st.checkbox("Visualize Project Flow", value=True, key="analyze_flow")

# Main content area
if uploaded_file is not None:
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create a temporary directory to extract files
    with tempfile.TemporaryDirectory() as temp_dir:
        status_text.text("Extracting ZIP file...")
        
        # Save the uploaded zip file to the temp directory
        zip_path = os.path.join(temp_dir, "project.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract the zip file
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        progress_bar.progress(20)
        status_text.text("Analyzing Java files...")
        
        # Parse the Java project
        parser = JavaProjectParser(extract_dir)
        project_data = parser.parse_project()
        
        progress_bar.progress(60)
        status_text.text("Generating visualizations...")
        
        # Add Project Summary Card first
        st.header("Project Summary")
        
        # Get project summary data
        summary = project_data.get('project_summary', {})
        
        # Create a grid layout for summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", summary.get('total_files', 0))
            st.metric("Java Files", summary.get('java_files', 0))
            
        with col2:
            st.metric("Total Classes", summary.get('total_classes', 0))
            st.metric("Total Lines of Code", summary.get('total_lines', 0))
            
        with col3:
            st.metric("APIs Detected", summary.get('apis_count', 0))
            st.metric("Batch Jobs", summary.get('batch_jobs', 0))
        
        # Add libraries used in an expander
        with st.expander("Libraries Used"):
            libraries = summary.get('libraries_used', [])
            if libraries:
                st.write(", ".join(libraries))
            else:
                st.info("No libraries detected")
        
        # Add a separator
        st.markdown("---")
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "Project Structure", 
            "APIs", 
            "Functions", 
            "Batch Processes",
            "Logical Flow",
            "UML Class Diagram",
            "Sequence Diagram",
            "Functional Flow"
        ])
        
        # Tab 1: Project Structure
        with tab1:
            st.header("Project Structure")
            
            # Create subtabs for different structure views
            struct_tab1, struct_tab2, struct_tab3, struct_tab4 = st.tabs([
                "Hierarchical View", 
                "Files Distribution", 
                "MVC Components",
                "Dependencies"
            ])
            
            # Tab 1.1: Hierarchical Directory Tree View
            with struct_tab1:
                st.subheader("Directory Tree View")
                # Display project structure as a tree
                structure_fig = visualize_project_structure(project_data['structure'])
                
                # Safety check before displaying
                if structure_fig and isinstance(structure_fig, go.Figure):
                    st.plotly_chart(structure_fig, use_container_width=True)
                    
                    # Add export options
                    st.markdown("#### Export Structure Visualization")
                    st.markdown(get_figure_download_link(structure_fig, "project_structure.html", 
                                "💾 Download structure visualization as interactive HTML"), unsafe_allow_html=True)
                else:
                    st.info("Unable to generate project structure visualization with the current data.")
                
                # Also display the structure as a text tree for easier reading
                st.subheader("Directory Text Tree")
                
                # Function to build a text tree representation
                def build_text_tree(node, indent="", is_last=True):
                    # Get the node name
                    node_name = node.get('name', '')
                    
                    # Determine branch connector based on whether this is the last item
                    branch = "└── " if is_last else "├── "
                    
                    # Create the line for this node
                    line = f"{indent}{branch}{node_name}"
                    
                    # Add node type indicator if available
                    if 'type' in node and node['type'] == 'file':
                        if node_name.endswith('.java'):
                            line += " [Java]"
                    
                    text_tree = [line]
                    
                    # Continue building tree if there are children
                    if 'children' in node and node['children']:
                        # Update indent for children
                        child_indent = indent + ("    " if is_last else "│   ")
                        
                        # Process children
                        children = node['children']
                        for i, child in enumerate(children):
                            is_child_last = (i == len(children) - 1)
                            text_tree.extend(build_text_tree(child, child_indent, is_child_last))
                    
                    return text_tree
                
                # Create text tree representation
                if 'structure' in project_data:
                    text_tree_lines = build_text_tree(project_data['structure'])
                    
                    # Display the text tree in a code block
                    st.code('\n'.join(text_tree_lines), language=None)
            
            # Tab 1.2: Files Distribution
            with struct_tab2:
                st.subheader("Files Distribution")
                files_by_type = project_data['file_types_count']
                
                # Display as a bar chart
                st.bar_chart(files_by_type)
                
                # Also display the raw counts
                st.dataframe(pd.DataFrame({
                    'File Type': files_by_type.index,
                    'Count': files_by_type.values
                }))
            
            # Tab 1.3: MVC Structure (Controllers, Services, DAOs)
            with struct_tab3:
                st.subheader("MVC Components")
                
                # Extract Controllers, Services, DAOs from functions
                controllers = []
                services = []
                daos = []
                
                for class_name, methods in project_data.get('functions', {}).items():
                    # Check if the class is a controller, service, or DAO
                    if 'Controller' in class_name:
                        controllers.append({
                            'Class Name': class_name,
                            'Methods Count': len(methods),
                            'File': methods[0]['file'] if methods else "Unknown"
                        })
                    elif 'Service' in class_name:
                        services.append({
                            'Class Name': class_name,
                            'Methods Count': len(methods),
                            'File': methods[0]['file'] if methods else "Unknown"
                        })
                    elif 'DAO' in class_name or 'Repository' in class_name:
                        daos.append({
                            'Class Name': class_name,
                            'Methods Count': len(methods),
                            'File': methods[0]['file'] if methods else "Unknown"
                        })
                
                # Create expandable sections for each component
                with st.expander("Controllers", expanded=True):
                    if controllers:
                        st.dataframe(pd.DataFrame(controllers))
                    else:
                        st.info("No Controllers found in the project.")
                
                with st.expander("Services", expanded=True):
                    if services:
                        st.dataframe(pd.DataFrame(services))
                    else:
                        st.info("No Services found in the project.")
                
                with st.expander("DAOs / Repositories", expanded=True):
                    if daos:
                        st.dataframe(pd.DataFrame(daos))
                    else:
                        st.info("No DAOs or Repositories found in the project.")
                
                # Also add entities if available
                entities = []
                for class_name, methods in project_data.get('functions', {}).items():
                    if 'Entity' in class_name or 'Model' in class_name or 'DTO' in class_name:
                        entities.append({
                            'Class Name': class_name,
                            'Fields/Methods Count': len(methods),
                            'File': methods[0]['file'] if methods else "Unknown"
                        })
                
                with st.expander("Entities / Models", expanded=True):
                    if entities:
                        st.dataframe(pd.DataFrame(entities))
                    else:
                        st.info("No Entities or Models found in the project.")
            
            # Tab 1.4: Dependencies
            with struct_tab4:
                st.subheader("Project Dependencies")
                
                # Extract dependencies from pom.xml or build.gradle if available
                st.text("Project Dependencies from configuration files:")
                
                # Find and extract dependencies from project files
                dependencies_found = False
                for java_file in project_data.get('java_files', []):
                    if 'pom.xml' in java_file:
                        dependencies_found = True
                        file_path = os.path.join(extract_dir, java_file)
                        content = get_file_content(file_path)
                        st.code(content, language="xml")
                        break
                    elif 'build.gradle' in java_file:
                        dependencies_found = True
                        file_path = os.path.join(extract_dir, java_file)
                        content = get_file_content(file_path)
                        st.code(content, language="gradle")
                        break
                
                if not dependencies_found:
                    st.info("No dependency files (pom.xml or build.gradle) found in the project.")
        
        # Tab 2: APIs
        with tab2:
            st.header("APIs")
            
            if analyze_apis and 'apis' in project_data and project_data['apis']:
                # Display API endpoints table
                st.subheader("API Endpoints")
                api_df = create_data_tables(project_data['apis'])
                st.dataframe(api_df, use_container_width=True)
                
                # Add export option for data
                st.markdown("#### Export API Data")
                st.markdown(get_csv_download_link(api_df, "api_endpoints.csv", "💾 Download API data as CSV"), unsafe_allow_html=True)
                st.markdown(get_json_download_link(project_data['apis'], "api_endpoints.json", "💾 Download API data as JSON"), unsafe_allow_html=True)
                
                # Visualize API relationships
                st.subheader("API Relationships")
                api_fig = visualize_api_calls(project_data['apis'])
                
                # Safety check before displaying
                if api_fig and isinstance(api_fig, go.Figure):
                    st.plotly_chart(api_fig, use_container_width=True)
                    
                    # Add export option for chart
                    st.markdown("#### Export API Visualization")
                    st.markdown(get_figure_download_link(api_fig, "api_relationships.html", "💾 Download chart as interactive HTML"), unsafe_allow_html=True)
                else:
                    st.info("Unable to generate API visualization with the current data.")
            else:
                st.info("No APIs were detected or API analysis was not selected.")
        
        # Tab 3: Functions
        with tab3:
            st.header("Functions/Methods")
            
            if analyze_functions and 'functions' in project_data and project_data['functions']:
                # Create filter for class selection
                classes = list(project_data['functions'].keys())
                selected_class = st.selectbox("Select a class to view its methods:", ["All Classes"] + classes)
                
                # Prepare data for table view
                all_methods = []
                
                if selected_class == "All Classes":
                    # Show methods from all classes
                    for class_name, methods in project_data['functions'].items():
                        for method in methods:
                            all_methods.append({
                                'Class': class_name,
                                'Method': method['name'],
                                'Return Type': method['return_type'],
                                'Parameters': ', '.join(method['parameters']) if method['parameters'] else 'None',
                                'File': os.path.basename(method['file'])
                            })
                else:
                    # Show methods from selected class only
                    methods = project_data['functions'].get(selected_class, [])
                    for method in methods:
                        all_methods.append({
                            'Class': selected_class,
                            'Method': method['name'],
                            'Return Type': method['return_type'],
                            'Parameters': ', '.join(method['parameters']) if method['parameters'] else 'None',
                            'File': os.path.basename(method['file'])
                        })
                
                # Create and display the methods table
                if all_methods:
                    methods_df = pd.DataFrame(all_methods)
                    st.dataframe(methods_df, use_container_width=True)
                    
                    # Add export options
                    st.markdown("#### Export Function Data")
                    st.markdown(get_csv_download_link(methods_df, f"functions_{selected_class.replace(' ', '_')}.csv", 
                                "💾 Download functions as CSV"), unsafe_allow_html=True)
                    
                    if selected_class == "All Classes":
                        st.markdown(get_json_download_link(project_data['functions'], "all_functions.json", 
                                    "💾 Download all functions as JSON"), unsafe_allow_html=True)
                else:
                    st.info(f"No methods found for {selected_class}.")
            else:
                st.info("No functions were detected or function analysis was not selected.")
        
        # Tab 4: Batch Processes
        with tab4:
            st.header("Batch Processes")
            
            if analyze_batch and 'batch_processes' in project_data and project_data['batch_processes']:
                # Display batch processes in a table
                st.subheader("Detected Batch Processes")
                
                # Create a more structured view of batch processes
                batch_data = []
                for batch in project_data['batch_processes']:
                    batch_info = {
                        'Type': batch.get('type', 'Unknown'),
                        'Class': batch.get('class', 'N/A'),
                        'Method': batch.get('method', 'N/A'),
                        'Details': batch.get('details', ''),
                        'File': os.path.basename(batch.get('file', 'Unknown'))
                    }
                    batch_data.append(batch_info)
                
                # Create and display the batch processes table
                if batch_data:
                    batch_df = pd.DataFrame(batch_data)
                    st.dataframe(batch_df, use_container_width=True)
                    
                    # Add a pie chart showing types of batch processes
                    st.subheader("Batch Process Types")
                    fig = px.pie(batch_df, names='Type', title='Batch Process Types')
                    
                    # Safety check before displaying
                    if fig and isinstance(fig, go.Figure):
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add export options
                        st.markdown("#### Export Batch Process Data")
                        st.markdown(get_csv_download_link(batch_df, "batch_processes.csv", 
                                    "💾 Download batch processes as CSV"), unsafe_allow_html=True)
                        st.markdown(get_json_download_link(project_data['batch_processes'], "batch_processes.json", 
                                    "💾 Download batch processes as JSON"), unsafe_allow_html=True)
                        st.markdown(get_figure_download_link(fig, "batch_process_types.html", 
                                    "💾 Download chart as interactive HTML"), unsafe_allow_html=True)
                    else:
                        st.info("Unable to generate batch process types chart with the current data.")
                        
                        # Still provide data export options even if chart fails
                        st.markdown("#### Export Batch Process Data")
                        st.markdown(get_csv_download_link(batch_df, "batch_processes.csv", 
                                    "💾 Download batch processes as CSV"), unsafe_allow_html=True)
                        st.markdown(get_json_download_link(project_data['batch_processes'], "batch_processes.json", 
                                    "💾 Download batch processes as JSON"), unsafe_allow_html=True)
                else:
                    st.info("No batch processes data available.")
            else:
                st.info("No batch processes were detected or batch analysis was not selected.")
        
        # Tab 5: Project Flow
        with tab5:
            st.header("Project Flow Visualization")
            
            if analyze_flow and 'dependencies' in project_data:
                flow_fig = visualize_flow(project_data['dependencies'])
                
                # Safety check before displaying
                if flow_fig and isinstance(flow_fig, go.Figure):
                    st.plotly_chart(flow_fig, use_container_width=True)
                    
                    # Add export option
                    st.markdown("### Export Options")
                    st.markdown(get_figure_download_link(flow_fig, "project_flow.html", "💾 Download as interactive HTML"), unsafe_allow_html=True)
                else:
                    st.info("Unable to generate project flow visualization with the current data.")
            else:
                st.info("Project flow visualization was not selected or no dependencies were detected.")
        
        # Tab 6: Class Diagram
        with tab6:
            st.header("UML Class Diagram")
            
            if 'functions' in project_data and 'dependencies' in project_data:
                try:
                    # Now returns both the figure and relationship table
                    result = generate_class_diagram(project_data['functions'], project_data['dependencies'])
                    
                    if isinstance(result, tuple) and len(result) == 2:
                        class_diagram, relationship_table = result
                    else:
                        # For backwards compatibility
                        class_diagram = result
                        relationship_table = []
                    
                    # Safety check before displaying
                    if class_diagram and isinstance(class_diagram, go.Figure):
                        st.plotly_chart(class_diagram, use_container_width=True)
                        
                        # Add export option
                        st.markdown("### Export Options")
                        st.markdown(get_figure_download_link(class_diagram, "class_diagram.html", "💾 Download as interactive HTML"), unsafe_allow_html=True)
                        
                        # Display class relationships table
                        if relationship_table:
                            st.subheader("Class Relationships")
                            
                            # Create a markdown table header
                            table_md = """
                            | Source Class | Relationship Type | Target Class | Description |
                            |-------------|-------------------|--------------|-------------|
                            """
                            
                            # Add each relationship row
                            for row in relationship_table:
                                table_md += row + "\n"
                            
                            st.markdown(table_md)
                            
                            # Also offer CSV export for the relationships
                            if len(relationship_table) > 0:
                                # Convert to DataFrame for CSV export
                                rel_data = []
                                for row in relationship_table:
                                    parts = row.split("|")
                                    if len(parts) >= 5:  # Should have 5 parts with empty first/last
                                        rel_data.append({
                                            "Source": parts[1].strip(),
                                            "Relationship": parts[2].strip(),
                                            "Target": parts[3].strip(),
                                            "Description": parts[4].strip()
                                        })
                                
                                if rel_data:
                                    rel_df = pd.DataFrame(rel_data)
                                    st.markdown(get_csv_download_link(rel_df, "class_relationships.csv", 
                                                "💾 Download relationships as CSV"), unsafe_allow_html=True)
                    else:
                        st.info("Unable to generate class diagram with the current data.")
                except Exception as e:
                    st.error(f"Error generating class diagram: {str(e)}")
                    st.info("Unable to generate class diagram due to an error in processing the data.")
            else:
                st.info("Insufficient data to generate class diagram. Ensure both functions and dependencies are available.")
        
        # Tab 7: Sequence Diagram
        with tab7:
            st.header("Sequence Diagram")
            
            if 'apis' in project_data and 'functions' in project_data:
                sequence_diagram = generate_sequence_diagram(project_data['apis'], project_data['functions'])
                
                # Safety check before displaying
                if sequence_diagram and isinstance(sequence_diagram, go.Figure):
                    st.plotly_chart(sequence_diagram, use_container_width=True)
                    
                    # Add export option
                    st.markdown("### Export Options")
                    st.markdown(get_figure_download_link(sequence_diagram, "sequence_diagram.html", "💾 Download as interactive HTML"), unsafe_allow_html=True)
                else:
                    st.info("Unable to generate sequence diagram with the current data.")
            else:
                st.info("Insufficient data to generate sequence diagram. Ensure APIs and functions are available.")
        
        # Tab 8: Functional Flow
        with tab8:
            st.header("Functional Flow Diagram")
            
            if 'apis' in project_data and 'functions' in project_data and 'batch_processes' in project_data:
                functional_flow = generate_functional_flow(
                    project_data.get('apis', []), 
                    project_data.get('functions', {}), 
                    project_data.get('batch_processes', [])
                )
                # Safety check before displaying
                if functional_flow and isinstance(functional_flow, go.Figure):
                    st.plotly_chart(functional_flow, use_container_width=True)
                else:
                    st.info("Unable to generate functional flow diagram with the current data.")
                
                # Add export option only if we have a valid figure
                if functional_flow and isinstance(functional_flow, go.Figure):
                    st.markdown("### Export Options")
                    st.markdown(get_figure_download_link(functional_flow, "functional_flow.html", "💾 Download as interactive HTML"), unsafe_allow_html=True)
            else:
                st.info("Insufficient data to generate functional flow diagram.")
        
        # Progress is complete
        progress_bar.progress(100)
        status_text.text("Analysis completed!")
        
else:
    # Display sample dashboard with instructions when no file is uploaded
    st.info("Please upload a ZIP file containing your Java J2EE project to start the analysis.")
    
    # Display explanation of features
    st.header("Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Project Structure Analysis")
        st.markdown("- Visualize directory structure")
        st.markdown("- Count files by type")
        st.markdown("- Identify key project components")
        
        st.subheader("API Analysis")
        st.markdown("- Detect REST endpoints")
        st.markdown("- Identify API methods (GET, POST, etc.)")
        st.markdown("- Map API relationships")
    
    with col2:
        st.subheader("Function Analysis")
        st.markdown("- List classes and methods")
        st.markdown("- Show method signatures")
        st.markdown("- Display return types and parameters")
        
        st.subheader("Batch Process Detection")
        st.markdown("- Identify scheduled jobs")
        st.markdown("- Detect batch processing classes")
        st.markdown("- Map data flow in batch operations")

# Add footer with Zensar Diamond Team branding
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 10px; margin-top: 30px;">
        <p style="color: #666; font-size: 0.9em;">
            © 2025 JLens - Developed by Zensar Diamond Team
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
