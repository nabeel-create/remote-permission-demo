import streamlit as st
from docx import Document
from io import BytesIO
import re

st.set_page_config(page_title="Smart CV Builder", page_icon="🧠")

st.title("🧠 Smart CV Builder")
st.write("""
Upload a **CV Template (.docx)** file with placeholders (like `{{name}}`, `{{summary}}`, etc.).
The app will:
1️⃣ Detect all placeholders,  
2️⃣ Ask you to fill details,  
3️⃣ Automatically **remove blank sections** in the final CV.
""")

# --- Step 1: Upload Template ---
uploaded_file = st.file_uploader("📄 Upload Template (.docx)", type=["docx"])

if uploaded_file:
    doc = Document(uploaded_file)

    # --- Step 2: Extract all text content (paragraphs + tables) ---
    text_blocks = []
    for p in doc.paragraphs:
        text_blocks.append(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text_blocks.append(cell.text)

    # --- Step 3: Detect placeholders {{field}} ---
    all_text = "\n".join(text_blocks)
    placeholders = sorted(list(set(re.findall(r"{{(.*?)}}", all_text))))

    if not placeholders:
        st.warning("⚠️ No placeholders found in your template.")
    else:
        st.success(f"✅ Found {len(placeholders)} fields in template.")
        st.caption(", ".join(placeholders))

        st.subheader("✏️ Fill in your details")
        user_inputs = {}
        for field in placeholders:
            label = field.replace("_", " ").title()
            user_inputs[field] = st.text_area(label, placeholder=f"Enter your {label} (leave blank to remove section)")

        if st.button("🚀 Generate CV"):
            # --- Step 4: Replace placeholders ---
            for p in doc.paragraphs:
                for key, value in user_inputs.items():
                    tag = f"{{{{{key}}}}}"
                    if tag in p.text:
                        if value.strip():
                            p.text = p.text.replace(tag, value)
                        else:
                            # if user left blank → remove that line
                            p.text = ""
            
            # Replace in tables too
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for key, value in user_inputs.items():
                            tag = f"{{{{{key}}}}}"
                            if tag in cell.text:
                                if value.strip():
                                    cell.text = cell.text.replace(tag, value)
                                else:
                                    cell.text = ""

            # --- Step 5: Clean up empty lines ---
            for p in doc.paragraphs:
                if not p.text.strip():
                    p.text = ""

            # --- Step 6: Download final CV ---
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.success("🎉 Your CV has been generated!")
            st.download_button(
                label="📥 Download CV (Word)",
                data=buffer,
                file_name="Generated_CV.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
