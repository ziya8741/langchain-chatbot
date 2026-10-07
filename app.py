import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(page_title="LangChain Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 LangChain Stateful Chatbot")

# Sidebar for configuration
st.sidebar.header("Configuration")

@st.cache_data(ttl=3600)
def get_groq_models(api_key_val):
    default_models = ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
    if not api_key_val:
        return default_models
    try:
        from groq import Groq
        client = Groq(api_key=api_key_val)
        models = client.models.list()
        fetched = [m.id for m in models.data]
        # Bring default models to the front if they exist, then append the rest
        sorted_models = [m for m in default_models if m in fetched]
        sorted_models += [m for m in fetched if m not in default_models]
        return sorted_models if sorted_models else default_models
    except Exception:
        return default_models

api_key = st.sidebar.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
model_name = st.sidebar.selectbox("Model", get_groq_models(api_key))
language = st.sidebar.selectbox("Assistant Language", ["English", "Hindi", "Spanish", "French", "German"])
session_id = st.sidebar.text_input("Session ID", value="chat1")

if st.sidebar.button("Clear Chat History"):
    if "store" in st.session_state and session_id in st.session_state.store:
        st.session_state.store[session_id].clear()
        st.session_state.messages = []
        st.rerun()

# Initialize session state for storing history
if "store" not in st.session_state:
    st.session_state.store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = ChatMessageHistory()
    return st.session_state.store[session_id]

if not api_key:
    st.warning("Please enter your Groq API Key in the sidebar to start chatting.")
    st.stop()

# Initialize Model
try:
    model = ChatGroq(model=model_name, groq_api_key=api_key)
except Exception as e:
    st.error(f"Error initializing model: {e}")
    st.stop()

# Set up Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Trimmer for context window management
import tiktoken

def custom_token_counter(messages) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    if isinstance(messages, list):
        return sum(len(enc.encode(m.content)) for m in messages)
    return len(enc.encode(messages.content))

trimmer = trim_messages(
    max_tokens=1024,
    strategy="last",
    token_counter=custom_token_counter,
    include_system=True,
    allow_partial=False,
    start_on="human"
)

# Construct Chain
chain = (
    RunnablePassthrough.assign(messages=itemgetter("messages") | trimmer)
    | prompt
    | model
)

# Wrap with Message History
with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages",
)

# Display chat history from session state store
history = get_session_history(session_id)

for msg in history.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)
    elif isinstance(msg, SystemMessage):
        pass # Don't display system messages

# Chat Input
if user_input := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        config = {"configurable": {"session_id": session_id}}
        
        with st.spinner("Thinking..."):
            try:
                response = with_message_history.invoke(
                    {
                        "messages": [HumanMessage(content=user_input)],
                        "language": language,
                    },
                    config=config,
                )
                message_placeholder.markdown(response.content)
            except Exception as e:
                st.error(f"Error during generation: {e}")
