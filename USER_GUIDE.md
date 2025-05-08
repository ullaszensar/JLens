# JLens User Guide

Welcome to JLens, the comprehensive Java J2EE project analyzer. This guide will help you navigate and use the application effectively.

## Getting Started

### Uploading a Project

1. Start the JLens application
2. On the home page, use the file uploader to select a ZIP file containing your Java J2EE project
3. Check the analysis options you want to perform (Structure, APIs, Functions, Batch Processes)
4. Click "Analyze Project" to begin the analysis

### Navigation

JLens organizes analysis results into separate tabs:

- **Project Structure**: Shows the organization and hierarchy of your project
- **APIs**: Displays detected REST endpoints and API relationships
- **Functions**: Shows class structures, methods, and relationships
- **Batch Processes**: Displays scheduled jobs and batch processes
- **Sequence Diagram**: Shows the sequence of operations in your application
- **Functional Flow**: Maps the business logic flow across components

## Understanding the Results

### Project Structure Tab

This tab shows:

- A hierarchical tree view of your project directories
- Visualization of the project structure using a network graph
- File type counts and distribution
- MVC components identified in the project

**Tips**:
- Hover over nodes in the graph to see details
- Use the zoom controls to explore complex structures
- Use the export buttons to save data for further analysis

### APIs Tab

This tab shows:

- A table of REST endpoints found in the project
- HTTP methods (GET, POST, PUT, DELETE, etc.)
- Path parameters and request mappings
- API visualization showing relationships between endpoints

**Tips**:
- Use filters to focus on specific API types or controllers
- Look for API naming patterns to understand the application's design
- Check for versioning and consistent URL patterns

### Functions Tab

This tab shows:

- Class structure with attributes and methods
- Class relationships (inheritance, composition, etc.)
- Detailed method signatures
- Class types (Controller, Service, Entity, etc.)

**Tips**:
- Use the class selector to focus on specific classes
- Check relationship types to understand dependencies
- Look for design patterns in the class structure
- Export method data for documentation

### Batch Processes Tab

This tab shows:

- Scheduled jobs and batch processing components
- Execution schedules and triggers
- Batch process types and relationships
- Chart showing the distribution of batch process types

**Tips**:
- Look for cron expressions to understand scheduling
- Check for transaction management in batch jobs
- Identify data processing patterns

### Sequence Diagram Tab

This tab shows:

- The flow of operations between components
- Request-response patterns
- Service interactions
- Exception handling flow

**Tips**:
- Follow the arrows to understand the execution flow
- Look for potential bottlenecks in complex sequences
- Identify synchronous vs. asynchronous patterns

### Functional Flow Tab

This tab shows:

- Business function flow across components
- Data transformation and processing steps
- Integration points between services
- End-to-end process visualization

**Tips**:
- Use this view to understand the overall application logic
- Identify core business functions and their implementations
- Trace how data flows through the system

## Advanced Features

### Data Export

JLens allows you to export analysis results in various formats:

- **CSV**: For tabular data like APIs, methods, and relationships
- **JSON**: For structured data with full details
- **HTML**: For interactive visualizations that can be viewed offline

To export data, look for the download links below each visualization or table.

### Class Structure Analysis

To get the most from the class structure analysis:

1. Use the Class Structure section to view attributes and methods
2. Check Class Relationships to understand dependencies
3. Look at the Methods List for detailed signatures
4. Export data for documentation or further analysis

### Understanding Relationships

JLens identifies several types of relationships between classes:

- **Association**: One class uses another class
- **Aggregation**: One class has a reference to another class ("has-a" relationship)
- **Composition**: One class owns another class (stronger "has-a" relationship)
- **Inheritance**: One class extends another class ("is-a" relationship)
- **Implementation**: One class implements an interface

These relationships help you understand the design patterns and architecture of the project.

## Tips for Large Projects

- **Be Selective**: For very large projects, select only the analysis options you need
- **Focus on Core Components**: Use the class selector to focus on important classes
- **Export Data**: Use the export options to analyze data offline
- **Look for Patterns**: Focus on identifying patterns rather than individual details
- **Follow Relationships**: Use relationships to navigate complex structures

## Troubleshooting

- **Analysis Errors**: Some complex Java files may not parse correctly; check the logs for details
- **Visualization Issues**: If graphs don't render properly, try refreshing the page
- **Missing Data**: If expected data is missing, ensure the project follows standard J2EE conventions
- **Performance Issues**: For large projects, be patient as analysis may take some time

## Example Workflow

Here's a typical workflow for analyzing a project with JLens:

1. Upload the project and select all analysis options
2. Start with Project Structure to understand the overall organization
3. Look at APIs to understand the application's endpoints
4. Examine Functions to see class relationships and implementation details
5. Check Batch Processes if the application has scheduling components
6. Use Sequence and Functional Flow diagrams to understand the runtime behavior

## Getting Help

If you encounter any issues or have questions about JLens, please refer to:

- The README.md file for installation and basic information
- The DEPLOYMENT.md file for deployment options
- Open issues on the project's GitHub repository

---

© 2025 JLens - Zensar Diamond Team