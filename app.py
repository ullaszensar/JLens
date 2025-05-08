import streamlit as st
import os
import tempfile
import zipfile
import shutil
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
            
            # Display project structure as a tree
            structure_fig = visualize_project_structure(project_data['structure'])
            st.plotly_chart(structure_fig, use_container_width=True)
            
            # Display files count by type
            st.subheader("Files Distribution")
            files_by_type = project_data['file_types_count']
            st.bar_chart(files_by_type)
        
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
        
        # File Explorer section
        st.header("File Explorer")
        
        # Create a list of all Java files for selection
        if 'java_files' in project_data:
            java_files = project_data['java_files']
            selected_file = st.selectbox("Select a file to view its content:", java_files)
            
            if selected_file:
                file_path = os.path.join(extract_dir, selected_file)
                
                # Display file content with syntax highlighting
                st.subheader(f"Content of {selected_file}")
                content = get_file_content(file_path)
                st.code(content, language="java")
        
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
