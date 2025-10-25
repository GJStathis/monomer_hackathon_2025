# Frontend - Streamlit Application

This is the Streamlit frontend for the Monomer Hackathon 2025 project.

## Running the Application

From the project root directory, run:

```bash
uv run streamlit run frontend/app.py
```

The app will start and open in your browser at `http://localhost:8501`

## Pages

- **Home** (`app.py`) - Main landing page
- **Cost Dashboard** (`pages/01_💰_Cost_Dashboard.py`) - View cost analytics with interactive visualizations

## Adding New Pages

To add new pages to the Streamlit app:

1. Create a new Python file in the `frontend/pages/` directory
2. Name it with a number prefix for ordering (e.g., `02_Page_Name.py`)
3. Optionally add an emoji for the page icon (e.g., `02_📊_Analytics.py`)
4. Streamlit will automatically detect and add it to the sidebar

## Structure

```
frontend/
├── app.py              # Main page
├── pages/              # Additional pages
│   └── 01_💰_Cost_Dashboard.py
└── README.md           # This file
```

