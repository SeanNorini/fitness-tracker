<!-- PROJECT LOGO -->
<div align="center">
  <h1 align="center" id="top">Group 5 - Fitness Tracker</h1>
  <a href="https://github.com/jaammons/FitnessTracker">https://github.com/jaammons/FitnessTracker</a>
</div>

### Contributors

- James Ammons - Project Manager
- Sean Norini - Developer
- Ethan Long - Developer
- Elijah Arnold - Developer
- Rahulkumar Jani - Developer

### Setting up testing and development

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/jaammons/FitnessTracker.git
   ```
2. Setup Virtual Environment
   ```sh
   # Create virtual environment folder name env
   python -m venv env
   ```
   ```sh
   # Activate the virtual environment, terminal should show env near prompt. Type deactivate to exit virtual environment
   env/scripts/activate
   ```
3. Install Project Dependencies
   ```sh
   pip install -r requirements.txt
   ```

### Running Django

1. Navigate to project folder in terminal
   ```sh
   # Example powershell command and directory, the folder should contain manage.py
   cd c:/your-github-folder/FitnessTracker
   ```
2. Start Django server
   ```sh
   python manage.py runserver
   ```
3. Ctrl + left-click the link created in the terminal or open web browser and enter django site address
   ```sh
   # Default address
   http://127.0.0.1:8000/
   ```