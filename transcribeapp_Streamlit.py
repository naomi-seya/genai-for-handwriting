import os
from io import BytesIO

import boto3
import pandas as pd
import streamlit as st
from PIL import Image

# Amazon Bedrock ClientをInitialize
bedrock = boto3.client("bedrock")

# アップロードされたファイルを保持するリスト
uploaded_files = []

# 関数の定義
def upload_page():
    st.title("Upload Handwritten Document")
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded Image", use_column_width=True)

        # Amazon Bedrock に Image を送信
        response = bedrock.detect_document_text(
            Document={"Bytes": uploaded_file.getvalue()}
        )

        # Bedrockから抽出したデータ
        entities = {
            "company": [
                item["Text"]
                for item in response["Blocks"]
                if item["BlockType"] == "WORD" and "企業名" in item["Text"]
            ],
            "department": [
                item["Text"]
                for item in response["Blocks"]
                if item["BlockType"] == "WORD" and "部署名" in item["Text"]
            ],
            "email": [
                item["Text"]
                for item in response["Blocks"]
                if item["BlockType"] == "WORD" and "@" in item["Text"]
            ],
            "phone": [
                item["Text"]
                for item in response["Blocks"]
                if item["BlockType"] == "WORD"
                and any(char.isdigit() for char in item["Text"])
            ],
            "content": " ".join(
                [
                    item["Text"]
                    for item in response["Blocks"]
                    if item["BlockType"] == "LINE"
                ]
            ),
        }

        if st.button("Upload"):
            uploaded_files.append({"image": image, "entities": entities})
            st.success(f"File uploaded successfully!")

def check_page():
    st.title("Check and Modify Extracted Text")
    if uploaded_files:
        for file in uploaded_files:
            st.image(file["image"], use_column_width=True)
            st.write("Extracted Entities:")
            entities = file["entities"]
            entities["company"] = st.text_area(
                "Company", "\n".join(entities["company"])
            )
            entities["department"] = st.text_area(
                "Department", "\n".join(entities["department"])
            )
            entities["email"] = st.text_area("Email", "\n".join(entities["email"]))
            entities["phone"] = st.text_area("Phone", "\n".join(entities["phone"]))
            entities["content"] = st.text_area("Content", entities["content"])
            if st.button("Checked"):
                file["entities"] = {
                    "company": [
                        e.strip() for e in entities["company"].split("\n") if e.strip()
                    ],
                    "department": [
                        e.strip()
                        for e in entities["department"].split("\n")
                        if e.strip()
                    ],
                    "email": [
                        e.strip() for e in entities["email"].split("\n") if e.strip()
                    ],
                    "phone": [
                        e.strip() for e in entities["phone"].split("\n") if e.strip()
                    ],
                    "content": entities["content"],
                }
                st.success("Data checked and updated!")
    else:
        st.warning("No files uploaded yet.")

def view_page():
    st.title("View Checked Data")
    if uploaded_files:
        data = []
        for file in uploaded_files:
            entities = file["entities"]
            for company in entities["company"]:
                for department in entities["department"]:
                    for email in entities["email"]:
                        for phone in entities["phone"]:
                            data.append(
                                {
                                    "Company": company,
                                    "Department": department,
                                    "Email": email,
                                    "Phone": phone,
                                    "Content": entities["content"],
                                }
                            )
        df = pd.DataFrame(data)
        st.dataframe(df)

        csv = df.to_csv().encode("utf-8")
        excel = BytesIO()
        writer = pd.ExcelWriter(excel, engine="xlsxwriter")
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        writer.save()
        excel.seek(0)

        if st.button("Extract"):
            st.download_button(
                label="Download Excel file",
                data=excel.getvalue(),
                file_name="data.xlsx",
                mime="application/vnd.ms-excel",
            )
    else:
        st.warning("No data to display.")

def chat_page():
    st.title("Chat with Bedrock")
    query = st.text_area("Enter your query")
    if st.button("Submit"):
        # Amazon Bedrock に質問を送信し、回答を取得する処理を記述する必要があります。
        # 回答の生成にはアップロードされたデータを参照する必要があります。
        response = "この部分は回答を生成する処理を記述する必要があります。"
        st.write(response)

# ページ選択
pages = {
    "Upload": upload_page,
    "Check": check_page,
    "View": view_page,
    "Chat": chat_page,
}

selection = st.sidebar.radio("Go to", list(pages.keys()))
pages[selection]()
