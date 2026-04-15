import dotenv
dotenv.load_dotenv()

from openai import OpenAI

client = OpenAI()

vs = client.vector_stores.create(name="life-coach-memory")
print(vs.id)