# DRF Recruitment App
 
## How to run app?
1. [Install Docker Compose](https://docs.docker.com/compose/install/)
2. Clone this repository
3. Run `python manage.py createsuperuser` to create admin account
4. Run `docker-compose up --build`
5. Go to `http://127.0.0.1:8000/` to check if app is working


* You can manage the application from `http://127.0.0.1:8000/admin/`
* There you can add users and simply assign Plans to their accounts using UserProfile
* You can add Plans and Features that can make other thumbnails too
* If you want to post and image, you can use for example Postman (Basic Authorization, Body: image, and expire_time if you want to generate expiring link)

