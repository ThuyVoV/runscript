# Installation
git clone https://github.com/ThuyVoV/runscripts.git <br>

In settings.py add 'runscript.apps.RunscriptConfig' to your INSTALLED_APPS.<br>
In urls.py add path('runscript/', include('runscript.urls')) <br>

Make your migrations:<br>
python manage.py makemigrations runscript<br>
python manage.py migrate<br>

Required the user to be logged in to access. If you don't have a user account:<br>
python manage.py createsuperuser<br>

It will then ask for your:<br>
username(required)<br>
email(optional, press enter again to skip)<br>
password<br>

To run the server use:<br>
python manage.py runserver<br>
Go to: http://127.0.0.1:8000/runscript/

# Usage
The app lets a user create script list, and each list contains multiple scripts that can be ran. 
The creator of the list can add other users to view and manage scripts in the list.

# Disclaimer
Currently, there are no permission restriction, so anyone added to the script list can upload, edit, or delete any scripts.
The only restriction they have is that they cannot add other users.
