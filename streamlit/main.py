import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.title("Simple Data Dashboard")

uploaded_file = st.file_uploader("Choose a csv file", type="csv")

if uploaded_file is not None:
    # Output the dataframe
    df = pd.read_csv(uploaded_file)
    st.write(df)
    
    # Show data summary
    st.subheader("Data summary")
    st.dataframe(df.describe())

    # Filter data
    st.subheader("Filter Data")
    columns = df.columns.tolist()
    selected_column = st.selectbox("Select column to filter by", columns)
    unique_values = df[selected_column].unique()
    selected_value = st.selectbox("Select value", unique_values)
    filtered_df = df[df[selected_column] == selected_value]
    st.write(filtered_df)

    # Plot data
    st.subheader("Plot Data")
    x_column = st.selectbox("Select x column", columns)
    y_column = st.selectbox("Select y column", columns)
    
    if st.button("Generate Plot"):
        fig, ax = plt.subplots()
        ax.plot(df[x_column], df[y_column])
        st.pyplot(fig)
        # st.line_chart(filtered_df.set_index(x_column)[y_column])
        

else:
    st.write("Waiting for file upload...")