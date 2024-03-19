import streamlit as st
import json
import requests  # For loading JSON files from GitHub

def load_json_from_github(category, model_name):
    base_url = f"https://github.com/szbgre/LLM-Ratings"
    response = requests.get(base_url)
    return response.json() if response.status_code == 200 else []

def main():
    st.title('Language Model Performance Evaluation')

    # Step 1: Choose a category
    st.markdown("### Step 1: Choose a category")
    category = st.selectbox("Select a category", ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'))

    # Step 2: Load JSON data for selected category
    models = ['GPT3.5', 'GPT4', 'Llama-2-70B-Chat-GGU', 'Llama-2-70B-GGU']
    data = {model: load_json_from_github(category, model) for model in models}

    # Step 3: Display questions and model responses
    if data:
        st.markdown("### Step 2: Evaluate the responses")

        # Assuming all models have the same number of questions
        for i in range(len(data[models[0]])):
            st.markdown(f"## Question {data[models[0]][i]['question_id']}")
            st.write(data[models[0]][i]['prompt'])

            for model in models:
                with st.expander(f"{model} Output"):
                    st.write(data[model][i]['output'])
                    st.markdown(f"**Rating:** {data[model][i]['rating']}")
                    st.text(f"Comment: {data[model][i]['comment']}")

if __name__ == "__main__":
    main()
