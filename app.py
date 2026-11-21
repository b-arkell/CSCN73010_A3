"""Flask web app that predicts hand-sign digits from uploaded images."""
# Importing required libs
from flask import Flask, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge
from model import preprocess_img, predict_result

# Instantiating flask app
app = Flask(__name__)
# Reject uploads larger than 5 MB before they are read into memory
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Home route
@app.route("/")
def main():
    """Render the image upload page."""
    return render_template("index.html")


# Prediction route
@app.route('/prediction', methods=['POST'])
def predict_image_file():
    """Preprocess the uploaded image and render the predicted digit."""
    try:
        img = preprocess_img(request.files['file'].stream)
        pred = predict_result(img)
        return render_template("result.html", predictions=str(pred))

    except (KeyError, OSError, ValueError):
        error = "File cannot be processed."
        return render_template("result.html", err=error)

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(_error):
    """Show a friendly error when the upload exceeds MAX_CONTENT_LENGTH."""
    return render_template("result.html", err="File is too large (max 5 MB)."), 413

# Driver code
if __name__ == "__main__":
    app.run(port=9000, debug=True)
