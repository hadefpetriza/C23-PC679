# Importing required libs
from flask import Flask, render_template, request, jsonify
from model import preprocess_img, predict_result
from flask_cors import CORS

# Instantiating flask app
app = Flask(__name__)
CORS(app)

# Home route
@app.route("/")
def main():
    return render_template("index.html")

# Prediction route
@app.route('/prediction', methods=['POST'])
def predict_image_file():
    try:
        if request.method == 'POST':
            img = preprocess_img(request.files['file'].stream)

            waste_classes = ["Organik", "Plastic Recycle", "Kayu Recycle", "Besi Recycle", "Non Recycle"]
            pred = predict_result(img)
            results = waste_classes[pred]

            search_string = ["pembuangan sampah Organik", "recycle Plastik", "recycle wood", "recycle scrap", "pembuangan sampah anorganik"]
            search = search_string[pred]

            
            return render_template("result.html", predictions=results, search=search)

    except:
        error = "File cannot be processed."
        return render_template("result.html", err=error)

# Driver code
if __name__ == "__main__":
    app.run(port=9000, debug=True)

