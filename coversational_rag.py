# conversational_rag.py
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from flask import session


class ConversationalRAG:
    def __init__(self, file_paths, api_key, model_name="llama3-8b-8192", embedding_model="all-mpnet-base-v2"):
        # Initialize models
        self.embed_model = HuggingFaceEmbeddings(model_name=embedding_model)
        self.chat_model = ChatGroq(temperature=0, model_name=model_name, api_key=api_key)
        self.system_prompt = """You are a highly intelligent and professional customer support assistant for Samsung products. Your goal is to assist customers with their queries in a friendly, polite, and efficient manner. \
        Use the following pieces of retrieved context and chat history to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\
        Ask follow up question to user\

        {context}"""
        # Load and index documents from both PDF and CSV files
        documents = []
        for file_path in file_paths:
            if file_path.endswith(".csv"):
                loader = CSVLoader(file_path=file_path)
            elif file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path=file_path)
            else:
                raise ValueError("Unsupported file format. Only CSV and PDF files are allowed.")
            documents.extend(loader.load())
        
        # Split documents into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        # Create a FAISS index for the document embeddings
        self.faiss_index = FAISS.from_documents(docs, self.embed_model)
        self.retriever = self.faiss_index.as_retriever(search_kwargs={"k": 6})

        # Initialize store for session history
        self.store = {}

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def get_history_aware_retriever(self):
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            self.chat_model, self.retriever, contextualize_q_prompt
        )

        return history_aware_retriever

    def qa_with_memory(self, user_question: str, session_id: str):
        qa_system_prompt = self.system_prompt
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(self.chat_model, qa_prompt)

        history_aware_retriever = self.get_history_aware_retriever()
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        chat_history_content = [message.content for message in self.get_session_history(session_id).messages]
        return [conversational_rag_chain.invoke(
            {"input": user_question},
            config={
                "configurable": {"session_id": session_id}
            },
        )["answer"], [message.content for message in self.get_session_history(session_id).messages]]
