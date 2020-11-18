# Project 1

Web Programming with Python and JavaScript

## User Behavior:
* User can register or login either from the buttons on the Homepage or through the navbar
* If valid, user credentials will be stored into users table in the db
* If duplicated, user gets an error message and an error code, and is redirected to `error.html`
* Once inside, the user is redirected to the `dashboard.html` where he can search a book by author, title, or ISBN
* Any partial input will return all the matching results
* The results are displayed as a table, also with a link that redirects to the book page
* On the book page, the user can see the details of the book, any existent reviews, and he can leave a review

## Front-end:
* the UI is done with Bootstrap 4 (some of the classes are overridden with SASS).
* all the website images are from `https://undraw.co/`.
* all the book covers are from `http://covers.openlibrary.org`

## Back-end:
* the logic of the application is written in python - flask framework

## Sitemap:
* `application.py`
     * main application file
     * defining routes for all the HTML pages
     * defining the API the user can call at `../api/` plus the ISBN code of a book 
* `helpers.py` 
     * code from CS50 2019 pset8 to require login on certain routes
* `import.py` 
     * function that reads `books.csv`, skips the first row (header row) and imports the rest into the books table in the db
* `templates/`
     * `layout.html` 
          * the layout for the web application
     * `index.html` 
          * the homepage, which will change the navbar and CTA info based on whether the user is logged in or not
     * `login.html` 
          * the login page
          * has `.js` code to prevent browser-side the user to leave the required fields empty
     * `register.html`
          * the registration page
          * has `.js` code to prevent browser-side the user to leave the required fields empty
     * `error.html` 
          * the error page, where the user will be redirected in case of an error (e.g. username already existing)
     * `dashboard.html`
          * the dashboard page which serves as a default page for the users that are logging in / registering
          * the users will use this page to search for a book
     * `result.html`
          * the page where the user will see the results of the book search
     * `book.html`
          * the UI of the book page
          * book cover images are from `http://covers.openlibrary.org`
* `static/`
     * `images/`
          * folder with all the images from `https://undraw.co/`
     * `styles.scss` 
          * CSS code for the HTML pages
     * `styles.css.map` & `styles.css` 
          * stlesheet code generated after compilation from the terminal
