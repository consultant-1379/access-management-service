# Decrypt files 
# create ams_vault.txt file in main folder and save valid password inside file
# password can be find in STS PMP
./decrypt_files.sh
# How to run locally
python3.9 -m venv amsEnv
source amsEnv/bin/activate
python3.9 -m pip install -r requirements.txt
python3.9 -m pip freeze  | grep -v pkg_resources > requirements.txt
# CREATE DB FOR TEST
mysql  -h host -p port -u your_username -p
## OR for docker root
mysql -u root -p
## DB create
CREATE DATABASE your_database_name;
GRANT ALL PRIVILEGES ON your_database_name.* TO '%'@'localhost';
# CREATE super user 
python3.9 manage.py makemigrations
python3.9 manage.py migrate
python3.9 manage.py create_groups
python3.9 manage.py createsuperuser
# ENV SETUP
python3.9 manage.py create_enm_profiles
python3.9 manage.py create_areas
python3.9 manage.py create_system_types
python3.9 manage.py create_test_systems or python3.9 manage.py create_enm_systems
python3.9 manage.py import_enm_users

# install npm modules
cd /opt/app/ams/static/ && npm install 
# Here you paste port on which you want to run it 
python3.9 manage.py runserver 0.0.0.0:8091
# OR - but have to include statics in urls
gunicorn ams.wsgi --bind 0.0.0.0:8091 &
# for nginx to serve static files look at start-server.sh

# BEFORE PUSH encrypt files 
./encrypt_files.sh 
