
from io import StringIO
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import json
load_dotenv()


# def process(uploaded_files, from_local=False):
#     text = ""
#     # if it is single file then no use for loop
#     if (from_local):
#         print("local")
#         for data_file in uploaded_files:
#             # print(data_file)
#             name = data_file.filename
#             extension = name.split(".")[1]
#             print(extension)
#             if data_file is not None and extension == "txt":
#                 stringio = StringIO(data_file.read().decode("utf-8"))
#                 txt = stringio.read()
#                 text += txt
#             if data_file is not None and extension == "pdf":
#                 pdf_reader = PdfReader(data_file)
#                 for page in pdf_reader.pages:
#                     text += page.extract_text()
#     else:
#         for file in uploaded_files:
#             text += file.read().decode("utf-8")
#     return json.dumps({"text": text, "name": name, "extension": extension})

def process(uploaded_file, from_local=False):
    text = ""
    file = uploaded_file[0]
    name = file.filename
    extension = name.split(".")[1]

    if (from_local):       
        print(extension)
        if file is not None and extension == "txt":
            stringio = StringIO(file.read().decode("utf-8"))
            txt = stringio.read()
            text += txt
        if file is not None and extension == "pdf":
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    else:       
        text += file.read().decode("utf-8")
    return json.dumps({"text": text, "name": name, "extension": extension})
