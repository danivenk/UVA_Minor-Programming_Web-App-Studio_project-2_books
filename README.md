# books

This webapp contains a book database in which you can review those books. You can only review a book once and to search for the books and review you need to be logged on.

functions:
  * import.py:
      can be run to initialize the database and add all books from books.csv
  * security.py:
      defines 2 functions, a function to hash a password (salt embedded) and a function to compare a hashed password (from the hash function in the same file) and a password

static:
  * css:
      contains the css of the webapp (css, scss, css.map)
  * js:
    * javascript.js:
        checks all forms on the page and gives the validation
  * img:
      contians the icon of the webapp, source: https://gamepedia.cursecdn.com/minecraft_gamepedia/f/f3/Book.png

templates:
  the html pages extend layout.html
  * book.html:
      contains the bookpage for the webapp, it has the title of the book, the book data, ratings if available, reviews if available and the possibility to write a review
  * error.html:
      contains the error page of the webapp, it has the header of the error and the message of the error
  * index.html:
      contains the homepage of the webapp, it has Home in the title and has a short writeup of the project.
  * layout.html:
      contains the framework of the webapp pages, it has the title like Project 2 - (page title), the navbar is automatically created by the application.py. It has a dropdown for the login form, where you can also find the link to sign up.
  * register.html:
      contains the register page of the webapp, it has Register in the title and contains the register form where you need to specify a username and a password, you must also retype the password.
  * search.html:
      contains the search page of the webapp, it has Search in the title and has the search bar, below it are the results.

application.py:
  * setup_urls()
      setups all the url enpoints and titles for the navbar. It gets all "GET" registered routes from the app and filters the log/static/register/api/book endpoints out and defines the search for login only. Finally it adds the url_list to the session

      ***REMARK:** I used the nav items this way because here I only need to add/remove stuff in the forbidden and login_req lists to get the correct items in the navbar. The TA told me it was maybe easier if I did it different but since there was not much time left I could leave it like this*
  * index()
      renders the homepage (depending on login status)
  * register()
      renders the register form. If posted, it adds the user to the database
  * login()
      only if posted, it checks with database if user login details are correct. If so add user to session
  * logout()
      logout if logged in, remove user from session
  * search()
      get user query (word for word), search in database and render result

      ***REMARK:** The query will be split word for word*
  * goodreads_api()
      gets the average rating and review count from goodreads when given the api url
  * book()
      renders bookpage of isbn if "GET" request and adds review to database if "POST" request
  * api()
      renders json style api page of isbn
  * errorhandler()
      renders error page when HTTPException is catched

books.csv:
  contians all books to be added to database

requirements.txt:
  contains all modules required for app

remarks:
  * don't know if I have to add the security module in functions directory to requirements.txt so I have not done that.

Personal Touch:
  * One place to update the navigation bar from and specify there what items to display when logged on or not, it uses the endpoints registered in the application
  * The ability to search for multiple queries at the same time, for example when "Micheal Grant" is searched it queries "michael" and "grant"
      it searches than for first "micheal" in authors or in isbn after moving on to the next query.