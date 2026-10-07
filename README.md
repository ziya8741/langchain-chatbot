# LangChain Stateful Chatbot

A lightweight conversational chatbot built with [Streamlit](https://streamlit.io/),
[LangChain](https://www.langchain.com/), and [Groq](https://groq.com/). The app
maintains conversation history for each session ID and lets you choose the
Groq model and response language from the sidebar.

## Features

- Chat interface powered by Streamlit
- Groq-hosted language models through `langchain-groq`
- Stateful conversation history per session ID
- Selectable assistant language:
  - English
  - Hindi
  - Spanish
  - French
  - German
- Groq model selection loaded from the API when available
- Context-window management with `tiktoken`-based message trimming
- Clear history for the active session
- API key entry in the sidebar or through an environment variable

## Requirements

- Python 3.9 or newer
- A [Groq API key](https://console.groq.com/keys)

## Installation

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/ziya8741/langchain-chatbot.git
   cd langchain-chatbot
   ```

2. Create and activate a virtual environment:

   **Windows PowerShell**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You can enter the API key directly into the **Groq API Key** field in the
sidebar. Alternatively, create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` files or API keys to source control.

## Running the app

Start the Streamlit application with:

```bash
streamlit run app.py
```

Streamlit will print a local URL, typically
`http://localhost:8501`, which you can open in your browser.

## Using the chatbot

1. Provide a Groq API key if one was not loaded from `.env`.
2. Select a model from the **Model** dropdown.
3. Select the assistant's response language.
4. Set a **Session ID** to identify a conversation.
5. Enter a message in the chat box.
6. Use **Clear Chat History** to reset the active session.

Changing the session ID switches to a separate in-memory conversation. Session
history is lost when the Streamlit process restarts because it is not persisted
to a database or file.

## Project structure

```text
.
├── app.py            # Streamlit UI and LangChain chatbot chain
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

## How it works

1. The app loads environment variables with `python-dotenv`.
2. It creates a `ChatGroq` model using the selected model and API key.
3. LangChain's `RunnableWithMessageHistory` stores messages by session ID.
4. A prompt instructs the assistant to respond in the selected language.
5. Older messages are trimmed to a 1,024-token context using `tiktoken`.
6. Streamlit renders the conversation and accepts new chat input.

## Troubleshooting

### The app asks for an API key

Set `GROQ_API_KEY` in `.env`, or enter the key in the sidebar. Restart the app
after changing environment variables.

### Model initialization or generation fails

Verify that the API key is valid and that the selected model is available in
your Groq account. Also check the terminal running Streamlit for the complete
error message.

### Dependencies are missing

Ensure the virtual environment is activated and reinstall the dependencies:

```bash
pip install -r requirements.txt
```

## License

No license file is currently included in this repository.
