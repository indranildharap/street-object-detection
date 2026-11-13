# Street Object Detector

## Run locally

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
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
