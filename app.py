import streamlit as st
import os
import tempfile
import zipfile
import shutil
import pandas as pd
from java_parser import JavaProjectParser
from visualizer import visualize_project_structure, visualize_api_calls, visualize_flow
from utils import create_data_tables, get_file_content

# Set page configuration
st.set_page_config(
    page_title="Jlens - Java J2EE Project Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# App title and description
st.title("🔍 Jlens")
st.subheader("Java J2EE Project Scanner")
st.markdown("""
    Upload your Java J2EE project (ZIP file) to analyze its structure, APIs, functions, and batch processes.
    Jlens will provide visualizations and insights into your project's architecture.
""")

# Sidebar for file upload and options
with st.sidebar:
    st.header("Upload Project")
    uploaded_file = st.file_uploader("Choose a ZIP file containing your Java J2EE project", type=["zip"])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        # Analysis options
        st.header("Analysis Options")
        analyze_apis = st.checkbox("Analyze APIs", value=True)
        analyze_functions = st.checkbox("Analyze Functions", value=True)
        analyze_batch = st.checkbox("Analyze Batch Processes", value=True)
        analyze_flow = st.checkbox("Visualize Project Flow", value=True)

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
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Project Structure", 
            "APIs", 
            "Functions", 
            "Batch Processes",
            "Project Flow"
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
                st.plotly_chart(structure_fig, use_container_width=True)
                
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
                
                # Visualize API relationships
                st.subheader("API Relationships")
                api_fig = visualize_api_calls(project_data['apis'])
                st.plotly_chart(api_fig, use_container_width=True)
            else:
                st.info("No APIs were detected or API analysis was not selected.")
        
        # Tab 3: Functions
        with tab3:
            st.header("Functions/Methods")
            
            if analyze_functions and 'functions' in project_data and project_data['functions']:
                # Create an expandable section for each class
                classes = project_data['functions'].keys()
                for class_name in classes:
                    with st.expander(f"Class: {class_name}"):
                        methods = project_data['functions'][class_name]
                        if methods:
                            for method in methods:
                                st.markdown(f"**Method:** `{method['name']}`")
                                st.markdown(f"**Return Type:** `{method['return_type']}`")
                                st.markdown(f"**Parameters:** {', '.join([f'`{p}`' for p in method['parameters']])}")
                                st.markdown(f"**File:** {method['file']}")
                                st.markdown("---")
                        else:
                            st.info("No methods found in this class.")
            else:
                st.info("No functions were detected or function analysis was not selected.")
        
        # Tab 4: Batch Processes
        with tab4:
            st.header("Batch Processes")
            
            if analyze_batch and 'batch_processes' in project_data and project_data['batch_processes']:
                # Display batch processes
                st.subheader("Detected Batch Processes")
                batch_df = create_data_tables(project_data['batch_processes'])
                st.dataframe(batch_df, use_container_width=True)
            else:
                st.info("No batch processes were detected or batch analysis was not selected.")
        
        # Tab 5: Project Flow
        with tab5:
            st.header("Project Flow Visualization")
            
            if analyze_flow and 'dependencies' in project_data:
                flow_fig = visualize_flow(project_data['dependencies'])
                st.plotly_chart(flow_fig, use_container_width=True)
            else:
                st.info("Project flow visualization was not selected or no dependencies were detected.")
        
        # Progress is complete
        # File Explorer section has been removed as per user request
        
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
