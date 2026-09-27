# Smart Store POS

A modern desktop store management app built with Python and Tkinter.

Features:
- SQLite database support
- Customer management
- Customer search
- Sales basket
- Invoice creation
- Invoice history
- Product catalog
- Clean modern desktop GUI

Project structure:
- `app.py` – desktop application
- `database.py` – database setup and helpers
- `smart_store.db` – SQLite database file created at runtime
- `requirements.txt` – project dependencies

Requirements:
- Python 3.9+
- Tkinter (included with Python on most systems)

Run the app:

```bash
python app.py
```

If Tkinter is not installed on your system:

Ubuntu/Debian:
```bash
sudo apt-get install python3-tk
```

Windows/macOS:
- Install Python from python.org and make sure Tkinter is included.

Notes:
- The app creates its database automatically on first launch.
- It includes sample products and customers to help you test the system quickly.
