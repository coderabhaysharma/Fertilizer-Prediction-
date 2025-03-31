from flask import Flask, request, render_template
import pickle

app = Flask(__name__)

# Load trained model
model = pickle.load(open('classifier.pkl', 'rb'))

# Load fertilizer encoder (if needed)
try:
    ferti = pickle.load(open('fertilizer.pkl', 'rb'))
except:
    ferti = None  # If not needed, ignore

# Define valid categories for encoding
soil_types = ['Clayey', 'Loamy', 'Black', 'Red']
crop_types = ['Rice', 'Wheat', 'Tobacco', 'Sugarcane', 'Pulses', 'Pomegranate', 'Paddy', 'Oil seeds', 'Millets']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Fetch input data and handle missing values
        temp = request.form.get('temp')
        humi = request.form.get('humi')
        mois = request.form.get('mois')
        soil = request.form.get('soil')
        crop = request.form.get('crop')
        nitro = request.form.get('nitro')
        pota = request.form.get('pota')
        phosp = request.form.get('phosp')

        # Ensure all fields are filled
        if None in (temp, humi, mois, soil, crop, nitro, pota, phosp):
            return render_template('index.html', result="⚠️ All fields are required!")

        # Convert numeric inputs
        try:
            temp = int(temp)
            humi = int(humi)
            mois = int(mois)
            nitro = int(nitro)
            pota = int(pota)
            phosp = int(phosp)
        except ValueError:
            return render_template('index.html', result="⚠️ Enter valid numeric values!")

        # Validate categorical values
        if soil not in soil_types or crop not in crop_types:
            return render_template('index.html', result="⚠️ Invalid Soil or Crop Type!")

        # Encode categorical variables
        soil_encoded = soil_types.index(soil)
        crop_encoded = crop_types.index(crop)

        # Create input array
        input_data = [[temp, humi, mois, soil_encoded, crop_encoded, nitro, pota, phosp]]

        # Predict fertilizer
        prediction_index = model.predict(input_data)[0]

        # Convert prediction to fertilizer name
        prediction_label = ferti.classes_[prediction_index] if ferti else prediction_index

        return render_template('index.html', result=f'✅ Predicted Fertilizer: {prediction_label}')

    except Exception as e:
        return render_template('index.html', result=f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT is not set
    app.run(host="0.0.0.0", port=port, debug=True)
