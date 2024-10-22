# from sanic import Sanic
# from sanic.response import json
#
# # Create a Sanic app
# app = Sanic("HelloWorldApp")
#
# # Define a route for the root URL ("/")
# @app.route("/")
# async def hello_world(request):
#     return json({"message": "Hello, World!"})
#
# # Run the app
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)
import mimetypes
from sanic import Sanic
from sanic.response import html, file, json as sanic_json  # Alias the Sanic json response
from sanic.exceptions import InvalidUsage
import os
import google.generativeai as genai
import re
import json  # Import the standard json module for parsing JSON
import io
genai.configure(api_key='AIzaSyAQKs3aH3az5dNe4tBOIIkUM684fZvg_rE')
app = Sanic("SPARK")

# Define the path to your UI folder and static folder
UI_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'UI')
STATIC_FOLDER = os.path.join(UI_FOLDER, 'static')
UPLOADS_FOLDER = ('/tmp')

# Ensure the uploads folder exists
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

# Serve static files for CSS and images
app.static('/static', STATIC_FOLDER)


# Route to render the identifyPiecePage.html
@app.route("/identifyPiece")
async def identify_piece(request):
    file_path = os.path.join(UI_FOLDER, "identifyPiecePage.html")
    return await file(file_path)


# Handle multiple image uploads and form data
@app.route("/upload", methods=["POST"])
async def handle_upload(request):
    if not request.files:
        return sanic_json({"error": "No files uploaded"}, status=400)

    uploaded_files = request.files.getlist('file')
    gemUploadedFiles = []

    for uploaded_file in uploaded_files:
        # Read the file data
        image_data = uploaded_file.body
        # Create a BytesIO object
        image_io = io.BytesIO(image_data)

        # Get the MIME type
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)

        # Reset the stream position to the beginning


        # Upload the file with the MIME type
        gemUploadedFiles.append( genai.upload_file(image_io, mime_type=mime_type))

    # Get the form data (brand and gender)
    brand = request.form.get('brand')
    gender = request.form.get('gender')

    # Create a mock description
    description = f"The uploaded images are analyzed as {gender} wear from the brand {brand}."

    model = genai.GenerativeModel("gemini-1.5-pro")
    result = model.generate_content(
        [*gemUploadedFiles, "\n\n", f"""I will provide you with multiple images of a piece of clothing and you must return a title and a description for this piece.
    Your response must be in the format of a JSON file with the parameters of "title" and "description".
    The title should be one brief sentence that describes the piece very briefly while including the brand and the gender (men or women) of the item.
    The description, on the other hand, should consist of 3 short-to-medium sentences that describes the item and shows the attributes and qualities of the item while maintaining engaging, persuasive and attractive tone.
    The brand of the item in this image is  "{brand}" and it's for {gender}."""])

    start = result.text.find('{')
    end = result.text.find('}')
    extracted_string = result.text[start:end + 1]

    # Use the standard json module to load the string into a dictionary
    data = json.loads(extracted_string)

    title, description = data['title'], data['description']
    print(title)
    print(description)
    # Return the JSON response with the description and image URLs using Sanic's json response
    return sanic_json({
        "title": title,
        "description": description

    })


# Run the Sanic app
if __name__ == "__main__":
    app.run(host="192.168.1.66", port=8080)
# myfile = genai.upload_file( "m.jpg")
# #print(f"{myfile=}")
# #
# # model = genai.GenerativeModel("gemini-1.5-pro")
# # result = model.generate_content(
# #     [myfile, "\n\n", """I will provide you with multiple images of a piece of clothing and you must return a title and a description for this piece.
# # Your response must be in the format of a JSON file with the parameters of "title" and "description".
# # The title should be one brief sentence that describes the piece very briefly while including the brand and the gender (men or women) of the item.
# # The description, on the other hand, should consist of 3 sentences that describes the item and shows the attributes and qualities of the item while maintaining persuasive and attractive tone.
# # The brand of the item in this image is "Armani" and it's for "women"."""]
# # )
# # print(f"{result.text=}")