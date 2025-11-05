import streamlit as st
from docx import Document
from docx.shared import Inches
from io import BytesIO
import re

st.set_page_config(page_title="Smart CV Builder", page_icon="🧠")

st.title("🧠 Smart CV Builder with Image Support")
st.write("""
Upload your `.docx` CV template.  
This version supports:
- Embedded template images (JPEG/PNG),
- User photo upload for `{{photo}}` placeholder,
- Auto removal of empty sections.
""")

# --- Upload template ---
uploaded_file = st.file_uploader("📄 Upload CV Template (.docx)", type=["docx"])

if uploaded_file:
    # Load the template safely (retaining images)
    doc = Document(uploaded_file)

    # Extract text from all paragraphs and table cells
    all_text = []
    for p in doc.paragraphs:
        all_text.append(p.text)
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                all_text.append(c.text)

    # --- Detect placeholders {{field}} ---
    all_text_joined = "\n".join(all_text)
    placeholders = sorted(list(set(re.findall(r"{{(.*?)}}", all_text_joined))))

    if not placeholders:
        st.warning("⚠️ No placeholders found in this template.")
    else:
        st.success(f"✅ Found {len(placeholders)} placeholders.")
        st.caption(", ".join(placeholders))

        st.subheader("✏️ Enter Your Details")
        user_inputs = {}

        # --- Create text areas for each placeholder except 'photo'
        for field in placeholders:
            if field.lower() != "photo":
                user_inputs[field] = st.text_area(
                    field.replace("_", " ").title(),
                    placeholder=f"Enter your {field.replace('_', ' ')} (leave blank to remove)",
                )

        # --- Image upload only if {{photo}} exists ---
        photo_data = None
        if any(f.lower() == "photo" for f in placeholders):
            st.subheader("📸 Upload Profile Image")
            photo_file = st.file_uploader("Choose an image (JPG/PNG)", type=["jpg", "jpeg", "png"])
            if photo_file:
                # Read binary data
                photo_data = photo_file.read()

        # --- Generate Button ---
        if st.button("🚀 Generate CV"):
            for p in doc.paragraphs:
                for key, value in user_inputs.items():
                    tag = f"{{{{{key}}}}}"
                    if tag in p.text:
                        if value.strip():
                            p.text = p.text.replace(tag, value)
                        else:
                            p.text = ""

                # Handle photo placeholder in paragraph
                if "{{photo}}" in p.text.lower():
                    p.text = ""
                    if photo_data:
                        run = p.add_run()
                        run.add_picture(BytesIO(photo_data), width=Inches(1.3))

            # Handle photo + text placeholders inside tables
            for t in doc.tables:
                for r in t.rows:
                    for c in r.cells:
                        # Replace text placeholders
                        for key, value in user_inputs.items():
                            tag = f"{{{{{key}}}}}"
                            if tag in c.text:
                                if value.strip():
                                    c.text = c.text.replace(tag, value)
                                else:
                                    c.text = ""
                        # Insert photo inside tables
                        if "{{photo}}" in c.text.lower():
                            c.text = ""
                            if photo_data:
                                paragraph = c.paragraphs[0]
                                run = paragraph.add_run()
                                run.add_picture(BytesIO(photo_data), width=Inches(1.3))

            # Clean up empty paragraphs
            for p in doc.paragraphs:
                if not p.text.strip():
                    p.text = ""

            # --- Save and provide download ---
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.success("🎉 Your CV has been successfully generated!")
            st.download_button(
                label="📥 Download CV (Word)",
                data=buffer,
                file_name="Generated_CV.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
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
