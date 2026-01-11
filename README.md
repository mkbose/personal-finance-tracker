# Personal Finance Tracker

A comprehensive web application for tracking personal expenses with categories, analytics, and import/export functionality.

## Features

- **User Authentication**: Login/logout functionality with secure password hashing
- **Expense Management**: Full CRUD operations for expense entries
- **Category System**: Hierarchical categories and subcategories
- **Dashboard**: Analytics with interactive charts and spending insights
- **Import/Export**: CSV and Excel file support for bulk operations
- **Responsive Design**: Modern UI that works on all devices
- **Docker Support**: Containerized deployment

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, JavaScript, Plotly.js
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Data Processing**: Pandas, OpenPyXL
- **Containerization**: Docker

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Access the application at `http://localhost:5000`

### Local Development

1. **Set up virtual environment** (recommended):
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run application**:
   ```bash
   python app.py
   ```

4. **Access application** at `http://localhost:5000`

5. **Deactivate virtual environment** when done:
   ```bash
   deactivate
   ```

## Usage

1. **Register**: Create a new account
2. **Add Categories**: Set up expense categories and subcategories
3. **Track Expenses**: Add daily expenses with descriptions and amounts
4. **View Analytics**: Check the dashboard for spending insights
5. **Import/Export**: Use CSV/Excel files for bulk data management

## API Endpoints

- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/expenses/monthly-trend` - Monthly spending trends
- `GET /api/expenses/category-comparison` - Category spending comparison
- `GET /categories/{id}/subcategories/json` - Subcategories for a category

## File Structure

```
personal_finance/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── expenses.py
│   │   └── categories.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── main.py
│       ├── expenses.py
│       ├── categories.py
│       └── api.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── auth/
│   ├── expenses/
│   └── categories/
├── static/
│   ├── css/
│   └── js/
├── instance/
├── uploads/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Security Notes

- Passwords are hashed using Werkzeug's security functions
- User sessions are managed securely with Flask-Login
- CSRF protection is enabled for all forms
- Input validation prevents SQL injection and XSS attacks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.
