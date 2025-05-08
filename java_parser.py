import os
import re
import javalang
import pandas as pd
from collections import defaultdict, Counter

class JavaProjectParser:
    """
    Class for parsing Java J2EE projects and extracting relevant information.
    """
    
    def __init__(self, project_path):
        self.project_path = project_path
        self.java_files = []
        self.parsed_files = {}
        self.apis = []
        self.functions = defaultdict(list)
        self.batch_processes = []
        self.dependencies = {}
        self.structure = {"name": os.path.basename(project_path), "children": []}
        self.file_types_count = Counter()
        
    def parse_project(self):
        """
        Parse the Java project and extract all relevant information.
        """
        # Collect all Java files in the project
        self._collect_java_files()
        
        # Parse each Java file
        for java_file in self.java_files:
            self._parse_java_file(java_file)
        
        # Analyze project dependencies
        self._analyze_dependencies()
        
        # Analyze project structure
        self._analyze_project_structure()
        
        # Generate file type statistics
        self._count_file_types()
        
        # Count total lines of code
        total_lines = 0
        for file_path in self.java_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except Exception:
                pass  # Skip files that can't be read
        
        # Extract unique libraries used
        libraries_used = set()
        for file_path in self.java_files:
            if file_path.endswith("pom.xml"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Simple regex to extract artifact IDs from pom.xml
                        import re
                        artifacts = re.findall(r'<artifactId>(.*?)</artifactId>', content)
                        for artifact in artifacts:
                            if artifact and not artifact.startswith('${'):
                                libraries_used.add(artifact)
                except Exception:
                    pass
            elif file_path.endswith("build.gradle"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Simple regex to extract dependencies from build.gradle
                        import re
                        deps = re.findall(r'implementation [\'"]([^:]+:[^:]+:[^\'"]+)[\'"]', content)
                        deps.extend(re.findall(r'compile [\'"]([^:]+:[^:]+:[^\'"]+)[\'"]', content))
                        for dep in deps:
                            libraries_used.add(dep)
                except Exception:
                    pass
        
        # Count total number of classes
        total_classes = len(self.functions.keys())
        
        # Count total number of files by extension
        file_extensions = {}
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext:
                    if ext not in file_extensions:
                        file_extensions[ext] = 0
                    file_extensions[ext] += 1
        
        # Collect project summary
        project_summary = {
            "total_files": sum(file_extensions.values()),
            "java_files": len(self.java_files),
            "total_classes": total_classes,
            "total_lines": total_lines,
            "batch_jobs": len(self.batch_processes),
            "apis_count": len(self.apis),
            "libraries_used": list(libraries_used)
        }
        
        # Collect results
        return {
            "structure": self.structure,
            "apis": self.apis,
            "functions": self.functions,
            "batch_processes": self.batch_processes,
            "dependencies": self.dependencies,
            "java_files": [os.path.relpath(f, self.project_path) for f in self.java_files],
            "file_types_count": self.file_types_count,
            "project_summary": project_summary
        }
        
    def _collect_java_files(self):
        """
        Find all Java files in the project directory.
        """
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden directories and files
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'target' and d != 'build']
            
            for file in files:
                if file.endswith('.java'):
                    self.java_files.append(os.path.join(root, file))
    
    def _parse_java_file(self, file_path):
        """
        Parse a single Java file and extract relevant information.
        """
        relative_path = os.path.relpath(file_path, self.project_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse Java code
            tree = javalang.parse.parse(content)
            self.parsed_files[relative_path] = tree
            
            # Check for API endpoints (REST annotations)
            self._extract_apis(tree, relative_path)
            
            # Extract functions and methods
            self._extract_functions(tree, relative_path)
            
            # Check for batch processes
            self._extract_batch_processes(tree, relative_path, content)
                
        except Exception as e:
            print(f"Error parsing {relative_path}: {str(e)}")
            # Continue with other files even if one fails
            pass
    
    def _extract_apis(self, tree, file_path):
        """
        Extract API endpoints from a parsed Java file.
        """
        # Check for classes with REST annotations
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            class_annotations = []
            
            # Check class annotations
            if hasattr(node, 'annotations') and node.annotations:
                class_annotations = [a.name for a in node.annotations]
            
            # Check if class has REST-related annotations
            is_rest_controller = any(a in ['RestController', 'Controller', 'Path', 'WebServlet'] for a in class_annotations)
            class_path = ""
            
            # Extract class-level path if available
            for annotation in node.annotations:
                if annotation.name in ['RequestMapping', 'Path']:
                    if annotation.element and annotation.element.value:
                        # Extract path value from annotation
                        class_path = self._extract_annotation_value(annotation)
            
            # Look for methods with REST annotations
            if hasattr(node, 'methods'):
                for method in node.methods:
                    method_annotations = []
                    
                    # Get method annotations
                    if hasattr(method, 'annotations') and method.annotations:
                        method_annotations = [a.name for a in method.annotations]
                    
                    # Check for REST method annotations
                    rest_methods = ['GetMapping', 'PostMapping', 'PutMapping', 'DeleteMapping', 
                                   'RequestMapping', 'GET', 'POST', 'PUT', 'DELETE']
                    
                    is_api_method = any(a in rest_methods for a in method_annotations) or is_rest_controller
                    
                    if is_api_method:
                        # Determine HTTP method and path
                        http_method = "GET"  # Default
                        method_path = ""
                        
                        for annotation in method.annotations:
                            annotation_name = annotation.name
                            
                            if annotation_name == 'RequestMapping':
                                # Extract method and path from RequestMapping
                                if annotation.element:
                                    for elem in annotation.element:
                                        if elem.name == 'method':
                                            http_method = self._extract_annotation_value(elem)
                                        elif elem.name == 'value' or elem.name == 'path':
                                            method_path = self._extract_annotation_value(elem)
                            elif annotation_name == 'GetMapping':
                                http_method = 'GET'
                                method_path = self._extract_annotation_value(annotation)
                            elif annotation_name == 'PostMapping':
                                http_method = 'POST'
                                method_path = self._extract_annotation_value(annotation)
                            elif annotation_name == 'PutMapping':
                                http_method = 'PUT'
                                method_path = self._extract_annotation_value(annotation)
                            elif annotation_name == 'DeleteMapping':
                                http_method = 'DELETE'
                                method_path = self._extract_annotation_value(annotation)
                            elif annotation_name in ['GET', 'POST', 'PUT', 'DELETE']:
                                http_method = annotation_name
                            elif annotation_name == 'Path':
                                method_path = self._extract_annotation_value(annotation)
                        
                        # Combine class path and method path
                        full_path = class_path + method_path if method_path else class_path
                        
                        # Add API endpoint to the list
                        self.apis.append({
                            'class': class_name,
                            'method': method.name,
                            'http_method': http_method,
                            'path': full_path,
                            'file': file_path
                        })
    
    def _extract_annotation_value(self, annotation):
        """
        Extract value from a Java annotation.
        """
        if hasattr(annotation, 'element') and annotation.element:
            if isinstance(annotation.element, list):
                for elem in annotation.element:
                    if hasattr(elem, 'value') and elem.value:
                        return elem.value.strip('"')
            elif hasattr(annotation.element, 'value') and annotation.element.value:
                return annotation.element.value.strip('"')
        return ""
    
    def _extract_functions(self, tree, file_path):
        """
        Extract classes and methods from a parsed Java file.
        """
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            
            if hasattr(node, 'methods'):
                for method in node.methods:
                    # Skip private methods
                    if method.modifiers and 'private' in method.modifiers:
                        continue
                    
                    # Get method parameters
                    parameters = []
                    if method.parameters:
                        for param in method.parameters:
                            param_type = param.type.name if hasattr(param.type, 'name') else str(param.type)
                            parameters.append(f"{param_type} {param.name}")
                    
                    # Get return type
                    return_type = "void"
                    if hasattr(method, 'return_type') and method.return_type:
                        if hasattr(method.return_type, 'name'):
                            return_type = method.return_type.name
                        else:
                            return_type = str(method.return_type)
                    
                    # Add method to the functions list
                    self.functions[class_name].append({
                        'name': method.name,
                        'return_type': return_type,
                        'parameters': parameters,
                        'file': file_path
                    })
    
    def _extract_batch_processes(self, tree, file_path, content):
        """
        Extract batch processing related information from a Java file.
        """
        # Check for batch process related annotations or class names
        batch_annotations = ['Scheduled', 'Schedule', 'Quartz', 'BatchJob', 'Job']
        batch_class_patterns = [
            'BatchJob', 'Job', 'Processor', 'Reader', 'Writer', 'TaskExecutor', 
            'Scheduler', 'QuartzJob'
        ]
        
        is_batch_process = False
        batch_details = {
            'file': file_path,
            'type': 'Unknown',
            'details': ''
        }
        
        # Check class annotations and names
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            
            # Check if class name suggests a batch process
            if any(pattern in class_name for pattern in batch_class_patterns):
                is_batch_process = True
                batch_details['class'] = class_name
                batch_details['type'] = 'Batch Class'
            
            # Check annotations for batch-related annotations
            if hasattr(node, 'annotations') and node.annotations:
                for annotation in node.annotations:
                    if annotation.name in batch_annotations:
                        is_batch_process = True
                        batch_details['class'] = class_name
                        batch_details['type'] = f'Batch Class ({annotation.name})'
                        if annotation.element:
                            batch_details['details'] = self._extract_annotation_value(annotation)
            
            # Check methods for @Scheduled annotations
            if hasattr(node, 'methods'):
                for method in node.methods:
                    if hasattr(method, 'annotations') and method.annotations:
                        for annotation in method.annotations:
                            if annotation.name in batch_annotations:
                                is_batch_process = True
                                batch_details['class'] = class_name
                                batch_details['method'] = method.name
                                batch_details['type'] = f'Scheduled Method ({annotation.name})'
                                if annotation.element:
                                    batch_details['details'] = self._extract_annotation_value(annotation)
        
        # Check for Spring Batch XML configuration
        if '<job' in content or '<step' in content or '<tasklet' in content:
            is_batch_process = True
            batch_details['type'] = 'Spring Batch XML Configuration'
            
            # Extract job id if available
            job_match = re.search(r'<job[^>]*id=[\'"](.*?)[\'"]', content)
            if job_match:
                batch_details['details'] = f"Job ID: {job_match.group(1)}"
        
        # Add to batch processes if found
        if is_batch_process:
            self.batch_processes.append(batch_details)
    
    def _analyze_dependencies(self):
        """
        Analyze dependencies between classes.
        """
        for file_path, tree in self.parsed_files.items():
            # Extract the package name
            package_name = ""
            if hasattr(tree, 'package') and tree.package:
                package_name = tree.package.name
            
            # Extract imported packages
            imports = []
            if hasattr(tree, 'imports'):
                for import_decl in tree.imports:
                    imports.append(import_decl.path)
            
            # Find classes in this file
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_name = node.name
                fully_qualified_name = f"{package_name}.{class_name}" if package_name else class_name
                
                # Create a node for this class
                if fully_qualified_name not in self.dependencies:
                    self.dependencies[fully_qualified_name] = {
                        'file': file_path,
                        'package': package_name,
                        'imports': imports,
                        'uses': []
                    }
                
                # Check field types and method return types for dependencies
                for path, field in tree.filter(javalang.tree.FieldDeclaration):
                    for var_decl in field.declarators:
                        field_type = field.type.name if hasattr(field.type, 'name') else str(field.type)
                        # Check if field type is one of our classes
                        for imp in imports:
                            if imp.endswith(f".{field_type}"):
                                self.dependencies[fully_qualified_name]['uses'].append(imp)
                
                # Add interfaces as dependencies
                if node.implements:
                    for interface in node.implements:
                        interface_name = interface.name if hasattr(interface, 'name') else str(interface)
                        for imp in imports:
                            if imp.endswith(f".{interface_name}"):
                                self.dependencies[fully_qualified_name]['uses'].append(imp)
                
                # Add superclass as dependency
                if node.extends:
                    extends_name = node.extends.name if hasattr(node.extends, 'name') else str(node.extends)
                    for imp in imports:
                        if imp.endswith(f".{extends_name}"):
                            self.dependencies[fully_qualified_name]['uses'].append(imp)
    
    def _analyze_project_structure(self):
        """
        Create a hierarchical representation of the project structure.
        """
        # Create a recursive function to build the structure
        def build_structure(path, structure):
            relative_path = os.path.relpath(path, self.project_path)
            name = os.path.basename(path)
            
            if os.path.isfile(path):
                # Skip non-Java files for simplicity
                if not path.endswith('.java'):
                    return None
                return {"name": name, "path": relative_path, "type": "file"}
            else:
                children = []
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    # Skip hidden files and build directories
                    if item.startswith('.') or item in ['target', 'build', 'bin', 'out']:
                        continue
                    
                    child = build_structure(item_path, structure)
                    if child:
                        children.append(child)
                
                if children:
                    return {"name": name, "path": relative_path, "children": children, "type": "directory"}
                else:
                    return None
        
        # Build the structure starting from the project root
        self.structure = build_structure(self.project_path, self.structure)
        if not self.structure:
            self.structure = {"name": os.path.basename(self.project_path), "children": [], "type": "directory"}
    
    def _count_file_types(self):
        """
        Count files by their extension.
        """
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden directories and files
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'target' and d != 'build']
            
            for file in files:
                _, ext = os.path.splitext(file)
                if ext:
                    # Remove the dot from extension
                    ext = ext[1:]
                    self.file_types_count[ext] += 1
        
        # Convert to DataFrame for easy visualization
        self.file_types_count = pd.Series(self.file_types_count).sort_values(ascending=False)
