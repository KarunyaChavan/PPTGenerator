# PPT Generator Web Application

A local web application for automated PowerPoint presentation generation with version control.

## Features

- **Automated PPT Generation**: Convert structured form data into PowerPoint presentations
- **Version Control**: Track all PPT versions with rollback capabilities  
- **Role-based Access**: Separate dashboards for Users and Admins
- **Template Compliance**: Enforce organizational branding and formatting standards
- **Local Storage**: SQLite database with file-based PPT storage

## Project Structure

```
PPTGenerator/
├── app/                    # Main application package
│   ├── models/            # Database models
│   ├── routes/            # Flask route handlers
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions
├── static/                # Static assets (CSS, JS, images)
├── templates/             # HTML templates
├── storage/               # PPT file storage
├── database/              # SQLite database location
└── tests/                 # Test files
```

## Setup Instructions

1. **Create and activate conda environment**:
   ```bash
   conda create -n pptgen python=3.11 -y
   conda activate pptgen
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

## User Roles

### User (Department Employee)
- Submit presentation content via structured forms
- Track submission status
- Download approved presentations

### Admin (Validation Team)  
- Review submitted presentations
- Approve/reject submissions
- Manage presentation versions
- Access version history and rollback functionality

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **PPT Generation**: python-pptx
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login