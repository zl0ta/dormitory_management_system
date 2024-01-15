venv_path = 'C:/xampp/htdocs/dormitory-management-system/dormitory'
activate_this = venv_path + '/Scripts/Activate.ps1'

# Activate the virtual environment
exec(open(activate_this).read(), dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)

# Add the path to your project directory
sys.path.insert(0, 'C:/xampp/htdocs/dormitory-management-system')

from app import app as application
