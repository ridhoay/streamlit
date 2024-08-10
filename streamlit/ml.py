import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.preprocessing import StandardScaler



st.title("Simple Data Dashboard")

uploaded_file = st.file_uploader("a csv file", type="csv")

if uploaded_file is not None:
    # Output the dataframe
    df = pd.read_csv(uploaded_file)
    st.write(df)
    
    # Show data summary
    st.subheader("Data summary")
    st.dataframe(df.describe())
    
    # Filter data
    if 'filter_button_pressed' not in st.session_state:
        st.session_state.filter_button_pressed = False
    
    if st.button("Filter Data"):
        st.session_state.filter_button_pressed = True
    
    if st.session_state.filter_button_pressed:
        st.subheader("Filter Data")
        columns = df.columns.tolist()
        selected_column = st.selectbox("Select column to filter by", columns)
        unique_values = df[selected_column].unique()
        selected_value = st.selectbox("Select value", unique_values)
        filtered_df = df[df[selected_column] == selected_value]
        st.write(filtered_df)

    # Plot data
    if st.button("Plot Data"):
        st.subheader("Plot Data")
        x_column = st.selectbox("Select x column", columns)
        y_column = st.selectbox("Select y column", columns)
        
        if st.button("Generate Plot"):
            fig, ax = plt.subplots()
            ax.plot(df[x_column], df[y_column])
            st.pyplot(fig)
            st.line_chart(filtered_df.set_index(x_column)[y_column])

    # Input Parameters
    st.subheader("Input Parameters")
    machine_types = ["M", "L", "H"]
    machine_type = st.selectbox("Machine Type", machine_types)
    machine_type_value = machine_types.index(machine_type)    
    air_temp = st.select_slider(
        "Air temperature (K)",
        options=[i / 10.0 for i in range(2800, 3111, 1)],
        value=280.0,
    )
    process_temp = st.select_slider(
        "Process temperature (K)",
        options=[i / 10.0 for i in range(3000, 3151, 1)],
        value=300.0,
    )
    rot_speed = st.select_slider(
        "Rotational Speed (rpm)",
        options=[i for i in range(1000, 3001, 1)],
        value=1000.0,
    )
    torque = st.select_slider(
        "Torque (Nm)",
        options=[i / 10.0 for i in range(350, 801, 1)],
        value=35.0,
    )
    tool_wear = st.select_slider(
        "Tool Wear (min)",
        options=[i for i in range(0, 301, 1)],
        value=0,
    )
    twf = st.selectbox("twf", [0,1])
    hdf = st.selectbox("hdf", [0,1])
    pwf = st.selectbox("pwf", [0,1])
    osf = st.selectbox("osf", [0,1])
    rnf = st.selectbox("rnf", [0,1])
        
    def predict_machine_failure(rf_model, scaler, parameters):
        """
        Predict if a machine will fail based on input parameters.
        
        :param rf_model: Trained Random Forest model
        :param scaler: Fitted StandardScaler
        :param parameters: List of parameter values for a single case
        :return: Prediction (0 for no failure, 1 for failure) and probability of failure
        """
        # Convert input parameters to a 2D numpy array (required for sklearn)
        input_data = np.array(parameters).reshape(1, -1)
        
        # Scale the input parameters
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction = rf_model.predict(input_scaled)
        probability = rf_model.predict_proba(input_scaled)[0][1]  # Probability of failure
        
        return prediction[0], probability

    # Example usage:
    rf_model = joblib.load('streamlit\rf_model.joblib')
    scaler = StandardScaler()
    parameters = [
        machine_type_value, 
        air_temp, 
        process_temp, 
        rot_speed, 
        torque, 
        tool_wear, 
        twf, 
        hdf, 
        pwf, 
        osf, 
        rnf
    ] 
    
    prediction, probability = predict_machine_failure(rf_model, scaler, parameters)
    # print(f"Prediction: {'Failure' if prediction == 1 else 'No Failure'}")
    # print(f"Probability of Failure: {probability:.2f}")
    if prediction == 0: 
        st.success('Machine Survived :thumbsup:')
    else: 
        st.error('Machine did not Survive :thumbsdown:') 

else:
    st.write("Waiting for file upload...")