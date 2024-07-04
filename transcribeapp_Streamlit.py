import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# Bedrockのエンドポイントと認証情報
BEDROCK_ENDPOINT = "https://your-bedrock-endpoint.aws.amazon.com"
BEDROCK_API_KEY = "your-bedrock-api-key"

# Lambda関数のエンドポイント
LAMBDA_ENDPOINT = "https://your-lambda-endpoint.aws.amazon.com/prod"

# データ保存用
data = []

# タイトル
st.title("手書き内容デジタル化アプリ")

# 機能1: 手書き用紙の写真データをアップロードするページ
st.header("1. 手書き用紙の写真をアップロード")
uploaded_file = st.file_uploader("写真をアップロードしてください", type=["jpg", "png"])

if uploaded_file:
    # Lambdaに画像を送信してテキストを抽出
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(LAMBDA_ENDPOINT, files=files)
    output = response.json()

    # 機能2: アップロードされた写真とBedrockから返信されたテキスト内容を表示
    st.header("2. 手書き内容の確認・修正")
    st.image(uploaded_file, caption="アップロードされた写真")
    st.write("Bedrockから抽出されたテキスト:")
    extracted_text = st.text_area("手書き内容", output["extracted_text"])

    # 企業名、部署名、メールアドレス、電話番号を入力
    company_name = st.text_input("企業名", output.get("company_name", ""))
    department_name = st.text_input("部署名", output.get("department_name", ""))
    email = st.text_input("メールアドレス", output.get("email", ""))
    phone_number = st.text_input("電話番号", output.get("phone_number", ""))

    if st.button("Checked"):
        # データを保存
        data.append({
            "image": uploaded_file,
            "text": extracted_text,
            "company_name": company_name,
            "department_name": department_name,
            "email": email,
            "phone_number": phone_number
        })
        st.success("データが登録されました。")

# 機能3: 登録データ一覧を表示
st.header("3. 登録データ一覧")
df = pd.DataFrame(data)
st.write(df)

# データをエクセルで抽出
if st.button("Extract"):
    csv = df.to_csv(index=False)
    b = BytesIO(csv.encode())
    st.download_button(
        label="データをダウンロード",
        data=b,
        file_name="data.csv",
        mime="text/csv",
    )

# 機能4: チャットボット
st.header("4. チャットボット")
query = st.text_input("質問を入力してください")

if query:
    headers = {"x-api-key": BEDROCK_API_KEY}
    data = {"query": query, "data": df.to_dict("records")}
    response = requests.post(BEDROCK_ENDPOINT, headers=headers, json=data)
    answer = response.json()["answer"]
    st.write("回答:", answer)

