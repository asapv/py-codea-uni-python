import streamlit as st
import pandas as pd

def calculate_cutoff_grade(mining_cost, processing_cost, mineral_price, refining_cost, metallurgical_recovery):
    """Calculate Cut-Off Grade using Kenneth Lane's method."""
    recovery_decimal = metallurgical_recovery / 100
    denominator = (mineral_price - refining_cost) * recovery_decimal
    if denominator <= 0:
        st.error("Mineral price adjusted by refining and recovery must be greater than 0.")
        return None
    return ((mining_cost + processing_cost) / denominator) * 100

def decide_block_action(block_grade, cutoff_grade, stock_threshold):
    """Decide if a block should be processed, sent to stock, or discarded."""
    stock_limit = cutoff_grade * stock_threshold
    if block_grade >= cutoff_grade:
        return "Process"
    elif block_grade >= stock_limit:
        return "Send to Stock"
    else:
        return "Discard"

# Initialize session state to store results
if 'results' not in st.session_state:
    st.session_state.results = []

# Page configuration
st.set_page_config(page_title="Cut-Off Grade Calculator", layout="wide")
st.title("Cut-Off Grade Calculator")

# Create columns for layout
col1, col2 = st.columns([1, 1])

# Input parameters in the first column
with col1:
    st.subheader("Input Data")
    with st.form("input_form"):
        mining_cost = st.number_input("Mining Cost ($/ton):", min_value=0.01, value=20.0, format="%.2f", key="mining_cost")
        processing_cost = st.number_input("Processing Cost ($/ton):", min_value=0.01, value=30.0, format="%.2f", key="processing_cost")
        mineral_price = st.number_input("Mineral Price ($/ton):", min_value=0.01, value=6000.0, format="%.2f", key="mineral_price")
        refining_cost = st.number_input("Refining Cost ($/ton):", min_value=0.0, value=500.0, format="%.2f", key="refining_cost")
        recovery = st.number_input("Metallurgical Recovery (%):", min_value=0.1, max_value=100.0, value=85.0, format="%.1f", key="recovery")
        stock_threshold = st.number_input("Stock Threshold (0-1):", min_value=0.0, max_value=1.0, value=0.7, format="%.2f", key="stock_threshold")
        
        # Block grades input
        block_grade_input = st.text_input("Block Grades (%):", 
                                         help="Enter grades separated by commas (e.g., '1.2, 3.4, 5.6')", key="block_grade_input")
        
        # Buttons
        col_submit, col_clear = st.columns(2)
        with col_submit:
            submitted = st.form_submit_button("Calculate")
        with col_clear:
            cleared = st.form_submit_button("Clear")

# Results in the second column
with col2:
    st.subheader("Results")
    
    if cleared:
        # Reset all inputs and results
        st.session_state.results = []
        for key in ["mining_cost", "processing_cost", "mineral_price", "refining_cost", "recovery", "stock_threshold", "block_grade_input"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()
    
    if submitted:
        # Calculate cut-off grade
        cutoff_grade = calculate_cutoff_grade(mining_cost, processing_cost, mineral_price, refining_cost, recovery)
        
        if cutoff_grade is not None:
            st.success(f"**Cut-Off Grade: {cutoff_grade:.2f}%**")
            
            # Process block grades
            try:
                if block_grade_input:
                    block_grades = [float(grade.strip()) for grade in block_grade_input.split(',')]
                    
                    # Append new results
                    for grade in block_grades:
                        action = decide_block_action(grade, cutoff_grade, stock_threshold)
                        st.session_state.results.append({"Block Grade (%)": f"{grade:.2f}", "Action": action})
                    
                    # Clear block grade input for new entries
                    st.session_state.block_grade_input = ""
            
            except ValueError:
                st.error("Invalid grade format. Use numbers separated by commas.")
    
    # Display results if available
    if st.session_state.results:
        # Show block analysis table
        st.subheader("Block Analysis")
        df = pd.DataFrame(st.session_state.results)
        st.dataframe(df, use_container_width=True)
        
        # Show summary
        processed = sum(1 for r in st.session_state.results if r["Action"] == "Process")
        stocked = sum(1 for r in st.session_state.results if r["Action"] == "Send to Stock")
        discarded = sum(1 for r in st.session_state.results if r["Action"] == "Discard")
        
        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Processed", processed)
        col2.metric("Sent to Stock", stocked)
        col3.metric("Discarded", discarded)
