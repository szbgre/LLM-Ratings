import streamlit as st
import requests

def load_json_from_git(category, model_name):
    base_url = f"https://raw.githubusercontent.com/szbgre/LLM-Ratings/master/{category}/{model_name}.json"
    response = requests.get(base_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to load data for {model_name} in {category}: HTTP {response.status_code}")
        return None

def get_rating_color_and_description(rating):
    descriptions = {
        '1': 'Misinterpretation of the Problem',
        '2': 'Incorrect Solution',
        '3': 'Partially Correct Solution',
        '4': 'Mostly Correct Solution',
        '5': 'Completely Correct Solution'
    }
    custom_colors = [
        'rgba(135, 206, 250, 0.6)',  # Light blue for '1'
        'rgba(100, 149, 237, 0.6)',  # Blue for '2'
        'rgba(64, 224, 208, 0.6)',   # Turquoise for '3'
        'rgba(255, 156, 143, 0.6)',  # Light coral for '4'
        'rgba(255, 182, 193, 0.6)'   # Pink for '5'
    ]
    return custom_colors[int(rating) - 1], descriptions[str(rating)]

def main():
    st.title('LLM Answers Evaluation')

    categories = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    labels_base_url = "https://raw.githubusercontent.com/szbgre/LLM-Ratings/master/Labels/"
    categories_base_url = "https://raw.githubusercontent.com/szbgre/LLM-Ratings/master/Categories/"
    plots_base_url = "https://raw.githubusercontent.com/szbgre/LLM-Ratings/master/Plots/"

    # Display images first
    image_cols = st.columns(len(categories))
    for i, category in enumerate(categories):
        with image_cols[i]:
            st.image(f"{labels_base_url}{category}.png", use_column_width=True)

    # Display buttons below images
    button_cols = st.columns(len(categories))
    selected_category = None
    for i, category in enumerate(categories):
        with button_cols[i]:
            if st.button(category):
                selected_category = category

    if selected_category:
        st.image(f"{plots_base_url}{selected_category}.png", use_column_width=True, caption="Overview of the Ratings")
        
        models = ['GPT3.5', 'GPT4', 'Llama-2-70B-Chat-GGU', 'Llama-2-70B-GGU']
        data = {}
        for model in models:
            data[model] = load_json_from_git(selected_category, model)

        if data:
            st.image(f"{categories_base_url}{selected_category}.png", use_column_width=True)
            st.markdown(f"### Responses and Evaluations for {selected_category}")
            
            # Assuming all models have the same number of questions
            num_questions = min(len(data[model]) for model in models if data[model])
            for q_index in range(num_questions):
                question_displayed = False
                for model in models:
                    responses = data[model]
                    if responses and q_index < len(responses):
                        response = responses[q_index]
                        if not question_displayed:
                            st.markdown("________________________")
                            st.markdown(f"#### Question {response['question_id']}")
                            st.markdown(f"{response['prompt']}")
                            st.markdown("________________________")
                            question_displayed = True

                        rating_color, description = get_rating_color_and_description(response['rating'])
                        with st.container():
                            st.markdown(f"""
                            <div style="border: 1px solid #ccc; border-radius: 5px; padding: 10px; background-color: {rating_color};"
                                        title="{description}: {response['comment']}">
                                <h4>{model}</h4>
                                <p><strong>Rating:</strong> {response['rating']} - {description}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        st.write(response['output'])

    st.markdown("### Explanation of Ratings")
    st.image("Ratings/Ratings.png", use_column_width=True)

if __name__ == "__main__":
    main()
