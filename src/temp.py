import requests

def api_call(df_chunk):
    data = df_chunk.to_dict(orient='records')  # Convert DataFrame to a list of dicts
    response = requests.post('http://api.example.com/data', json=data)
    # Process the response...
    return response

def process_dataframe(df):
    # Split the DataFrame into smaller chunks
    chunks = np.array_split(df, len(df) // TX_PER_CALL if len(df) % TX_PER_CALL == 0 else len(df) // TX_PER_CALL + 1)
    
    # Make an API call for each chunk
    for chunk in chunks:
        api_call(chunk)
