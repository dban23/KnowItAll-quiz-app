# KnowItAll Quiz App
#### Video Demo: [KnowItAll demo](my.url.com/video_of_app)
### Description:
Hi, my name is David and for my last project for CS50P I decided to make a quiz app. It is called KnowItAll.

I made it using Kivy framework because with this project I wanted to learn more about developing an app for both computers and phones. The entire GUI is written in Python rather than .kv files, since the core goal of this course is Python development. :)

In short, it fetches live trivia questions from the Open Trivia Database API, offers category-based gameplay with multiple choice questions and tracks user progress.

### File overview:
    - KNOWITALL.png -> logo of the app used on the GUI
    - project.py -> main application source code
    - README.md -> the file you're (hopefully) reading
    - requirements.txt -> all pip-installable libraries required for the app
    - test_project.py -> code used for validation of the core functions

### Let's dive in!
As previously said, after running the app, the first thing you can see in the terminal is the app name written in ASCII art. It's just a small fun addition to start the project. After that, the main app screen will be opened. On that screen, you'll see several widgets that are, as already written, made with the Kivy framework.

#### *Welcome screen*
From the top, there is an app logo, "Select category" label along with the four buttons used to choose the said categories, and at the bottom there is a "Start quiz" button. Once a category is selected, the Start Quiz button updates to read:
>"Start quiz on {category}".

App currently lets you choose between only 4 categories: Sport, Music, History and Politics. The plan is to eventually update this with more categories to choose, maybe in the form of a drop-down menu.

One thing that the first screen currently doesn't have is a widget to choose the difficulty of the questions. At the moment, this is hard-coded to a medium difficulty. And as with the categories widget, the plan for the future is to update this first screen to allow users to choose the difficulty of the questions to give users a bit more flexibility in the app itself.

Clicking the button "Start quiz on {category}", the app will lead you to the second screen where the questions are given.

#### *Questions screen*
The second screen also includes several widgets: the number of the question you're answering to, the question itself and the 4 possible answers, from which only one is correct.

After the user clicks the answer which he thinks is correct, a new question and set of answers will appear — all widgets are dynamically updated when a choice is made.

The quiz itself consists of 10 questions and after the last question is answered, the user will see the final screen where the total score will be shown:
>("eg. Your total score is 5/10!")

At the bottom of the screen user will see a "Play again" button that, when clicked, returns the user to the first "Welcome screen" from where new quiz can be started.

### Source code

#### *main() and three custom functions*
At the start of the code, after importing all of the needed libraries, there is a *main function* whose purpose in life is to print out ASCII art in the terminal and, more importantly, to run the QuizApp.

After that, there are two functions *get_token* and *get_questions*. They, with the help of the *requests* library (GET requests), fetch the token and questions needed in the later stage of the code. The former is fairly simple but important so that no questions are repeated for the user and the latter is a bit more complicated.

It takes three inputs: the number of questions that need to be fetched (currently hard-coded as 10), category that user chooses and token fetched with the previous function. That function then takes response from the API call and transforms it into a list of dictionaries with the important keys: question, answers and correct answer.

Third special function is *fix_encoding* which is using *html* library to unescape special characters that could be encoded in the questions or answers that are fetched from the Open trivia DB so that they are in the readable format.

#### *Kivy classes*
Second, longer and more complicated part of the code, consists of three classes. Two that are used to configure app GUI and special methods, and third, main one, that is used to connect everything into a single flow.

The first class is responsible for the creation of the welcome screen and all widgets that are on there. In there, you can find the hardcoded number of questions variable and two special methods:

    - on_cat_click -> defines what happens after user clicks one of the category button

    - to_next_screen -> defines what happens when user clicks "Start quiz" button. It calls *get_question()*, calls *build_ui()* function from the second class and then takes user to the next screen

The second class is responsible for the second screen - "Questions screen". After initializing second class, three other methods can be seen. The first one - *build_ui* is responsible for building all of the widgets on the second screen (questions and the answers) and initializing question data for the first question.

After that one I use *answer_clicked* method to always fetch the current question and answers - based on the current index which increments every time the answer is clicked. It then assigns that question data to the label and button widgets. After all of the questions are answered, this method removes buttons and question number widgets from the screen, and shows user's total score and displays a button to restart the quiz from the beginning.

Last method in the second class - *restart_game* is used to restart the important instance variables, clear all of the widgets and returns to the "Welcome screen". Because of that, user can start every quiz with a clean slate.

Third and final class *QuizApp* is the one where *build()* method could be found. The one that Kivy looks for when *.run()* on the app is called. It connects all of the screens used in the app.
