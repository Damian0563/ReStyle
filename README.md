# ReStyle
The app was built and is maintained by Damian Piechocki.
ReStyle is a web service, which allows users to create accounts,
post products on a marketplace and communicate with other potential customers or sellers in real time.
Users have the ability to manipulate their listings as well as to edit their profile information.

<img src="demo/landing.png" width="600">
<img src="demo/main.png" width="600">
<img src="demo/user.png" width="600">
<img src="demo/my_listings.png" width="600">
<div width="900">
  <img src="demo/pov1.png" width="450">
  <img src="demo/pov2.png" width="450">
</div>

## Technologies in use
  -Mongodb
  
  -Flask
  
  -HTML(Jinja templating language) and CSS
  
  -Websockets
  
  -JavaScript
  
## Booting
Run innit.py:
  ```console
  python -u [absolute_path_to_innit.py]
  ```
Alternatively run the dockerfile:
  ```console
  docker build -t restyle .
	docker run -p 3000:3000 restyle
  ```
## Overcome issues
  Handling user account creation and signing up, password hashing

  Vast customisation possibilities within user profiles

  Real time communication between users
  
  Storing and serving uploaded images
  
  Pagination of user-submitted listings
