# BRONZE: 1177 BC - Flask Web App

Web version of BRONZE: 1177 BC, built with Flask. Mobile-responsive and ready to deploy.

## Local Development

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit `http://localhost:5000` in your browser.

## File Structure

```
bronze_flask/
├── app.py                 # Flask application
├── game_logic.py          # Game state and actions
├── requirements.txt       # Python dependencies
├── Procfile              # For Render deployment
├── render.yaml           # Render configuration
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── game.html
│   └── victory.html
└── static/               # CSS and JavaScript
    ├── css/
    │   └── style.css
    └── js/
        └── game.js
```

## Deployment to Render

### Method 1: GitHub Integration (Recommended)

1. Push this folder to a GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **New → Web Service**
4. Connect your GitHub repository
5. Render will auto-detect `render.yaml` and configure everything
6. Click **Create Web Service**
7. Wait 2-3 minutes for deployment
8. Your app will be live at `https://bronze-1177-bc.onrender.com`

### Method 2: Manual Configuration

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New → Web Service**
3. Connect your repository or use "Public Git Repository"
4. Configure:
   - **Name:** bronze-1177-bc
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add environment variable:
   - **SECRET_KEY:** (generate a random string)
6. Click **Create Web Service**

### Important Notes

- **Free tier:** Render free tier spins down after 15 minutes of inactivity. First load may take 30-60 seconds.
- **Sessions:** Game state is stored in Flask sessions (client-side cookies). Each player's game is independent.
- **Persistence:** No database needed - all state is in session storage.

## Environment Variables

- `SECRET_KEY`: Flask secret key for session encryption (auto-generated on Render)
- `PORT`: Server port (auto-set by Render, defaults to 5000 locally)

## Features

- ✅ Mobile-responsive (Bootstrap 5)
- ✅ Session-based game state (no database needed)
- ✅ All v1.2.6 game mechanics
- ✅ Touch-friendly UI
- ✅ Auto-dismissing alerts
- ✅ Confirmation dialogs for dangerous actions
- ✅ Progress bars for visual feedback

## Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** Bootstrap 5, Vanilla JavaScript
- **Deployment:** Render (with Gunicorn)
- **Session Storage:** Flask sessions (encrypted cookies)

## Performance

- **Load time:** <1 second (after initial spin-up on free tier)
- **Mobile data usage:** ~500 KB initial load
- **Browser support:** All modern browsers (Chrome, Firefox, Safari, Edge)

## Customization

### Change Secret Key (Production)

Edit `app.py` or set environment variable:

```bash
export SECRET_KEY="your-super-secret-key-here"
```

### Adjust Game Balance

Edit `game_logic.py`:
- Starting resources
- Action costs
- Random event probabilities
- Victory conditions

### Styling

Edit `static/css/style.css`:
- Colors (see `:root` variables)
- Mobile breakpoints
- Animation speeds

## Troubleshooting

**App won't start locally:**
```bash
pip install --upgrade Flask gunicorn
```

**Session data lost:**
- Check that SECRET_KEY is set and not changing
- Clear browser cookies

**Render deployment fails:**
- Check Python version in `render.yaml` matches available versions
- Verify `requirements.txt` has no syntax errors
- Check Render build logs for specific errors

## License

See LICENSE in root repository.
