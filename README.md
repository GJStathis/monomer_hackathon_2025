# Monomer Hackathon 2025

A full-stack application for managing reagent data, plate experiments, and cell growth tracking with cost analytics.

## Project Structure

```
monomer_hackathon_2025/
├── src/                    # Source code
│   └── models/            # SQLAlchemy database models
│       ├── __init__.py
│       ├── reagent.py
│       ├── plate_reagent_map.py
│       ├── plate.py
│       └── cell_growth.py
├── frontend/              # Streamlit web application
│   ├── app.py            # Main page
│   ├── pages/            # Additional pages
│   └── README.md
├── alembic/              # Database migrations
│   └── versions/
├── data/                 # Data files
│   └── default_reagnets.csv
├── setup.sh              # Setup script to install uv
├── run_frontend.sh       # Run Streamlit app
└── database.db           # SQLite database
```

## Setup

### 1. Install UV

Run the setup script to ensure UV is installed:

```bash
./setup.sh
```

Or manually install:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies

Dependencies are automatically managed by UV when you run commands.

## Database

This project uses SQLAlchemy with Alembic for database migrations.

### Models

- **Reagent**: Chemical reagent information
- **PlateReagentMap**: Maps plates/wells to reagents
- **Plate**: Plate measurement data
- **CellGrowth**: Cell density measurements

### Running Migrations

```bash
# Check current migration status
uv run alembic current

# View migration history
uv run alembic history

# Apply all migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "Description"

# Create empty migration for data changes
uv run alembic revision -m "Description"
```

## Frontend

The frontend is built with Streamlit and includes:
- Home page
- Cost Dashboard with interactive visualizations

### Running the Frontend

```bash
# Using the helper script
./run_frontend.sh

# Or directly
uv run streamlit run frontend/app.py
```

The app will be available at `http://localhost:8501`

## Development

### Adding New Models

1. Create a new model file in `src/models/`
2. Import it in `src/models/__init__.py`
3. Generate migration: `uv run alembic revision --autogenerate -m "Description"`
4. Apply migration: `uv run alembic upgrade head`

### Adding New Frontend Pages

1. Create a new file in `frontend/pages/`
2. Name it with a number prefix: `02_Page_Name.py`
3. Streamlit will automatically detect it

## Database Schema

See `local/table_models.md` for detailed schema documentation.

## Dependencies

Main dependencies:
- `sqlalchemy` - ORM for database
- `alembic` - Database migrations
- `streamlit` - Web application framework
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation

All dependencies are managed in `pyproject.toml` and installed via UV.

