import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, model:str ="text-embedding-ada-002") -> list[int]:
    text.replace("\n", " ")
    return openai.Embedding.create(input=text, model=model)["data"][0]["embedding"]  # type: ignore
