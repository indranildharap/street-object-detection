import base64
import hashlib
import os

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


def get_api_url() -> str:
    api_url = os.getenv("STREET_OBJECT_API_URL")
    if api_url:
        return api_url

    try:
        return st.secrets["STREET_OBJECT_API_URL"]
    except (KeyError, StreamlitSecretNotFoundError):
        return "http://127.0.0.1:8000/detect"


API_URL = get_api_url()
UPLOAD_KEY_PREFIX = "street_object_upload"

st.set_page_config(page_title="Street Object Detector", layout="wide")
st.title("Street Object Detector")
st.write("Upload an image to detect and count the objects in it.")

if "upload_generation" not in st.session_state:
    st.session_state["upload_generation"] = 0

upload_error = st.session_state.pop("upload_error", None)
if upload_error:
    st.error(upload_error)

uploaded_file = st.file_uploader(
    "Choose a file",
    key=f"{UPLOAD_KEY_PREFIX}_{st.session_state['upload_generation']}",
    help="The detector will check that the uploaded file is a valid image.",
)

if st.button("Clear image"):
    st.session_state["upload_generation"] += 1
    st.session_state.pop("detection", None)
    st.session_state.pop("detection_error", None)
    st.rerun()

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    upload_id = hashlib.sha256(image_bytes).hexdigest()

    if st.session_state.get("detection", {}).get("upload_id") != upload_id:
        try:
            response = requests.post(
                API_URL,
                files={
                    "file": (
                        uploaded_file.name,
                        image_bytes,
                        uploaded_file.type or "application/octet-stream",
                    )
                },
                timeout=180,
            )
            response.raise_for_status()
            st.session_state["detection"] = {
                "upload_id": upload_id,
                "annotated_image": base64.b64decode(
                    response.json()["annotated_image"]
                ),
                "counts": response.json()["counts"],
            }
            st.session_state.pop("detection_error", None)
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 400:
                st.session_state["upload_error"] = (
                    exc.response.json().get("detail", "The uploaded file is invalid.")
                )
                st.session_state["upload_generation"] += 1
                st.session_state.pop("detection", None)
                st.session_state.pop("detection_error", None)
                st.rerun()
            st.session_state["detection_error"] = (
                f"The detector could not process this upload: {exc}"
            )
        except (requests.RequestException, ValueError, KeyError) as exc:
            st.session_state["detection_error"] = (
                f"Could not get a valid response from the detector: {exc}"
            )

    detection = st.session_state.get("detection")
    if detection is not None and detection["upload_id"] == upload_id:
        original_column, result_column = st.columns(2)
        with original_column:
            st.subheader("Original image")
            st.image(image_bytes, use_container_width=True)
        with result_column:
            st.subheader("Detected objects")
            st.image(detection["annotated_image"], use_container_width=True)

        st.subheader("Object counts")
        if detection["counts"]:
            st.dataframe(
                [
                    {"Object": name, "Count": count}
                    for name, count in sorted(detection["counts"].items())
                ],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No objects were detected.")

    detection_error = st.session_state.get("detection_error")
    if detection_error:
        st.error(detection_error)
