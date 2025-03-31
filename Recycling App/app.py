# app.py

"""
=========================================================
 1) IMPORTS & DEPENDENCIES
=========================================================
"""
import gradio as gr
import torch
import theme
theme = theme.Theme()

from huggingface_hub import from_pretrained_keras
from tensorflow.keras.applications import EfficientNetB0
import tensorflow as tf
from tensorflow import keras

from PIL import Image
import shutil

import tenacity  # for retrying failed requests
from fake_useragent import UserAgent

# LangChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain.chains import RetrievalQA, ConversationalRetrievalChain, LLMChain
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from langchain_community.llms import HuggingFaceHub
from langchain_community.document_loaders import WebBaseLoader
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory

from pydantic.v1 import BaseModel, Field

# Import the separate file that contains our list of URLs
from url_list import URLS


"""
=========================================================
 2) IMAGE CLASSIFICATION MODEL SETUP
=========================================================
"""
# Load a Keras model from HuggingFace Hub
model1 = from_pretrained_keras("rocioadlc/efficientnetB0_trash")

# Define class labels for the trash classification
class_labels = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

def predict_image(input_image):
    """
    Resize the user-uploaded image and preprocess it so that it can be fed
    into the EfficientNetB0 model. The model then returns a dictionary of
    class probabilities.
    """
    # Resize the image (note the target dimensions)
    image_array = tf.keras.preprocessing.image.img_to_array(
        input_image.resize((244, 224))
    )
    # Normalize/prescale the image for EfficientNet
    image_array = tf.keras.applications.efficientnet.preprocess_input(image_array)
    # Expand the dimensions to create a batch of size 1
    image_array = tf.expand_dims(image_array, 0)
    # Get predictions
    predictions = model1.predict(image_array)
    
    # Convert predictions into a dictionary {class_label: score}
    category_scores = {}
    for i, class_label in enumerate(class_labels):
        category_scores[class_label] = predictions[0][i].item()
    
    return category_scores

# Gradio interface for image classification
image_gradio_app = gr.Interface(
    fn=predict_image,
    inputs=gr.Image(label="Image", sources=['upload', 'webcam'], type="pil"),
    outputs=[gr.Label(label="Result")],
    title="<span style='color: rgb(243, 239, 224);'>Green Greta</span>",
    theme=theme
)

"""
=========================================================
 3) CHATBOT MODEL SETUP
=========================================================
"""
# 3.1) Define user agent to avoid blocking, etc.
user_agent = UserAgent().random
header_template = {"User-Agent": user_agent}


@tenacity.retry(
    wait=tenacity.wait_fixed(3),   # wait 3 seconds between retries
    stop=tenacity.stop_after_attempt(3),  # stop after 3 attempts
    reraise=True
)
def load_url(url):
    """
    Use the WebBaseLoader for a single URL.
    The function is retried if it fails due to connection issues.
    """
    loader = WebBaseLoader(
        web_paths=[url],
        header_template=header_template
    )
    return loader.load()


def safe_load_all_urls(urls):
    """
    Safely load documents from a list of URLs.
    Any URL that fails after the specified number of retries is skipped.
    """
    all_docs = []
    for link in urls:
        try:
            docs = load_url(link)
            all_docs.extend(docs)
        except Exception as e:
            # If load_url fails after all retries, skip that URL
            print(f"Skipping URL due to error: {link}\nError: {e}\n")
    return all_docs

# 3.2) Actually load the data from all URLs (imported from url_list.py)
all_loaded_docs = safe_load_all_urls(URLS)

# 3.3) Split the documents into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024,
    chunk_overlap=150,
    length_function=len
)
docs = text_splitter.split_documents(all_loaded_docs)

# 3.4) Create embeddings
embeddings = HuggingFaceEmbeddings(model_name='thenlper/gte-small')

# 3.5) Create a persistent directory to store vector DB
persist_directory = 'docs/chroma/'
shutil.rmtree(persist_directory, ignore_errors=True)  # remove old DB files

# 3.6) Build Chroma vector store
vectordb = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory=persist_directory
)

# 3.7) Create a retriever
retriever = vectordb.as_retriever(
    search_kwargs={"k": 2},
    search_type="mmr"
)

"""
=========================================================
 4) PROMPT & CHAIN SETUP
=========================================================
"""
# 4.1) Define the schema for final chatbot answers
class FinalAnswer(BaseModel):
    question: str = Field()
    answer: str = Field()

parser = PydanticOutputParser(pydantic_object=FinalAnswer)

# 4.2) Prompt template: system instructions
template = """
Your name is Greta and you are a recycling chatbot with the objective to answer questions from user in English or Spanish /
Has sido diseñado y creado por el Grupo 1 del Máster en Data Science & Big Data de la promoción 2023/2024 de la Universidad Complutense de Madrid. Este grupo está formado por Rocío, María Guillermo, Alejandra, Paloma y Álvaro /
Use the following pieces of context to answer the question /
If the question is English answer in English /
If the question is Spanish answer in Spanish /
Do not mention the word context when you answer a question /
Answer the question fully and provide as much relevant detail as possible. Do not cut your response short /
Context: {context}
User: {question}
{format_instructions}
"""

sys_prompt = SystemMessagePromptTemplate.from_template(template)
qa_prompt = ChatPromptTemplate(
    messages=[
        sys_prompt,
        HumanMessagePromptTemplate.from_template("{question}")
    ],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# 4.3) Define the LLM from HuggingFace
llm = HuggingFaceHub(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    task="text-generation",
    model_kwargs={
        "max_new_tokens": 2000,
        "top_k": 30,
        "temperature": 0.1,
        "repetition_penalty": 1.03
    },
)

# 4.4) Create a ConversationalRetrievalChain that uses the above LLM
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    memory=ConversationBufferMemory(
        llm=llm,
        memory_key="chat_history",
        input_key='question',
        output_key='output'
    ),
    retriever=retriever,
    verbose=True,
    combine_docs_chain_kwargs={'prompt': qa_prompt},
    get_chat_history=lambda h : h,  # pass memory directly
    rephrase_question=False,
    output_key='output'
)

def chat_interface(question, history):
    """
    This function processes the user's question through the qa_chain,
    then parses out the final answer from the chain's output.
    """
    result = qa_chain.invoke({'question': question})
    output_string = result['output']

    # Find the index of the last occurrence of '"answer":' in the string
    answer_index = output_string.rfind('"answer":')
    answer_part = output_string[answer_index + len('"answer":'):].strip()

    # Find the next occurrence of a double quote to get the start of the answer value
    quote_index = answer_part.find('"')
    answer_value = answer_part[quote_index + 1:answer_part.find('"', quote_index + 1)]
    
    return answer_value


# Gradio chat interface for the chatbot
chatbot_gradio_app = gr.ChatInterface(
    fn=chat_interface,
    title="<span style='color: rgb(243, 239, 224);'>Green Greta</span>"
)

"""
=========================================================
 5) BANNER / WELCOME TAB
=========================================================
"""
banner_tab_content = """
<div style="background-color: #d3e3c3; text-align: center; padding: 20px; display: flex; flex-direction: column; align-items: center;">
    <img src="https://huggingface.co/spaces/ALVHB95/TFM_DataScience_APP/resolve/main/front_4.jpg" alt="Banner Image" style="width: 50%; max-width: 500px; margin: 0 auto;">
    <h1 style="font-size: 24px; color: #4e6339; margin-top: 20px;">¡Bienvenido a nuestro clasificador de imágenes y chatbot para un reciclaje más inteligente!♻️</h1>
    <p style="font-size: 16px; color: #4e6339; text-align: justify;">¿Alguna vez te has preguntado si puedes reciclar un objeto en particular? ¿O te has sentido abrumado por la cantidad de residuos que generas y no sabes cómo manejarlos de manera más sostenible? ¡Estás en el lugar correcto!</p>
    <p style="font-size: 16px; color: #4e6339; text-align: justify;">Nuestra plataforma combina la potencia de la inteligencia artificial con la comodidad de un chatbot para brindarte respuestas rápidas y precisas sobre qué objetos son reciclables y cómo hacerlo de la manera más eficiente.</p>
    <p style="font-size: 16px; text-align:center;"><strong><span style="color: #4e6339;">¿Cómo usarlo?</span></strong></p>
    <ul style="list-style-type: disc; text-align: justify; margin-top: 20px; padding-left: 20px;">
        <li style="font-size: 16px; color: #4e6339;"><strong><span style="color: #4e6339;">Green Greta Image Classification:</span></strong> Ve a la pestaña Greta Image Classification y simplemente carga una foto del objeto que quieras reciclar, y nuestro modelo de identificará de qué se trata🕵️‍♂️ para que puedas desecharlo adecuadamente.</li>
        <li style="font-size: 16px; color: #4e6339;"><strong><span style="color: #4e6339;">Green Greta Chat:</span></strong> ¿Tienes preguntas sobre reciclaje, materiales específicos o prácticas sostenibles? ¡Pregunta a nuestro chatbot en la pestaña Green Greta Chat!📝 Está aquí para responder todas tus preguntas y ayudarte a tomar decisiones más informadas sobre tu reciclaje.</li>
    </ul>
    <h1 style="font-size: 24px; color: #4e6339; margin-top: 20px;">Welcome to our image classifier and chatbot for smarter recycling!♻️</h1>
    <p style="font-size: 16px; color: #4e6339; text-align: justify;">Have you ever wondered if you can recycle a particular object? Or felt overwhelmed by the amount of waste you generate and don't know how to handle it more sustainably? You're in the right place!</p>
    <p style="font-size: 16px; color: #4e6339; text-align: justify;">Our platform combines the power of artificial intelligence with the convenience of a chatbot to provide you with quick and accurate answers about which objects are recyclable and how to do it most efficiently.</p>
    <p style="font-size: 16px; text-align:center;"><strong><span style="color: #4e6339;">How to use it?</span></strong>
    <ul style="list-style-type: disc; text-align: justify; margin-top: 20px; padding-left: 20px;">
        <li style="font-size: 16px; color: #4e6339;"><strong><span style="color: #4e6339;">Green Greta Image Classification:</span></strong> Go to the Greta Image Classification tab and simply upload a photo of the object you want to recycle, and our model will identify what it is🕵️‍♂️ so you can dispose of it properly.</li>
        <li style="font-size: 16px; color: #4e6339;"><strong><span style="color: #4e6339;">Green Greta Chat:</span></strong> Have questions about recycling, specific materials, or sustainable practices? Ask our chatbot in the Green Greta Chat tab!📝 It's here to answer all your questions and help you make more informed decisions about your recycling.</li>
    </ul>
</div>
"""
banner_tab = gr.Markdown(banner_tab_content)

"""
=========================================================
 6) GRADIO FINAL APP: TABS
=========================================================
"""
app = gr.TabbedInterface(
    [banner_tab, image_gradio_app, chatbot_gradio_app],
    tab_names=["Welcome to Green Greta", "Green Greta Image Classification", "Green Greta Chat"],
    theme=theme
)

# Enable queue() for concurrency and launch the Gradio app
app.queue()
app.launch()
