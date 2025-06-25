# Data Visualization Dashboard

A powerful tool for visualizing and analyzing data with various chart types and customization options.

## Features

- Load data from CSV, Excel, and JSON files
- Create various types of visualizations:
  - Bar charts
  - Line charts
  - Scatter plots
  - Histograms
  - Box plots
  - Heatmaps
  - Pie charts
- Customize plot appearance (colors, titles, labels, etc.)
- Save and export visualizations
- Track recently opened files

## Installation

### Required Dependencies

The dashboard requires the following Python packages:
- pandas
- numpy
- matplotlib
- scipy

For enhanced visualizations (optional):
- seaborn

### Setup Instructions

1. Create a virtual environment (recommended):
   ```
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On Linux/Mac:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

3. Install the minimal dependencies:
   ```
   pip install -r requirements_dashboard_minimal.txt
   ```

4. For enhanced visualizations (optional):
   ```
   pip install seaborn
   ```

## Running the Application

After installing the dependencies, run the application with:

```
python 18_data_visualization_dashboard.py
```

## Usage

1. Open a data file (CSV, Excel, or JSON) from the File menu or the Open button
2. Select columns for X and Y axes from the dropdown menus
3. Choose a plot type from the dropdown or Visualizations menu
4. Click "Generate Plot" to create the visualization
5. Adjust plot settings from the Settings menu
6. Save or export your visualization using the buttons below the plot

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed correctly
2. Check that your data file is properly formatted
3. For large datasets, try using a smaller subset of the data

## Additional Information

The dashboard automatically saves your settings and recent files between sessions. These are stored in a `dashboard_settings.json` file in the same directory as the application. 