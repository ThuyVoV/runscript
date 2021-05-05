# runscript
git clone https://github.com/ThuyVoV/runscripts.git <br>

You will get a folder runscripts/runscript<br>
Move the subfolder "runscript" into your project base directory.

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

