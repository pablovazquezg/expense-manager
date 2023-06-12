import os
import dotenv

import openai
import numpy as np
import pandas as pd
from src.get_embedding import get_embedding
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import DeepLake
from sklearn.metrics.pairwise import cosine_similarity

def find_similar_description(new_description: str, embeddings: np.ndarray, n=5):
    """Find the transactions in the data that are most similar to a new description."""
    
    # Convert the new_description_vector and description_vectors to float
    new_description_vector = get_embedding(new_description)
    vstacked_embeddings = np.vstack(embeddings) # type: ignore

    # Compute the cosine similarity between the new description vector and each description vector in the data
    similarities = cosine_similarity([new_description_vector], vstacked_embeddings) # type: ignore

    # Flatten the list of similarities
    similarities = np.array(similarities).flatten()

    # Find the indices of the top n most similar descriptions
    most_similar_indices = np.argsort(similarities)[-n:][::-1]

    # Return the most similar descriptions and their corresponding categories
    return most_similar_indices




