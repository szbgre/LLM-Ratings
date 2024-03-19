import streamlit as st
import json
import requests

def load_json_from_git(category, model_name):
    base_url = f"https://raw.githubusercontent.com/szbgre/LLM-Ratings/master/{category}/{model_name}.json"
    response = requests.get(base_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to load data for {model_name} in {category}: HTTP {response.status_code}")
        return None

def main():
    st.title('LLM Answers Evaluation')

    categories = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    labels_base_url = "https://raw.githubusercontent.com/szbgre/LLM-Ratings/master/Labels/"

    # Display category labels and make them clickable
    cols = st.columns(len(categories))
    selected_category = None
    for i, category in enumerate(categories):
        with cols[i]:
            if st.image(f"{labels_base_url}{category}.png", use_column_width=True, on_click=lambda c=category: select_category(c)):
                selected_category = category

    def select_category(category):
        nonlocal selected_category
        selected_category = category

    if selected_category:
        models = ['GPT3.5', 'GPT4', 'Llama-2-70B-Chat-GGU', 'Llama-2-70B-GGU']
        data = {}
        for model in models:
            data[model] = load_json_from_git(selected_category, model)

        if data:
            st.markdown(f"### Responses and Evaluations for {selected_category}")
            # Assuming all models have the same number of questions
            num_questions = min(len(data[model]) for model in models if data[model])
            for q_index in range(num_questions):
                question_displayed = False
                for model, responses in data.items():
                    if responses and q_index < len(responses):
                        response = responses[q_index]
                        if not question_displayed:
                            st.markdown(f"## Question {response['question_id']}")
                            st.write(response['prompt'])
                            question_displayed = True
                        
                        st.markdown(f"**{model} Output:**")
                        st.write(response['output'])
                        st.markdown(f"**Rating:** {response['rating']}")
                        if response['comment']:
                            st.markdown(f"**Comment:** {response['comment']}")

if __name__ == "__main__":
    main()
