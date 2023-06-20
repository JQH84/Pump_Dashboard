# ESP Data Visualization Dashboard

This Streamlit app visualizes ESP (Electric Submersible Pump) data from multiple files in a folder and displays it in a dashboard. It provides various visualizations and interactive features for analyzing pump operating data.

## How to Use

1. Install the required dependencies by running `pip install -r requirements.txt`.
2. Place the ESP data files in a folder.
3. Run the Streamlit app by executing the command `streamlit run app.py`.
4. Upload the input CSV files using the file uploader in the sidebar.
5. Select a well from the dropdown menu to visualize data specific to that well.
6. Choose the columns to plot against time.
7. Explore the provided visualizations, including gauge charts, scatter plots, line plots, bar charts, and a geographical map.

## Dependencies

The app requires the following dependencies:
- streamlit
- pandas
- numpy
- matplotlib
- seaborn
- plotly
- plotly.io
- plotly.express
- plotly.graph_objects
- plotly.figure_factory

You can install these dependencies by running `pip install -r requirements.txt`.

## File Structure

- `app.py`: The main Streamlit application file.
- `DP_BlueLogo.png`: The logo image displayed in the sidebar.
- `README.md`: The readme file with instructions and information about the app.

## Credits

This app is developed by [Your Name] and is based on Streamlit, a Python library for building interactive web applications for data science and machine learning.

## License

[Specify the license for your app]

