import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import altair as alt  # type: ignore
import plotly.express as px  # type: ignore
import os
from datetime import datetime

# Set the page configuration with a custom favicon
st.set_page_config(
    page_title="VRIAS TEST Dashboard",
    page_icon="favicon.ico", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enable Altair dark theme
alt.themes.enable("dark")

# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}
[st.write] {
    text-align: center        }

/* Neon effect */
.neon-text {
    color: #fff;
    text-shadow:
        0 0 7px #fff,
        0 0 10px #fff,
        0 0 21px #fff,
        0 0 42px #0fa,
        0 0 82px #0fa,
        0 0 92px #0fa,
        0 0 102px #0fa,
        0 0 151px #0fa;
}

/* Auto-scroll effect */
.route-display {
    white-space: nowrap;
    overflow: hidden;
    position: relative;
    width: 100%;
    height: 30px;
    background-color: #000;
    border: 1px solid #0fa;
    box-shadow: 0 0 10px #0fa;
}

.route-display span {
    position: absolute;
    width: 100%;
    height: 100%;
    margin: 0;
    line-height: 25px;
    text-align: center;
    transform: translateX(100%);
    animation: scroll-left 20s linear infinite;
}

@keyframes scroll-left {
    0% {
        transform: translateX(100%);
    }
    100% {
        transform: translateX(-100%);
    }
}

/* Magnification effect */
.magnified {
    transform: scale(1.2);
    transition: transform 0.3s ease-in-out;
}

/* Neon window styling */
.neon-window {
    background-color: #000;
    border: 1px solid;
    box-shadow: 0 0 10px;
    padding: 10px;
    text-align: center;
}

.neon-window.green {
    border-color: #27AE60;
    box-shadow: 0 0 10px #27AE60;
}

.neon-window.blue {
    border-color: #29b5e8;
    box-shadow: 0 0 10px #29b5e8;
}

.neon-window.orange {
    border-color: #F39C12;
    box-shadow: 0 0 10px #F39C12;
}

.neon-window.red {
    border-color: #E74C3C;
    box-shadow: 0 0 10px #E74C3C;
}

</style>
""", unsafe_allow_html=True)

# Function to scan the data folder for route folders
def scan_data_folder(folder_path):
    route_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    return route_folders

# Function to extract route name and date from folder name
def extract_info(foldername):
    parts = foldername.split('-')
    route_name = '-'.join(parts[:3])  # Extract "NAIROBI-WESTLANDS-A05"
    date_str = '-'.join(parts[3:6])  # Extract "21-11-23"
    date = datetime.strptime(date_str, '%d-%m-%y').date()
    route_codes = parts[6:]  # Extract additional route codes
    return route_name, date, route_codes

# Function to count occurrences of 'Potholes' and 'Cracks/Other Defects'
def count_defects(df):
    potholes_count = df[df['Class Name'] == 'pothole'].shape[0]
    cracks_other_defects_count = df[df['Class Name'] == 'crack-other-defect'].shape[0]
    return potholes_count, cracks_other_defects_count

# Function to determine the road condition grade
def determine_grade(potholes_count):
    if potholes_count < 5:
        return 'A'
    elif potholes_count < 20:
        return 'B'
    elif potholes_count < 40:
        return 'C'
    elif potholes_count < 60:
        return 'D'
    else:
        return 'E'

# Function to create the donut chart
def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
    
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text

# Function to upgrade 'crack-other-defect' to 'pothole' if three or more detections share the same 'seconds' field
def upgrade_defects(df):
    df['Seconds'] = df['Timestamp (seconds)'].apply(lambda x: int(x))
    grouped = df.groupby(['Seconds', 'Class Name']).size().unstack(fill_value=0)
    for seconds, counts in grouped.iterrows():
        if counts['crack-other-defect'] >= 4:
            df.loc[(df['Seconds'] == seconds) & (df['Class Name'] == 'crack-other-defect'), 'Class Name'] = 'pothole'
    df.drop(columns=['Seconds'], inplace=True)
    return df

# Path to the data folder
data_folder = 'data'  # Replace with the actual path

# Scan the data folder for route folders
route_folders = scan_data_folder(data_folder)

# Extract route names, dates, and route codes
routes_dates_codes = {extract_info(foldername)[0]: [] for foldername in route_folders}
for foldername in route_folders:
    route_name, date, route_codes = extract_info(foldername)
    routes_dates_codes[route_name].append((date, route_codes))

# Create a list of unique route names
route_names = list(routes_dates_codes.keys())

# Sidebar configuration
with st.sidebar:
     # Display the custom resized image
    st.image("icon.png", width=100)  # Replace with the actual path to your image
    
    # Add the title below the image
    st.title('VRIAS Results Dashboard')
    
    # Dropdown for selecting the route
    selected_route = st.selectbox(
        '🌍 Select Route',  # Add location icon
        route_names,
        index=0
    )
    
    # Dropdown for selecting the date
    selected_date = st.selectbox(
        '📅 Select Date',  # Add calendar icon
        sorted([date for date, _ in routes_dates_codes[selected_route]], reverse=True),
        index=0
    )

# Filter the data based on selected route and date
selected_folders = [f for f in route_folders if extract_info(f)[0] == selected_route and extract_info(f)[1] == selected_date]

# Load and display the selected CSV file
if selected_folders:
    selected_folder = selected_folders[0]
    csv_file = os.path.join(data_folder, selected_folder, f"{selected_folder}.csv")
    df = pd.read_csv(csv_file)

    # Upgrade 'crack-other-defect' to 'pothole' if three or more detections share the same 'seconds' field
    df = upgrade_defects(df)

    # Display the route display at the top
    potholes_count, cracks_other_defects_count = count_defects(df)
    route_display_text = f"VRIAS - {selected_route} - Potholes: {potholes_count} - Cracks/Other Defects: {cracks_other_defects_count}"
    st.markdown(f"""
        <div class="route-display">
            <span class="neon-text">{route_display_text}</span>
        </div>
    """, unsafe_allow_html=True)

    # Determine the road condition grade
    grade = determine_grade(potholes_count)
    if grade == 'A':
        neon_color = 'green'
    elif grade == 'B':
        neon_color = 'blue'
    elif grade == 'C':
        neon_color = 'orange'
    else:
        neon_color = 'red'

    # Define the columns layout
    col1, col2, col3 = st.columns((1.5, 4.5, 3.5), gap='medium')
    
    # Display counts in the first column
    with col1:
        st.metric("Potholes", potholes_count)
        st.metric("Cracks/Other Defects", cracks_other_defects_count)

        # Display the donut chart
        st.write("### Health")
        if grade == 'A':
            donut_chart = make_donut(100, grade, 'green')
        elif grade == 'B':
            donut_chart = make_donut(80, grade, 'blue')
        elif grade == 'C':
            donut_chart = make_donut(60, grade, 'orange')
        elif grade == 'D':
            donut_chart = make_donut(40, grade, 'red')
        else:
            donut_chart = make_donut(20, grade, 'red')
        
        st.altair_chart(donut_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display the map in the second column
    with col2:
        
        # Create a map with Plotly Express
        fig = px.scatter_mapbox(
            df,
            lat="Latitude",
            lon="Longitude",
            color="Class Name",
            color_discrete_map={
                "pothole": "red",
                "crack-other-defect": "orange"
            },
            zoom=10,
            height=500,
            custom_data=['Timestamp (seconds)']  # Use the correct column name
        )
        
        # Update the layout for better visualization
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(0,0,0,0.5)",
                font=dict(color="white")
            )
        )
        
        # Highlight routes with different shades
        for route_code in extract_info(selected_folder)[2]:
            fig.add_trace(
                px.line_mapbox(
                    df[df['Route Code'] == route_code],
                    lat="Latitude",
                    lon="Longitude",
                    color_discrete_sequence=["fuchsia"]  # Change color as needed
                ).data[0]
            )
        
        # Display the map
        map_placeholder = st.empty()
        map_placeholder.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display the video and images in the third column
    with col3:

        # Display images based on map clicks
        image_folder = os.path.join(data_folder, selected_folder, 'pictures')
        if os.path.exists(image_folder):
            images = [f for f in os.listdir(image_folder) if f.endswith('.png')]
            image_timestamps = [float(img.replace('.png', '')) for img in images]
            image_paths = [os.path.join(image_folder, img) for img in images]
            
            # Sort images based on timestamps
            sorted_images = [img for _, img in sorted(zip(image_timestamps, images))]
            sorted_image_paths = [os.path.join(image_folder, img) for img in sorted_images]
            
            # Filter images to display only one instance per minute
            filtered_images = []
            seen_minutes = set()
            for img, timestamp in zip(sorted_images, image_timestamps):
                minute = int(timestamp)
                if minute not in seen_minutes:
                    filtered_images.append(img)
                    seen_minutes.add(minute)
            
            # Create a dictionary to map indexes to image paths
            index_to_image = dict(enumerate(sorted_image_paths))
            
            # Display the first image by default
            current_image_index = 0
            current_image_path = sorted_image_paths[current_image_index]
            image_placeholder = st.empty()
            image_placeholder.image(current_image_path, use_column_width=True)
            
            # Add a dropdown menu to select images
            selected_image = st.selectbox(
                'Select Image',
                options=filtered_images,
                index=current_image_index
            )
            
            # Update the displayed image based on the dropdown selection
            if selected_image:
                current_image_index = sorted_images.index(selected_image)
                current_image_path = os.path.join(image_folder, selected_image)
                image_placeholder.image(current_image_path, use_column_width=True)
                
                # Highlight the corresponding coordinate on the map and auto-zoom
                fig.data[0].marker.color = ['blue' if i == current_image_index else 'red' if row['Class Name'] == 'pothole' else 'orange' for i, row in df.iterrows()]
                fig.update_layout(
                    mapbox=dict(
                        center=dict(
                            lat=df.iloc[current_image_index]['Latitude'],
                            lon=df.iloc[current_image_index]['Longitude']
                        ),
                        zoom=15
                    )
                )
                map_placeholder.plotly_chart(fig, use_container_width=True)
                
            # Get the corresponding video file
            video_file = os.path.join(data_folder, selected_folder, f"{selected_folder}.mp4")
            
            if os.path.exists(video_file):
                # Display the video player
                st.video(video_file)
                
            else:
                st.write("No video available for the selected route and date.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
else:
    st.write("No data available for the selected route and date.")