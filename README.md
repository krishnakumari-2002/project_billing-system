1.Navigate to the project Folder and create the env
python -m venv venv
# Activate the venv
# Windows
venv\Scripts\activate

2.Install all the requireed depencise from the requirement .txt
pip install -r requirements.txt

3.Use the databse from your local system ..
4.Install the redis server for mail process..

5 run the redis by uisng te command  .\redis-server.exe  
6.run the broker  python -m celery -A shop worker --loglevel=info --pool=solo

 7.run the local server 
 python manage.py runserver
 
 8.Enter the web brower as the http://127.0.0.1:8000/billing/

 Notes / Tips
Make sure the .env file contains correct credentials:
EMAIL_USER=youremail@gmail.com
EMAIL_PASS=app_password_here
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
