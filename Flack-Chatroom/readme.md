# Project 2

Web Programming with Python and JavaScript

## Sitemap
* `application.py` - the back-end logic for the chatroom, with routes for pages and `socketio` events for joining and leaving a room, and emiting messages.
* |-- templates/
    * |-- `layout.html` - the layout for the `HTML` pages, with the navbar, left side menu (channels list and users list), and the main screen (for hosting the chat space and login/creating a new channel forms).
    * |-- `index.html` - the index file, where a user is invited to join or create a new channel after he has logged in with his username.
    * |-- `empty.html` - used after the first login, once the user has no channels to join. It invites the user to create a new channel.
    * |-- `error.html` - used for rendering error messages.
    * |-- `login.html` - used for first time users and logged out users to enable them to log in with a unique username.
    * |-- `channel.html` - used for rendering messages for a particular channel.
    * |-- `users.html` - used for rendering messages in private discussions
* |-- static/
    * |-- css/
        * |-- `style.scss` - Sass file used for styling the `HTML` documents
        * |-- `style.css.map`
        * |-- `style.css`
    * |-- img/
        * |-- `error.svg` - image used on the `error.html` file
        * |-- `flackLogo.svg` - image used as `Favicon`
    * |-- js/
        * |-- `channel.js` - `JS` file used to render messages in channels and handle events (such as entering and leaving a channel, and sending a new message)
        * |-- `users.js` - `JS` file used to render messages in private discussion
* `helper.py` - code snippet from CS50 2019 pset8 to require login on certain routes

## Checklist
[x] Display name
[x] Channel Creation
[x] Channel List
[x] Messages View
[x] Sending Messages
[x] Remembering the Channel
[x] Personal Touch - 1:1 messaging
[x] README file
