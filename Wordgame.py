import streamlit as st
from langchain.chains import LLMChain
from langchain.llms import Bedrock
from langchain.prompts import PromptTemplate

# Streamlitアプリの作成
st.title("単語当てクイズ")

# answerを初期化
if "answer" not in st.session_state:
    st.session_state.answer = None

# チャット履歴を初期化
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# /answerで単語を登録する、/stopで単語を削除する、/showanswerで答えを表示する
def handle_user_input():
    if user_input.startswith("/answer:"):
        st.session_state.answer = user_input.split(":")[1]
    elif user_input == "/stop":
        st.session_state.answer = None
        st.success("答えを削除しました。")
    elif user_input == "/showanswer":
        if st.session_state.answer:
            st.success(f"答えは '{st.session_state.answer}' です。")
        else:
            st.warning("答えが登録されていません。")


user_input = st.text_input(
    "答えを /answer:単語 の形式で入力してください。/stopで答えを削除でき、/showanswerで答えを表示できます。",
    on_change=handle_user_input,
    key="user_input",
)

# チャット画面
if st.session_state.answer is not None:
    if "user_query" not in st.session_state:
        st.session_state.user_query = ""  # user_queryを初期化

    user_query = st.text_input("質問を入力してください。", key="user_query")

    if user_query:
        answer = st.session_state.answer
        template = f"""
         あなたは優秀な出題者です。
         回答者からの質問を日本語から英語に翻訳し、その後に正確に「はい/Yes」、「いいえ/No」のいずれかで回答します。
         答えは「{answer}」です。この答えを教えてはいけません。
         翻訳された質問に対して「{answer}」が当てはまる場合は「はい/Yes」、あてはまらない場合は「いいえ/No」と正確に答えてください。
         回答は「はい/Yes」、「いいえ/No」のみ答えてください。

        問題: {{inputs}}"""
        prompt = PromptTemplate(template=template, input_variables=["inputs"])
        inputs = {"inputs": user_query}
        llm_chain = LLMChain(
            llm=Bedrock(model_id="anthropic.claude-instant-v1"), prompt=prompt
        )
        result = llm_chain.run(inputs)
        st.session_state.chat_history.append({"query": user_query, "response": result})
        for chat in st.session_state.chat_history:
            st.chat_message("user").write(chat["query"])
            st.chat_message("ai").write(chat["response"])
