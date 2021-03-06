# Django REST Google OAuth2

This app aims to facilitate the integration of signing in with Google OAuth2.
It is intended to work with SPAs (e.g React, Vue, Angular) and potentially
 with mobiles in the future.


### Rationale
It is rewritten based on [allauth](https://github.com/pennersr/django-allauth) 
package. 
While the [allauth](https://github.com/pennersr/django-allauth) is an
 amazing package that handles tons of providers for authentication, it is
 not trivial to customize it for REST usage.

In most of the cases we need'd only a few providers to integrate to our
 projects. For that reason the structure of the code is simplified, so
 that it could be easier to extend it for another provider.
 
### How does it work?
1. When the [login page](http://127.0.0.1:8000/accounts/google/login/) is
 visited the app redirects to [Google Signin](https://accounts.google.com/signin/oauth/)
2. After signing in the Google will redirect back based on the [callback](http://127.0.0.1:8000/accounts/google/login/callback) 
we setup. The callback url contains `code` parameter.
3. The `code` along with `key` and `secret` are used to get an `access_token`
4. Then the `access_token` is used to get basic user info defined in the
 scope. 
5. Retrieved data is parsed and an user is created/retrieved as below:
    1. First we check if the user already exists with this email address. If
     not:  Create a `User`, `SocialAccount` with that user and return
      the `User`,  otherwise:
    2. We check if `User` has a `SocialAccount`. If it does the `User`
     is returned otherwise `AccountExistError` is raised because of [this](https://github.com/pennersr/django-allauth/blob/master/allauth/socialaccount/adapter.py#L150).
6. In case of error the related error templates are rendered, otherwise we
 create `jwt` token for the current user and set it to the `AUTH_COOKIE_NAME` 
7. Redirect to `LOGIN_SUCCESS_URL` path.

### Authenticating requests
The requests are authenticated with `RestAuthentication` class.
It will authenticate the users either using authorization headers or cookies.

Example request:
```bash
curl -H "Authorization: Bearer <jwt_auth_token>" http://localhost:8000/your/protected/view
```

### Setup & Run

1. Download the source code and setup an virtualenv
    ```bash
    git clone https://github.com/shklqm/django-rest-google.git
    cd django-rest-google/
    mkdir env && virtualenv env/ -p python3
    ```
2. Install the requirements
    ```bash
    pip install -r requirements.pip
    ```
3. Get the `key` and `secret` at [google console](https://console.developers.google.com/apis/credentials)
    , set the [callback](http://127.0.0.1:8000/accounts/google/login/callback)
    and update the settings: 
    ```bash
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'your app key'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'your app secret'
    ```
4. Run migrations and the server
    ```bash
   ./manage.py migrate && ./manage.py runserver 
   ```

5. Visit [localhost](http://127.0.0.1:8000/accounts/google/login/) and try
 to login. Upon successful login you should be redirected to
  `LOGIN_SUCCESS_URL` path.
