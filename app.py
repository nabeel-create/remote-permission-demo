import streamlit as st
from docx import Document
from docx.shared import Inches
from io import BytesIO
import re

st.set_page_config(page_title="Smart CV Builder", page_icon="🧠")

st.title("🧠 Smart CV Builder")
st.write("""
Upload a **CV Template (.docx)** with placeholders (like `{{name}}`, `{{summary}}`, or `{{photo}}`).  
The app will:
- Detect all placeholders,  
- Ask you to fill them in,  
- Automatically remove empty sections,  
- Insert your uploaded **profile image** if provided.
""")

# --- Step 1: Upload Template ---
uploaded_file = st.file_uploader("📄 Upload Template (.docx)", type=["docx"])

if uploaded_file:
    doc = Document(uploaded_file)

    # --- Step 2: Extract text from paragraphs and tables ---
    text_blocks = []
    for p in doc.paragraphs:
        text_blocks.append(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text_blocks.append(cell.text)

    # --- Step 3: Detect placeholders like {{field}} ---
    all_text = "\n".join(text_blocks)
    placeholders = sorted(list(set(re.findall(r"{{(.*?)}}", all_text))))

    if not placeholders:
        st.warning("⚠️ No placeholders found in the template.")
    else:
        st.success(f"✅ Found {len(placeholders)} placeholders.")
        st.caption(", ".join(placeholders))

        st.subheader("✏️ Enter Your Information")
        user_inputs = {}

        # --- Step 4: Input fields for text placeholders ---
        for field in placeholders:
            if field.lower() != "photo":  # text inputs for all except photo
                label = field.replace("_", " ").title()
                user_inputs[field] = st.text_area(label, placeholder=f"Enter your {label} (leave blank to remove section)")

        # --- Step 5: Upload Image if {{photo}} exists ---
        photo_data = None
        if "photo" in [f.lower() for f in placeholders]:
            st.subheader("📸 Upload Profile Photo")
            uploaded_image = st.file_uploader("Choose an image (JPG or PNG)", type=["jpg", "jpeg", "png"])
            if uploaded_image:
                photo_data = uploaded_image.read()

        # --- Step 6: Generate Button ---
        if st.button("🚀 Generate CV"):
            for p in doc.paragraphs:
                for key, value in user_inputs.items():
                    tag = f"{{{{{key}}}}}"
                    if tag in p.text:
                        if value.strip():
                            p.text = p.text.replace(tag, value)
                        else:
                            p.text = ""

                # Handle photo placeholder in paragraphs
                if "{{photo}}" in p.text.lower():
                    p.text = ""
                    if photo_data:
                        run = p.add_run()
                        run.add_picture(BytesIO(photo_data), width=Inches(1.2))

            # Handle photo placeholders inside tables too
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        # Replace text placeholders
                        for key, value in user_inputs.items():
                            tag = f"{{{{{key}}}}}"
                            if tag in cell.text:
                                if value.strip():
                                    cell.text = cell.text.replace(tag, value)
                                else:
                                    cell.text = ""
                        # Handle {{photo}} in tables
                        if "{{photo}}" in cell.text.lower():
                            cell.text = ""
                            if photo_data:
                                paragraph = cell.paragraphs[0]
                                run = paragraph.add_run()
                                run.add_picture(BytesIO(photo_data), width=Inches(1.2))

            # Remove empty paragraphs
            for p in doc.paragraphs:
                if not p.text.strip():
                    p.text = ""

            # --- Step 7: Download File ---
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.success("🎉 Your CV is ready for download!")
            st.download_button(
                label="📥 Download CV (Word)",
                data=buffer,
                file_name="Generated_CV.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
