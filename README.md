# Street Object Detector

## Run locally

Install the dependencies:

```powershell
python -m pip install -r requirements.txt -r requirements-api.txt
```

Start the FastAPI detector from the project root:

```powershell
python -m uvicorn app.main:app --reload
```

In another terminal, start the Streamlit UI:

```powershell
python -m streamlit run app/streamlit_app.py
```

The UI sends uploaded files to `http://127.0.0.1:8000/detect`. Set
`STREET_OBJECT_API_URL` to change the API endpoint. Invalid files are rejected
by the API and cleared from the UI; valid images are shown beside the annotated
results and object counts.

## Deploy with Streamlit Community Cloud and Fly.io

Streamlit Community Cloud runs the Streamlit UI only. Deploy the FastAPI
detector separately, then configure the UI to call its public URL.

### Deploy the FastAPI service to Fly.io

Install `flyctl`, sign in, and run these commands from the project root:

```powershell
fly auth login
fly launch --no-deploy
fly deploy
```

Use the generated Fly app hostname to check the API at
`https://<fly-app-name>.fly.dev/health` and its interactive docs at
`https://<fly-app-name>.fly.dev/docs`. The API deployment needs `yolo11n.pt`
beside the Dockerfile; this model file is not tracked in the Git repository, so
ensure it is present in the local deployment directory.

### Configure the Streamlit app

In the Streamlit Community Cloud app settings, add this under **Secrets**,
using the hostname from Fly.io:

```toml
STREET_OBJECT_API_URL = "https://<fly-app-name>.fly.dev/detect"
```

Then redeploy or reboot the Streamlit app. Locally, the app continues to use
`http://127.0.0.1:8000/detect` unless `STREET_OBJECT_API_URL` is set in the
environment or Streamlit secrets.
