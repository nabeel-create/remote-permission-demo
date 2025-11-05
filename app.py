import streamlit as st
import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Mobile Permission Access Portal", page_icon="📱", layout="centered")

st.title("📱 Mobile Permission Access Portal")
st.caption("By Nabeel | Streamlit Web App")

st.markdown("""
Welcome!  
This page demonstrates **secure and permission-based access** to mobile data through your browser.  
Each permission is optional and requires **explicit user consent**.
""")

st.markdown("---")

# ---------- CAMERA ----------
st.subheader("🎥 Step 1: Camera Access")
camera_image = st.camera_input("Take a photo (optional)")
if camera_image:
    st.success("✅ Photo captured successfully!")
    st.image(camera_image, caption="Captured Image", use_column_width=True)

# ---------- AUDIO ----------
st.subheader("🎤 Step 2: Audio Upload")
audio_file = st.file_uploader("Upload an audio file (optional)", type=["mp3", "wav", "m4a"])
if audio_file:
    st.audio(audio_file)
    st.success(f"✅ Uploaded audio: {audio_file.name}")

# ---------- LOCATION ----------
st.subheader("📍 Step 3: Location Access")
st.write("Click the button below to share your current location (browser will ask permission).")

get_location = st.button("📍 Share My Location")
if get_location:
    st.components.v1.html(
        """
        <script>
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const coords = pos.coords.latitude + "," + pos.coords.longitude;
            const py = parent.document.querySelector('iframe[srcdoc]').contentWindow.streamlit;
            py.setComponentValue("user_location", coords);
          },
          (err) => alert("Permission denied or error getting location.")
        );
        </script>
        """, height=0
    )

user_location = st.session_state.get("user_location", None)
if user_location:
    st.success(f"✅ Location received: {user_location}")

# ---------- FILE UPLOAD ----------
st.subheader("📂 Step 4: File Upload")
uploaded_file = st.file_uploader("Upload any document, image, or file (optional)")
if uploaded_file:
    st.success(f"✅ File received: {uploaded_file.name}")

# ---------- SUMMARY ----------
st.markdown("---")
st.header("📊 Permission Summary")
st.write("Here's a summary of what was shared:")

if camera_image or audio_file or uploaded_file or user_location:
    st.write("**Camera:**", "✅" if camera_image else "❌ Not shared")
    st.write("**Audio:**", "✅" if audio_file else "❌ Not shared")
    st.write("**File:**", "✅" if uploaded_file else "❌ Not shared")
    st.write("**Location:**", user_location if user_location else "❌ Not shared")
    st.success("✅ Data successfully processed (temporary session only).")
else:
    st.info("No permissions granted yet.")

st.markdown("---")
st.caption(f"© {datetime.datetime.now().year} Nabeel | Secure Consent Demo")

