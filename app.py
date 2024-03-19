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

    col1, col2 = st.columns(2)
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/800px-ChatGPT_logo.svg.png", width=300)
    with col2:
        st.image("https://eu-images.contentstack.com/v3/assets/blt6b0f74e5591baa03/blt98d8a946b63c9b5f/64b7170ab314c94aa481d8c3/Untitled_design_(1).jpg", width=540)

    st.markdown("### Step 1: Choose a category")
    category = st.selectbox("Select a category", ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])

    models = ['GPT3.5', 'GPT4', 'Llama-2-70B-Chat-GGU', 'Llama-2-70B-GGU']
    data = {}
    for model in models:
        data[model] = load_json_from_git(category, model)

    if data:
        st.markdown("### Responses and Evaluations")
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
