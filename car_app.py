import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# Page configuration
st.set_page_config(page_title="Car Price Predictor", page_icon="🚗")

@st.cache_resource
def train_model():
    # Load dataset
    df_real = pd.read_csv('ford.csv')

    # Drop duplicates as per notebook
    df = df_real.drop_duplicates()

    # Preprocessing: One-hot encoding
    # Note: drop_first=True is used in the notebook
    df_encoded = pd.get_dummies(df, drop_first=True)

    # Define numeric columns for scaling
    numeric_cols = ['engineSize', 'mpg', 'tax', 'mileage', 'year']

    # Standard Scaler
    scaler = StandardScaler()
    df_encoded[numeric_cols] = scaler.fit_transform(df_encoded[numeric_cols])

    # Feature Selection (as per the 'all' list in notebook)
    all_features = [
        'year', 'mileage', 'tax', 'mpg', 'engineSize', 'model_ C-MAX',
        'model_ EcoSport', 'model_ Edge', 'model_ Escort', 'model_ Fiesta',
        'model_ Focus', 'model_ Fusion', 'model_ Galaxy', 'model_ Grand C-MAX',
        'model_ Grand Tourneo Connect', 'model_ KA', 'model_ Ka+',
        'model_ Kuga', 'model_ Mondeo', 'model_ Mustang', 'model_ Puma',
        'model_ Ranger', 'model_ S-MAX', 'model_ Streetka',
        'model_ Tourneo Connect', 'model_ Tourneo Custom',
        'transmission_Manual', 'transmission_Semi-Auto', 'fuelType_Petrol'
    ]

    # Ensure all requested features exist in the encoded dataframe
    # Some categories might be missing if the dataset is small, though unlikely here
    for col in all_features:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    X = df_encoded[all_features]
    y = df_encoded['price']

    # Train Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    return model, scaler, all_features, df_real

# Load model and assets
try:
    model, scaler, feature_cols, original_df = train_model()
except Exception as e:
    st.error(f"Error loading data or training model: {e}")
    st.stop()

st.title("🚗 Car Price Prediction")
st.write("Predict the price of a Ford car based on its specifications.")

# User input section
with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        # Get unique values for dropdowns from the original dataset
        model_list = sorted(original_df['model'].unique())
        selected_model = st.selectbox("Car Model", model_list)

        year = st.number_input("Year", min_value=1900, max_value=2026, value=2018)
        mileage = st.number_input("Mileage", min_value=0, value=10000)
        tax = st.number_input("Tax", min_value=0, value=150)

    with col2:
        mpg = st.number_input("MPG", min_value=0.0, value=50.0)
        engine_size = st.number_input("Engine Size", min_value=0.0, value=1.0)

        trans_list = sorted(original_df['transmission'].unique())
        transmission = st.selectbox("Transmission", trans_list)

        fuel_list = sorted(original_df['fuelType'].unique())
        fuel_type = st.selectbox("Fuel Type", fuel_list)

    submit = st.form_submit_button("Predict Price")

if submit:
    # Create a dataframe for the input
    input_data = pd.DataFrame({
        'model': [selected_model],
        'year': [year],
        'mileage': [mileage],
        'tax': [tax],
        'mpg': [mpg],
        'engineSize': [engine_size],
        'transmission': [transmission],
        'fuelType': [fuel_type]
    })

    # 1. One-hot encoding the input
    input_encoded = pd.get_dummies(input_data)

    # 2. Align with training features
    # We must ensure the input has exactly the same columns as the training set
    final_input = pd.DataFrame(0, index=[0], columns=feature_cols)

    # Map inputs to encoded columns
    # model_...
    model_col = f"model_{selected_model}"
    if model_col in feature_cols:
        final_input[model_col] = 1

    # transmission_...
    # Notebook used drop_first=True, so we only set 1 for Manual/Semi-Auto
    if transmission == 'Manual':
        if 'transmission_Manual' in feature_cols:
            final_input['transmission_Manual'] = 1
    elif transmission == 'Semi-Auto':
        if 'transmission_Semi-Auto' in feature_cols:
            final_input['transmission_Semi-Auto'] = 1

    # fuelType_...
    if fuel_type == 'Petrol':
        if 'fuelType_Petrol' in feature_cols:
            final_input['fuelType_Petrol'] = 1

    # 3. Scale numeric features
    numeric_cols = ['year', 'mileage', 'tax', 'mpg', 'engineSize']
    # Note: The order of columns passed to the scaler must match the order it was fit on
    # Notebook fit order: ['engineSize','mpg','tax','mileage','year']
    scaler_cols = ['engineSize', 'mpg', 'tax', 'mileage', 'year']

    # Get current values from user input
    current_vals = np.array([[engine_size, mpg, tax, mileage, year]])
    scaled_vals = scaler.transform(current_vals)[0]

    # Put scaled values back into final_input
    final_input['engineSize'] = scaled_vals[0]
    final_input['mpg'] = scaled_vals[1]
    final_input['tax'] = scaled_vals[2]
    final_input['mileage'] = scaled_vals[3]
    final_input['year'] = scaled_vals[4]

    # 4. Prediction
    prediction = model.predict(final_input[feature_cols])[0]

    st.success(f"### Estimated Price: £{prediction:,.2f}")
