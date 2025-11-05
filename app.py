import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Remote Permission Demo", page_icon="📱")

st.title("📱 Remote Permission Demo (with user consent)")
st.write("This demo shows how to safely ask for permissions using a web link.")

st.markdown("---")

# ---------- CAMERA ----------
st.subheader("🎥 Camera Access")
camera_image = st.camera_input("Take a picture (optional)")
if camera_image:
    st.success("✅ Picture captured successfully!")

# ---------- AUDIO ----------
st.subheader("🎤 Microphone / Audio Upload")
audio_file = st.file_uploader("Upload an audio recording (optional)", type=["mp3", "wav", "m4a"])
if audio_file:
    st.success(f"✅ Received audio file: {audio_file.name}")

# ---------- LOCATION ----------
st.subheader("📍 Location Access (Browser permission)")
location_script = """
<script>
navigator.geolocation.getCurrentPosition(
  (pos) => {
    const coords = pos.coords.latitude + ", " + pos.coords.longitude;
    const streamlit = parent.document.querySelector('iframe[srcdoc]').contentWindow.streamlit;
    streamlit.setComponentValue("user_location", coords);
  },
  (err) => console.error(err)
);
</script>
"""
st.components.v1.html(location_script, height=0)

user_location = st.session_state.get("user_location", None)
if user_location:
    st.success(f"✅ Location shared: {user_location}")

# ---------- FILE UPLOAD ----------
st.subheader("📂 File Upload")
uploaded_file = st.file_uploader("Upload any file (optional)")
if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")

st.markdown("---")
st.info("✅ All permissions are optional. No permanent data storage is done.")
