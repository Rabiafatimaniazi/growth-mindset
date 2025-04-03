import streamlit as st
import pandas as pd
import os
from io import BytesIO
from typing import Union

st.set_page_config(page_title="Data Sweeper", page_icon=":bar_chart:", layout="wide")

st.title("Data Sweeper :bar_chart:")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning & visualization!")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel)", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        DFType = Union[pd.DataFrame, None]


        try:
            if file_ext == ".csv":
                # First try reading with default utf-8 encoding
                df: DFType = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file format: {file_ext}")
                continue
        except UnicodeDecodeError:
            # Handle CSV encoding issues by trying alternative encodings
            if file_ext == ".csv":
                encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-8-sig']
                df = None
                success_encoding = None
                for encoding in encodings:
                    try:
                        file.seek(0)  # Reset file pointer to the beginning
                        df = pd.read_csv(file, encoding=encoding)
                        success_encoding = encoding
                        break
                    except Exception as e:
                        continue

                if df is not None:
                    st.success(f"Successfully read {file.name} with encoding: {success_encoding}")
                else:
                    st.error(f"Could not read {file.name} with any of the tried encodings.")
                    continue
            else:
                st.error(f"Error reading file {file.name}")
                continue
        except Exception as e:
            st.error(f"Error reading file {file.name}: {e}")
            continue

        # Proceed with data processing and visualization here
        st.write(f"**File Name**: {file.name}") 
        st.write(f"**File Size**: {file.size/1024}")

        # show first 5 rows of the dataframe
        if isinstance(df, pd.DataFrame):
            st.write("Preview the head of the Dataframe")
            st.dataframe(df.head())


            # Options for data cleaning
            st.subheader("🛠️ Data Cleaning Options")  
            
            if st.checkbox(f"Clean Data for {file.name}"):
                
                #  Creating two columns for data cleaning options
                col1, col2 = st.columns(2);

                with col1: 
                    if st.button(f"Remove duplicates from {file.name}"):
                        df.drop_duplicates(inplace=True)
                        st.write("Duplicates Removed!")

                with col2:
                    if st.button(f"Fill Missing Values for {file.name}"):
                        numeric_cols = df.select_dtypes(include=["number"]).columns
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.write("Missing values have been filled!")


            # Choose specific columns to keep or convert
            st.subheader("📂 Select Columns to Keep or Convert")  

            columns = st.multiselect(f"Select columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            # Convert column names to strings to prevent encoding issues
            df.columns = df.columns.astype(str)

            # Creating Some Visualizations
            st.subheader("📉 Data Visualization")  
            numeric_cols = df.select_dtypes(include="number").columns
            
            if len(numeric_cols) == 0:
                st.warning("Data must have numeric columns in order to visualize")
            else:
                if st.checkbox(f"Show visualization for {file.name}"):
                    # Ensure we have at least 2 columns for the first chart
                    if len(numeric_cols) >= 2:
                        st.bar_chart(df[numeric_cols[:2]])
                    else:
                        st.bar_chart(df[numeric_cols[0]])
                    
                    st.line_chart(df[numeric_cols])
                    st.area_chart(df[numeric_cols])

            # Convert the file -> Excel to CSV or vice versa
            st.subheader("🔃 Conversion Options")  
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"conversion_{file.name}")

            if st.button("Convert"):
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"  # Corrected typo

                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False)
                    file_name = file.name.replace(file_ext, "xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" 
                
                buffer.seek(0)

                # Download Button
                st.download_button(
                    label=f"Download {file.name} as {conversion_type} ↓",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type 
                )