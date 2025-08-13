import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO, BytesIO
import base64
import os
import sys
import asyncio
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import AutoAnalyst
import config

st.set_page_config(
    page_title="AutoAnalyst - AI Data Science Consultant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🤖 AutoAnalyst - AI Data Science Consultant")
    st.markdown("Upload your dataset and let AI agents perform comprehensive analysis")
    
    with st.sidebar:
        st.header("Configuration")
        
        use_autogen = st.checkbox("Enable AutoGen Integration", value=False)
        interactive_mode = st.checkbox("Interactive Mode", value=False)
        
        st.header("Analysis Options")
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Full Analysis", "Quick Summary", "Custom Analysis"]
        )
        
        if analysis_type == "Custom Analysis":
            custom_objectives = st.text_area(
                "Custom Objectives",
                placeholder="Describe what you want to analyze..."
            )
    
    tab1, tab2, tab3, tab4 = st.tabs(["Data Upload", "Analysis Results", "Visualizations", "Reports"])
    
    with tab1:
        st.header("Upload Dataset")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file for analysis"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"Dataset uploaded successfully! Shape: {df.shape}")
                
                st.subheader("Dataset Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                st.subheader("Dataset Info")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Rows", df.shape[0])
                with col2:
                    st.metric("Columns", df.shape[1])
                with col3:
                    st.metric("Missing Values", df.isnull().sum().sum())
                
                if st.button("Start Analysis", type="primary"):
                    with st.spinner("Running AI analysis..."):
                        save_path = f"datasets/uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        df.to_csv(save_path, index=False)
                        
                        try:
                            analyst = AutoAnalyst()
                            
                            if use_autogen:
                                from autogen_integration import enhance_autoanalyst_with_autogen
                                analyst = enhance_autoanalyst_with_autogen(analyst)
                            
                            result = analyst.analyze_dataset(
                                save_path,
                                use_autogen=use_autogen,
                                interactive=interactive_mode
                            )
                            
                            st.session_state['analysis_result'] = result
                            st.session_state['dataset'] = df
                            st.success("Analysis completed!")
                            
                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")
                            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with tab2:
        st.header("Analysis Results")
        
        if 'analysis_result' in st.session_state:
            result = st.session_state['analysis_result']
            
            st.subheader("Summary")
            if hasattr(result, 'summary'):
                st.write(result.summary)
            
            st.subheader("Key Insights")
            if hasattr(result, 'insights'):
                for insight in result.insights:
                    st.info(insight)
            
            st.subheader("Recommendations")
            if hasattr(result, 'recommendations'):
                for rec in result.recommendations:
                    st.success(rec)
        else:
            st.info("Upload a dataset and run analysis to see results here.")
    
    with tab3:
        st.header("Visualizations")
        
        if 'dataset' in st.session_state:
            df = st.session_state['dataset']
            
            st.subheader("Quick Visualizations")
            
            viz_type = st.selectbox(
                "Select Visualization Type",
                ["Correlation Heatmap", "Distribution Plot", "Scatter Plot", "Box Plot"]
            )
            
            if viz_type == "Correlation Heatmap":
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 1:
                    corr_matrix = df[numeric_cols].corr()
                    fig = px.imshow(
                        corr_matrix,
                        title="Correlation Heatmap",
                        color_continuous_scale="RdBu"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Need at least 2 numeric columns for correlation heatmap")
            
            elif viz_type == "Distribution Plot":
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    selected_col = st.selectbox("Select Column", numeric_cols)
                    fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}")
                    st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Scatter Plot":
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        x_col = st.selectbox("X-axis", numeric_cols)
                    with col2:
                        y_col = st.selectbox("Y-axis", numeric_cols)
                    
                    if x_col != y_col:
                        fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                        st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Box Plot":
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    selected_col = st.selectbox("Select Column", numeric_cols)
                    fig = px.box(df, y=selected_col, title=f"Box Plot of {selected_col}")
                    st.plotly_chart(fig, use_container_width=True)
            
            if os.path.exists("visuals"):
                st.subheader("Generated Visualizations")
                for filename in os.listdir("visuals"):
                    if filename.endswith(('.png', '.jpg', '.jpeg')):
                        st.image(f"visuals/{filename}", caption=filename)
        else:
            st.info("Upload a dataset to create visualizations.")
    
    with tab4:
        st.header("Reports")
        
        if 'analysis_result' in st.session_state:
            st.subheader("Download Reports")
            
            if os.path.exists("reports"):
                for filename in os.listdir("reports"):
                    if filename.endswith('.pdf'):
                        with open(f"reports/{filename}", "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                            st.download_button(
                                label=f"Download {filename}",
                                data=pdf_bytes,
                                file_name=filename,
                                mime="application/pdf"
                            )
            
            st.subheader("Email Report")
            email = st.text_input("Email Address")
            if st.button("Send Report via Email") and email:
                try:
                    from email_service import send_analysis_report
                    send_analysis_report(email, "reports/")
                    st.success("Report sent successfully!")
                except Exception as e:
                    st.error(f"Failed to send email: {str(e)}")
        else:
            st.info("Complete an analysis to generate reports.")

if __name__ == "__main__":
    main()