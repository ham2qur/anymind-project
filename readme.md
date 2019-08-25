# Project for Python Engineer at AnyMind Group

## Notes

- This is a simple project. We’ll not look into whether you can do it or not, but the details.
- You can choose any tool you like for this project but programming language should be Python 3.6 or 3.7
- Make sure you have it tested
- We'll review your documentation as well

## Tips

- The repository should have a readme file with clear instructions of how to deploy/install locally
- DON’t use public available Twitter SDK instead please implement your own
- Include unit tests

## Getting started

This django application exposes two routes:
- hashtags/<str:tag>
- users/<str:user>

The first route fetches tweets by tag name provided.
The second route fetches tweets by user.

The optional parameter is limit, specifies the number of tweets to retrieve, the default should be 30


### Deployment

This is a Python django application, so you need to have python > 3.7 in able to run this application.

# Steps
- Git clone project
- install requirements (pip install -r requirements)
- python manage.py migrate
- python manage.py runserver

### Running tests

./manage.py test
