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
