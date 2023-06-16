# Importing required libs
from flask import Flask, render_template, request, jsonify
from model import preprocess_img, predict_result
from flask_cors import CORS
import csv

# Instantiating flask app
app = Flask(__name__)
CORS(app)

# Home route
@app.route("/")
def main():
    return render_template("index.html")

# Prediction route
@app.route('/prediction', methods=['POST', 'GET'])
def predict_image_file():
    try:
        if request.method == 'POST':
            img = preprocess_img(request.files['file'].stream)

            waste_classes = ["Sampah Organik", "Sampah Plastik", "Sampah Kayu", "Sampah Besi", "Non Recycle"]
            pred = predict_result(img)
            results = waste_classes[pred]

            search_string = ["Pembuangan Sampah Organik",  "Sampah Plastik", "Sampah Kayu", "Sampah Besi", "Pembuangan Sampah Anorganik"]
            search = search_string[pred]
            with open('index.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([results])
                writer.writerow([search])

            
            return render_template("result.html", predictions=results, search=search)
        
        if request.method == 'GET':       
            with open('index.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    pred_akhir = row
                    search_akhir = row   
            return render_template("result.html", predictions=pred_akhir, search=search_akhir)

    except:
        error = "Mohon Masukan Gambar Terlebih Dahulu"
        return render_template("result.html", err=error)


# maps route
@app.route('/maps')
def maps():
    with open('index.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            search_akhir = row
    return render_template("maps.html", search=search_akhir)

# Driver code
if __name__ == "__main__":
    app.run(port=9000, debug=True)

