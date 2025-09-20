import streamlit as st
import os
import csv
from datetime import datetime
import random
import io
from PIL import Image

# Page configuration
st.set_page_config(page_title="OMR Evaluation", page_icon="📝", layout="wide")

# Page header
st.title("OMR Sheet Evaluation")
st.markdown("Upload and evaluate OMR answer sheets")

# Mock OMR processing function (simulates backend functionality)
def process_omr_sheet(image):
    """Mock function to simulate OMR processing"""
    # Generate random answers for demonstration
    questions = range(1, 21)
    options = ['A', 'B', 'C', 'D']
    detected_answers = {str(q): random.choice(options) for q in questions}
    return detected_answers

# Create directory for OMR uploads if it doesn't exist
omr_upload_dir = os.path.join("uploads", "omr_sheets")
os.makedirs(omr_upload_dir, exist_ok=True)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload OMR Sheet")
    uploaded_file = st.file_uploader("Choose an OMR sheet image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded OMR Sheet", use_column_width=True)
        
        # Upload button
        if st.button("Process OMR Sheet"):
            with st.spinner("Processing OMR sheet..."):
                # Process the OMR sheet locally
                detected_answers = process_omr_sheet(uploaded_file)
                
                # Store in session state
                st.session_state.omr_filename = uploaded_file.name
                st.session_state.detected_answers = detected_answers
                
                st.success("OMR sheet processed successfully!")
                
                # Display detected answers
                st.subheader("Detected Answers")
                st.markdown("#### Detected Answers")
                for q, a in detected_answers.items():
                    st.markdown(f"**Question {q}:** {a}")
                st.divider()

with col2:
    st.subheader("Evaluate Answers")
    
    # Input for answer key
    st.markdown("Enter the correct answer key (format: 1:A, 2:B, etc.)")
    
    # Create input fields for answer key
    answer_key = {}
    cols = st.columns(5)
    
    for i in range(1, 21):  # Assuming 20 questions max
        col_idx = (i - 1) % 5
        with cols[col_idx]:
            answer = st.selectbox(f"Q{i}", ["", "A", "B", "C", "D"], key=f"answer_{i}")
            if answer:
                answer_key[str(i)] = answer
    
    # Evaluate button
    if st.button("Evaluate OMR Sheet"):
        if not hasattr(st.session_state, "omr_filename"):
            st.error("Please upload and process an OMR sheet first")
        elif not answer_key:
            st.error("Please enter at least one answer in the answer key")
        else:
            with st.spinner("Evaluating answers..."):
                # Evaluate locally
                detected_answers = st.session_state.detected_answers
                
                # Calculate score
                score = 0
                total = len(answer_key)
                results = {}
                
                for q, correct_answer in answer_key.items():
                    student_answer = detected_answers.get(q, "")
                    if student_answer == correct_answer:
                        status = "Correct"
                        score += 1
                    elif not student_answer:
                        status = "Skipped"
                    else:
                        status = "Incorrect"
                    
                    results[q] = status
                
                percentage = round((score / total) * 100) if total > 0 else 0
                
                # Display results
                st.success(f"Evaluation complete! Score: {score}/{total}")
                
                # Display results
                st.subheader("Detailed Results")
                for q, status in results.items():
                    student_ans = detected_answers.get(q, "")
                    correct_ans = answer_key.get(q, "")
                    
                    if status == "Correct":
                        status_color = "green"
                        status_icon = "✅"
                    elif status == "Incorrect":
                        status_color = "red"
                        status_icon = "❌"
                    else:  # Skipped
                        status_color = "orange"
                        status_icon = "⚠️"
                    
                    st.markdown(f"""
                    {status_icon} **Question {q}:** Student: {student_ans} | Correct: {correct_ans} | <span style='color:{status_color}'>{status}</span>
                    """, unsafe_allow_html=True)
                
                # Display summary
                st.subheader("Summary")
                col1, col2, col3 = st.columns(3)
                col1.metric("Score", f"{score}/{total}")
                col2.metric("Percentage", f"{percentage}%")
                col3.metric("Status", "Pass" if percentage >= 60 else "Fail")