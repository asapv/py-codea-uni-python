import streamlit as st
import pandas as pd

def calculate_cutoff_grade(mining_cost: float, processing_cost: float, mineral_price: float, refining_cost: float,
                          metallurgical_recovery: float) -> float:
    """Calculate Cut-Off Grade using Kenneth Lane's method."""
    recovery_decimal = metallurgical_recovery / 100
    denominator = (mineral_price - refining_cost) * recovery_decimal
    if denominator <= 0:
        st.error("Mineral price adjusted by refining and recovery must be greater than 0.")
        return None
    return ((mining_cost + processing_cost) / denominator) * 100

def decide_block_action(block_grade: float, cutoff_grade: float, stock_threshold: float) -> str:
    """Decide if a block should be processed, sent to stock, or discarded."""
    stock_limit = cutoff_grade * stock_threshold
    if block_grade >= cutoff_grade:
        return "Process"
    elif block_grade >= stock_limit:
        return "Send to Stock"
    else:
        return "Discard"

def validate_input(value: str, field_name: str, max_value: float = None, is_threshold: bool = False, is_recovery: bool = False) -> float:
    """Validate that input is a positive number and within acceptable range."""
    try:
        num = float(value)
        if num <= 0:
            st.error(f"{field_name} must be greater than 0.")
            return None
        if is_threshold and (num < 0 or num > 1):
            st.error("Stock Threshold must be between 0 and 1.")
            return None
        if is_recovery and (num < 0 or num > 100):
            st.error("Metallurgical Recovery must be between 0 and 100%.")
            return None
        if max_value is not None and num > max_value:
            st.error(f"{field_name} cannot be greater than {max_value}.")
            return None
        return num
    except ValueError:
        st.error(f"{field_name} must be a valid number.")
        return None

# Initialize session state
if 'block_grades' not in st.session_state:
    st.session_state.block_grades = []
if 'results' not in st.session_state:
    st.session_state.results = []
if 'block_grade_key' not in st.session_state:
    st.session_state.block_grade_key = 0

# Page configuration
st.set_page_config(page_title="Cut-Off Grade Calculator", layout="wide")
st.title("Cut-Off Grade Calculator")

# Create columns for layout
col1, col2 = st.columns([1, 1])

# Input form in the first column
with col1:
    st.subheader("Input Data")
    with st.form("input_form"):
        mining_cost = st.number_input("Mining Cost ($/ton):", min_value=0.01, value=20.0, format="%.2f", key="mining_cost")
        processing_cost = st.number_input("Processing Cost ($/ton):", min_value=0.01, value=30.0, format="%.2f", key="processing_cost")
        mineral_price = st.number_input("Mineral Price ($/ton):", min_value=0.01, value=6000.0, format="%.2f", key="mineral_price")
        refining_cost = st.number_input("Refining Cost ($/ton):", min_value=0.0, value=500.0, format="%.2f", key="refining_cost")
        recovery = st.number_input("Metallurgical Recovery (%):", min_value=0.1, max_value=100.0, value=85.0, format="%.1f", key="recovery")
        stock_threshold = st.number_input("Stock Threshold (0-1):", min_value=0.0, max_value=1.0, value=0.7, format="%.2f", key="stock_threshold")
        
        block_grade = st.text_input("Block Grade (%):", help="Enter a single block grade (e.g., 1.2)", key=f"block_grade_{st.session_state.block_grade_key}")
        
        col_add, col_calc, col_clear = st.columns(3)
        with col_add:
            add_block = st.form_submit_button("Add Block")
        with col_calc:
            calculate = st.form_submit_button("Calculate")
        with col_clear:
            clear = st.form_submit_button("Clear")

# Results in the second column
with col2:
    st.subheader("Results")
    
    if clear:
        # Reset all inputs and results
        st.session_state.block_grades = []
        st.session_state.results = []
        st.session_state.block_grade_key += 1  # Change key to reset input
        for key in ["mining_cost", "processing_cost", "mineral_price", "refining_cost", "recovery", "stock_threshold"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()
    
    if add_block and block_grade:
        # Validate and add block grade
        grade = validate_input(block_grade, "Block Grade")
        if grade is not None:
            st.session_state.block_grades.append(grade)
            st.session_state.block_grade_key += 1  # Change key to clear input
            st.success(f"Block with grade {grade:.2f}% added.")
    
    if calculate:
        # Validate inputs
        mining_cost_valid = validate_input(str(mining_cost), "Mining Cost")
        processing_cost_valid = validate_input(str(processing_cost), "Processing Cost")
        mineral_price_valid = validate_input(str(mineral_price), "Mineral Price")
        refining_cost_valid = validate_input(str(refining_cost), "Refining Cost", max_value=mineral_price)
        recovery_valid = validate_input(str(recovery), "Metallurgical Recovery", is_recovery=True)
        stock_threshold_valid = validate_input(str(stock_threshold), "Stock Threshold", is_threshold=True)
        
        if all(v is not None for v in [mining_cost_valid, processing_cost_valid, mineral_price_valid, 
                                       refining_cost_valid, recovery_valid, stock_threshold_valid]):
            if not st.session_state.block_grades:
                st.error("Please add at least one block.")
            else:
                # Calculate cut-off grade
                cutoff_grade = calculate_cutoff_grade(mining_cost_valid, processing_cost_valid, mineral_price_valid,
                                                     refining_cost_valid, recovery_valid)
                
                if cutoff_grade is not None:
                    st.success(f"**Cut-Off Grade: {cutoff_grade:.2f}%**")
                    
                    # Process blocks
                    st.session_state.results = []
                    for grade in st.session_state.block_grades:
                        action = decide_block_action(grade, cutoff_grade, stock_threshold_valid)
                        st.session_state.results.append({"Block Grade (%)": f"{grade:.2f}", "Action": action})
    
    # Display results if available
    if st.session_state.results:
        st.subheader("Block Analysis")
        df = pd.DataFrame(st.session_state.results)
        st.dataframe(df, use_container_width=True)
        
        # Summary
        processed = sum(1 for r in st.session_state.results if r["Action"] == "Process")
        stocked = sum(1 for r in st.session_state.results if r["Action"] == "Send to Stock")
        discarded = sum(1 for r in st.session_state.results if r["Action"] == "Discard")
        
        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Processed", processed)
        col2.metric("Sent to Stock", stocked)
        col3.metric("Discarded", discarded)
