import streamlit as st
from docx import Document
from docx.shared import Inches
from io import BytesIO
import re
from PIL import Image
import pillow_avif  # 👈 enables AVIF decoding in Pillow

st.set_page_config(page_title="Smart CV Builder", page_icon="🧠")

st.title("🧠 Smart CV Builder")
st.write("""
Upload your CV Template (Word, Image, or PDF).  
Supports:
- 📄 `.docx` templates with placeholders (`{{name}}`, `{{summary}}`)
- 🖼️ JPEG/PNG/AVIF/PDF templates
- 👤 User photo upload (`{{photo}}`)
- 🚫 Auto-removal of empty sections
""")

# --- Upload Template (Word, Image, or PDF) ---
uploaded_template = st.file_uploader(
    "📄 Upload Your CV Template",
    type=["docx", "jpg", "jpeg", "png", "pdf", "avif"],
    help="Upload your CV design (Word, Image, or PDF)"
)

# --- Optional photo upload ---
uploaded_photo = st.file_uploader("📸 Upload Your Photo (optional)", type=["jpg", "jpeg", "png", "avif"])

# ===============================
# Handle different template types
# ===============================
if uploaded_template:
    file_type = uploaded_template.name.split(".")[-1].lower()

    # ================
    # DOCX Template
    # ================
    if file_type == "docx":
        doc = Document(uploaded_template)

        # Extract all text (paragraphs + tables)
        all_text = []
        for p in doc.paragraphs:
            all_text.append(p.text)
        for t in doc.tables:
            for r in t.rows:
                for c in r.cells:
                    all_text.append(c.text)

        # Find placeholders like {{name}}
        joined_text = "\n".join(all_text)
        placeholders = sorted(list(set(re.findall(r"{{(.*?)}}", joined_text))))

        if not placeholders:
            st.warning("⚠️ No placeholders found in this template.")
        else:
            st.success(f"✅ Found {len(placeholders)} placeholders.")
            st.caption(", ".join(placeholders))

            st.subheader("✏️ Enter Your Details")
            user_inputs = {}

            for field in placeholders:
                if field.lower() != "photo":
                    user_inputs[field] = st.text_area(
                        field.replace("_", " ").title(),
                        placeholder=f"Enter your {field.replace('_', ' ')} (leave blank to remove)",
                    )

            # --- Generate CV ---
            if st.button("🚀 Generate CV"):
                for p in doc.paragraphs:
                    for key, value in user_inputs.items():
                        tag = f"{{{{{key}}}}}"
                        if tag in p.text:
                            if value.strip():
                                p.text = p.text.replace(tag, value)
                            else:
                                p.text = ""

                    if "{{photo}}" in p.text.lower():
                        p.text = ""
                        if uploaded_photo:
                            run = p.add_run()
                            run.add_picture(BytesIO(uploaded_photo.read()), width=Inches(1.3))

                # Replace in tables too
                for t in doc.tables:
                    for r in t.rows:
                        for c in r.cells:
                            for key, value in user_inputs.items():
                                tag = f"{{{{{key}}}}}"
                                if tag in c.text:
                                    if value.strip():
                                        c.text = c.text.replace(tag, value)
                                    else:
                                        c.text = ""
                            if "{{photo}}" in c.text.lower():
                                c.text = ""
                                if uploaded_photo:
                                    paragraph = c.paragraphs[0]
                                    run = paragraph.add_run()
                                    run.add_picture(BytesIO(uploaded_photo.read()), width=Inches(1.3))

                # Remove empty paragraphs
                for p in doc.paragraphs:
                    if not p.text.strip():
                        p.text = ""

                # Save to memory buffer
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                st.success("🎉 CV generated successfully!")
                st.download_button(
                    label="📥 Download CV (Word)",
                    data=buffer,
                    file_name="Generated_CV.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    # ================
    # Image or PDF Template
    # ================
    elif file_type in ["jpg", "jpeg", "png", "pdf", "avif"]:
        st.subheader("🖼️ Template Preview")
        try:
            if file_type in ["jpg", "jpeg", "png", "avif"]:
                img = Image.open(uploaded_template)
                st.image(img, caption="Template Preview", use_container_width=True)
            else:
                st.info("📄 PDF uploaded (preview not supported here, but file accepted).")

            st.info("✅ Template uploaded successfully! (Auto-fill for image/PDF templates coming soon.)")
        except Exception as e:
            st.error(f"Error displaying template: {e}")

    else:
        st.error("Unsupported file type. Please upload DOCX, JPG, JPEG, PNG, PDF, or AVIF.")
