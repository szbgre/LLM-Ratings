import plotly.graph_objects as go
import pandas as pd
import os
import json

def read_json_file(file_path):
    """Read a JSON file from a local directory."""
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_ratings(data):
    """Extract ratings from the fetched data."""
    return [entry['rating'] for entry in data if 'rating' in entry]

def ratings_to_df(ratings, category_name):
    """Convert ratings to a pandas DataFrame."""
    return pd.DataFrame([str(rating) for rating in ratings], columns=[category_name])

def fetch_all_json_files(directory_path):
    """Fetch all JSON files recursively from a local directory."""
    files = []
    for root, dirs, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith('.json'):
                files.append(os.path.join(root, filename))
    return files

def process_directory(directory_path):
    """Process all JSON files in a given directory to get a combined DataFrame."""
    file_paths = fetch_all_json_files(directory_path)
    print(f"Found JSON files: {file_paths}")
    data_frames = []
    file_names = []  # List to hold the names of the files for the plot
    for path in file_paths:
        data = read_json_file(path)
        if data and any('rating' in entry for entry in data):
            file_name = os.path.splitext(os.path.basename(path))[0]  # Extract file name without extension
            df = ratings_to_df(extract_ratings(data), file_name)
            data_frames.append(df)
            file_names.append(file_name.replace('_', ' '))  # Replace underscores with spaces for readability
        else:
            print(f"Skipping file (no 'rating' found): {path}")
    combined_df = pd.concat(data_frames, ignore_index=True, axis=1) if data_frames else pd.DataFrame()
    combined_df.columns = file_names  # Set the column names to the file names
    return combined_df


def plot_data(combined_df, category_names):
    fig = go.Figure()

    custom_colors = [
        'rgba(135, 206, 250, 0.6)',  # Light blue for '1'
        'rgba(100, 149, 237, 0.6)',  # Blue for '2'
        'rgba(64, 224, 208, 0.6)',   # Turquoise for '3'
        'rgba(255, 156, 143, 0.6)',  # Light coral for '4'
        'rgba(255, 182, 193, 0.6)'   # Pink for '5'
    ]

    captions = [
        "1: Misinterpreted",
        "2: Incorrect",
        "3: Partially Correct",
        "4: Mostly Correct",
        "5: Completely Correct"
    ]

    # Added dummy traces for the legend
    for i, color in enumerate(custom_colors):
        fig.add_trace(go.Bar(
            x=[0],
            y=[0],
            marker=dict(color=color),
            name=captions[i],
            showlegend=True
        ))

    # Calculate the total positive percentage for each category
    total_positive = {}
    for category in category_names:
        category_counts = combined_df[category].value_counts().sort_index()
        question_count = combined_df[category].count()
        positive_percent = sum(category_counts.get(str(rating), 0) for rating in [3, 4, 5]) / question_count * 100
        total_positive[category] = positive_percent

    # Calculate the average rating for each category
    average_ratings = {}
    for category in category_names:
        ratings = combined_df[category].astype(float)  # Convert ratings to float
        average_ratings[category] = ratings.mean()

    # Sort categories in ascending order based on total positive percentage
    sorted_categories = sorted(category_names, key=lambda x: average_ratings[x], reverse=False)

    # Plotting data in sorted order
    for category in sorted_categories:
        category_counts = combined_df[category].value_counts().sort_index()
        category_percentages = category_counts / combined_df[category].count() * 100

        # Plot negative ratings
        for rating in ['2', '1']:
            percent = category_percentages.get(rating, 0)
            count = category_counts.get(rating, 0)
            # Modify hovertext to handle singular/plural
            hovertext = f"{captions[int(rating) - 1]} - {count} {'answer' if count == 1 else 'answers'} ({percent:.1f}%)"
            fig.add_trace(go.Bar(
                x=[-percent],
                y=[f"{category} ({combined_df[category].count()} questions)"],
                orientation='h',
                marker=dict(color=custom_colors[int(rating) - 1]),
                hoverinfo='text',
                hovertext=hovertext,
                showlegend=False
            ))

        # Plot positive ratings
        for rating in ['3', '4', '5']:
            percent = category_percentages.get(rating, 0)
            count = category_counts.get(rating, 0)
            # Modify hovertext to handle singular/plural
            hovertext = f"{captions[int(rating) - 1]} - {count} {'answer' if count == 1 else 'answers'} ({percent:.1f}%)"
            fig.add_trace(go.Bar(
                x=[percent],
                y=[f"{category} ({combined_df[category].count()} questions)"],
                orientation='h',
                marker=dict(color=custom_colors[int(rating) - 1]),
                hoverinfo='text',
                hovertext=hovertext,
                showlegend=False
            ))

    # Update layout
    fig.update_layout(
        barmode='relative',
        title=f'Response Ratings from {directory_path}',
        xaxis=dict(title='Percentage', range=[-100, 100]),
        yaxis=dict(
            title='Category',
            type='category',
            tickmode='array',
            tickvals=[f"{cat} ({combined_df[cat].count()} questions)" for cat in sorted_categories],
            ticktext=[
                # Make average rating bold
                f"<b>{cat}</b> ({combined_df[cat].count()} questions)       Average rating: <b>{average_ratings[cat]:.2f}</b>"
                for cat in sorted_categories
            ]
        ),
        plot_bgcolor='rgba(248, 248, 255, 0.6)',
        paper_bgcolor='rgba(248, 248, 255, 0.6)',
        legend_title_text='Ratings',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            traceorder="normal"
        )
    )

    fig.show()

directory_path = "Q5"
combined_df = process_directory(directory_path)
if not combined_df.empty:
    category_names = [col for col in combined_df.columns]
    plot_data(combined_df, category_names)
else:
    print("No valid JSON files found for plotting.")