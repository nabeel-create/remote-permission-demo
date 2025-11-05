import streamlit as st
from docx import Document
from docx.shared import Inches
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import re

st.set_page_config(page_title="Smart CV Builder", page_icon="🧠")

st.title("🧠 Smart CV Builder")
st.write("""
Upload your CV Template (Word, Image, or PDF).  
Supports:
- 📄 `.docx` templates with placeholders (`{{name}}`, `{{summary}}`)
- 🖼️ JPEG/PNG/AVIF templates (overlay text directly)
- 👤 Optional photo upload (`{{photo}}`)
""")

# --- Upload template ---
uploaded_template = st.file_uploader(
    "📄 Upload Your CV Template",
    type=["docx", "jpg", "jpeg", "png", "avif", "pdf"],
    help="Upload your CV design (Word, Image, or PDF)"
)

# --- Optional photo upload ---
uploaded_photo = st.file_uploader("📸 Upload Your Photo (optional)", type=["jpg", "jpeg", "png", "avif"])

# ==================================================
# WORD TEMPLATE MODE (.docx)
# ==================================================
if uploaded_template and uploaded_template.name.lower().endswith(".docx"):
    doc = Document(uploaded_template)

    # Extract placeholders
    all_text = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                all_text.append(c.text)

    placeholders = sorted(set(re.findall(r"{{(.*?)}}", "\n".join(all_text))))

    st.subheader("✏️ Fill in your details")
    user_inputs = {}
    for field in placeholders:
        if field.lower() != "photo":
            user_inputs[field] = st.text_area(field.title(), placeholder=f"Enter {field}")

    if st.button("🚀 Generate CV"):
        for p in doc.paragraphs:
            for key, value in user_inputs.items():
                tag = f"{{{{{key}}}}}"
                if tag in p.text:
                    p.text = p.text.replace(tag, value)
            if "{{photo}}" in p.text.lower() and uploaded_photo:
                p.text = ""
                run = p.add_run()
                run.add_picture(BytesIO(uploaded_photo.read()), width=Inches(1.3))

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        st.download_button("📥 Download Word CV", buffer, "Generated_CV.docx")

# ==================================================
# IMAGE TEMPLATE MODE (.jpg, .jpeg, .png, .avif)
# ==================================================
elif uploaded_template and uploaded_template.name.split(".")[-1].lower() in ["jpg", "jpeg", "png", "avif"]:
    image = Image.open(uploaded_template)
    st.image(image, caption="Template Preview", use_container_width=True)

    st.subheader("✏️ Enter Your CV Details")
    name = st.text_input("Full Name")
    job_title = st.text_input("Job Title")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    skills = st.text_area("Skills")
    about = st.text_area("About Me / Summary")

    if st.button("🖋️ Generate Image CV"):
        img_edit = image.convert("RGBA")
        draw = ImageDraw.Draw(img_edit)

        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()

        # Simple positioning (you can adjust)
        W, H = img_edit.size
        x, y = 100, 100
        line_gap = 40

        text_lines = [
            f"{name}",
            f"{job_title}",
            f"{email}",
            f"{phone}",
            "",
            f"Skills: {skills}",
            "",
            f"About: {about}",
        ]

        for line in text_lines:
            if line.strip():
                draw.text((x, y), line, fill=(0, 0, 0, 255), font=font)
                y += line_gap

        buffer = BytesIO()
        img_edit.save(buffer, format="PNG")
        buffer.seek(0)

        st.image(img_edit, caption="Generated CV", use_container_width=True)
        st.download_button("📥 Download Image CV", buffer, file_name="Generated_CV.png", mime="image/png")

# ==================================================
# PDF TEMPLATE (not editable yet)
# ==================================================
elif uploaded_template and uploaded_template.name.lower().endswith(".pdf"):
    st.info("📄 PDF uploaded. Text overlay support will be added soon.")
