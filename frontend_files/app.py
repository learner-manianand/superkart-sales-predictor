
import streamlit as st
import requests
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="SuperKart Sales Predictor",
    page_icon=":shopping_trolley:",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Header
st.title("🛒 SuperKart Sales Predictor")
st.markdown("Predict sales for SuperKart products based on various features.")

# Set the backend URL (This will be dynamically set in a deployed environment)
# For local testing, ensure your Flask app is running on http://127.0.0.1:7860
BACKEND_URL = "http://backend:7860" # 'backend' is the service name in docker-compose

# --- Sidebar for Navigation --- #
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Single Prediction", "Batch Prediction"])


# --- Single Prediction Page --- #
if page == "Single Prediction":
    st.header("Single Product Sales Prediction")
    st.markdown("Enter the details for a single product to get an instant sales prediction.")

    with st.form("single_prediction_form"):
        st.subheader("Product Details")
        col1, col2 = st.columns(2)
        product_weight = col1.number_input("Product Weight", min_value=0.0, value=12.66)
        product_mrp = col2.number_input("Product MRP", min_value=0.0, value=117.08)
        product_allocated_area = col1.number_input("Product Allocated Area", min_value=0.0, value=0.027)

        st.subheader("Product Characteristics")
        product_id_char = col1.selectbox("Product ID Characteristic", ['FD', 'NC', 'DR'], index=0)
        product_sugar_content = col2.selectbox("Product Sugar Content", ['Low Sugar', 'Regular', 'No Sugar'], index=0)
        product_type = col1.selectbox("Product Type", ['Frozen Foods', 'Dairy', 'Canned', 'Baking Goods', 'Health and Hygiene', 'Snack Foods', 'Meat', 'Household', 'Hard Drinks', 'Fruits and Vegetables', 'Breads', 'Soft Drinks', 'Breakfast', 'Others', 'Seafood', 'Starchy Foods'], index=0)
        product_type_category = col2.selectbox("Product Type Category", ['Non Perishable', 'Perishable'], index=0)

        st.subheader("Store Details")
        store_id = col1.selectbox("Store ID", ['OUT004', 'OUT003', 'OUT001', 'OUT002', 'OUT010', 'OUT013', 'OUT046', 'OUT018', 'OUT049', 'OUT045', 'OUT019', 'OUT035', 'OUT017', 'OUT027', 'OUT008'], index=0)
        store_establishment_year = col2.number_input("Store Establishment Year", min_value=1900, max_value=2023, value=2009)
        store_size = col1.selectbox("Store Size", ['Medium', 'High', 'Small'], index=0)
        store_location_city_type = col2.selectbox("Store Location City Type", ['Tier 2', 'Tier 1', 'Tier 3'], index=0)
        store_type = col1.selectbox("Store Type", ['Supermarket Type2', 'Departmental Store', 'Supermarket Type1', 'Food Mart'], index=0)
        store_age_years = col2.number_input("Store Age Years", min_value=0, value=15)

        submitted = st.form_submit_button("Predict Sales")

        if submitted:
            # Construct payload for API
            payload = {
                "Product_Weight": product_weight,
                "Product_Sugar_Content": product_sugar_content,
                "Product_Allocated_Area": product_allocated_area,
                "Product_Type": product_type,
                "Product_MRP": product_mrp,
                "Store_Id": store_id,
                "Store_Establishment_Year": store_establishment_year,
                "Store_Size": store_size,
                "Store_Location_City_Type": store_location_city_type,
                "Store_Type": store_type,
                "Store_Age_Years": store_age_years,
                "Product_Id_char": product_id_char,
                "Product_Type_Category": product_type_category
            }
            
            try:
                response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload)
                if response.status_code == 200:
                    prediction = response.json().get("prediction")
                    st.success(f"Predicted Product Store Sales Total: ${prediction:,.2f}")
                else:
                    st.error(f"Error making prediction: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend API. Please ensure it is running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")


# --- Batch Prediction Page --- #
elif page == "Batch Prediction":
    st.header("Batch Product Sales Prediction")
    st.markdown("Upload a CSV file containing multiple product entries to get batch sales predictions.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read the uploaded CSV file into a pandas DataFrame
        data_df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Preview:")
        st.dataframe(data_df.head())

        if st.button("Get Batch Predictions"):
            try:
                # Send the DataFrame as a file in the request
                files = {'file': data_df.to_csv(index=False).encode('utf-8')}
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files)

                if response.status_code == 200:
                    predictions = response.json().get("predictions")
                    if predictions:
                        results_df = pd.DataFrame({'Predicted_Sales': predictions})
                        st.success("Batch predictions successful!")
                        st.write("Predictions:")
                        st.dataframe(results_df)
                        
                        # Option to download predictions
                        csv = results_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Predictions as CSV",
                            data=csv,
                            file_name="batch_predictions.csv",
                            mime="text/csv",
                        )
                    else:
                        st.warning("No predictions received from the backend.")
                else:
                    st.error(f"Error making batch prediction: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend API. Please ensure it is running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
