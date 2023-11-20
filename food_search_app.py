import streamlit as st
import openai
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# Assuming you have set up your OpenAI API key
openai.api_key = 'your-api-key'

# Function to send a query to the ChatGPT API
def query_chatgpt(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Function to preprocess and combine text data for FAISS
def preprocess_data(row):
    return f"{row['Food Name']} {row['Type']} {row['Regional Category']} {row['Dish Type']} {row['Course']} {row['Drink Type']}"

# Load and preprocess your dataset
data = pd.read_csv('food.csv')
data['combined_text'] = data.apply(preprocess_data, axis=1)

# Convert to vectors using a sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
vectors = model.encode(data['combined_text'].tolist())

# Create and train a FAISS index
dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(vectors)

# Function for searching in FAISS index
def search_faiss_index(query, k=5):
    query_vector = model.encode([query])
    _, indices = index.search(query_vector, k)
    return data.iloc[indices[0]]

# Streamlit app layout
st.title("Food Search Application")
user_input = st.text_input("Enter your food query:")

if st.button("Search"):
    if user_input:
        try:
            gpt_response = query_chatgpt(user_input)
            results = search_faiss_index(gpt_response)
            st.write(results)
        except Exception as e:
            st.error("An error occurred: " + str(e))
    else:
        st.warning("Please enter a query.")
