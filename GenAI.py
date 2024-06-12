import tempfile
import streamlit as st
import pytesseract
from PIL import Image
import openai
import os
import fitz


os.environ["HTTP_PROXY"] = "proxy.its.hpecorp.net:8080"
os.environ["HTTPS_PROXY"] = "proxy.its.hpecorp.net:8080"
openai.api_key = os.getenv('OPENAI_API_KEY')


# Read PDF File
def extract_text_from_pdf(file):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file.read())
        tmp_file_path = tmp_file.name
    with fitz.open(tmp_file_path) as pdf_document:
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text


def extract_text_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text


def call_openai_api(prompt, max_tokens=1500):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=max_tokens
    )
    return response.choices[0].text.strip()


# Information extraction function
def extract_information(text):
    prompt = f"Extract key financial metrics:\n{text}"
    return call_openai_api(prompt)


def compliance_analysis(extracted_info):
    prompt = f"Analyze the following financial metrics:\n{extracted_info}"
    return call_openai_api(prompt)


def summarize_financial_statement(extracted_info):
    prompt = f"Summarize the following financial metrics:\n{extracted_info}"
    return call_openai_api(prompt, max_tokens=500)


def retrieve_regulations(query):
    prompt = f"Retrieve relevant regulatory information :\n{query}"
    return call_openai_api(prompt)


# Streamlit app
def main():
    st.title('Automated Financial Statement Analysis and Compliance Tool')
    uploaded_file = st.file_uploader("Upload a PDF or Image file of a financial statement", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.write("File uploaded successfully!")
        file_type = uploaded_file.type
        extracted_text = ""
        if file_type == "application/pdf":
            st.write("Processing PDF file...", uploaded_file.name)
            extracted_text = extract_text_from_pdf(uploaded_file)
            st.write("Extracted Text:")
            st.text_area("", extracted_text, height=300)
        elif file_type in ["image/png", "image/jpeg"]:
            st.write("Processing Image file...")
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            extracted_text = extract_text_from_image(image)
            st.write("Extracted Text:")
            st.text_area("", extracted_text, height=300)

        extracted_info = extract_information(extracted_text)
        compliance_report = compliance_analysis(extracted_info)
        summary = summarize_financial_statement(extracted_info)

        st.subheader("Extracted Information")
        st.write(extracted_info)

        st.subheader("Compliance Report")
        st.write(compliance_report)

        st.subheader("Summary")
        st.write(summary)

        query = "current financial regulations"
        regulations = retrieve_regulations(query)
        st.subheader("Relevant Regulations")
        st.write(regulations)


if __name__ == "__main__":
    main()
