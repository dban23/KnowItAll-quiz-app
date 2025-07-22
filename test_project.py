from project import get_token, get_questions, fix_encoding, QuizApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window


# test that my main function is creating screens for the app
def test_main():
    app = QuizApp()
    sm = app.build()

    assert isinstance(sm, ScreenManager) == True
    assert "Welcome screen" in sm.screen_names
    assert "Questions screen" in sm.screen_names
    assert Window.clearcolor == [0.949, 0.957, 0.988, 1]


# testing that my token is created and is of type str
def test_get_token():
    token = get_token()
    assert isinstance(token, str) == True
    assert token != ""


# testing that my questions are in the proper format and that function returnes the correct amount of questions
def test_get_questions():
    token = get_token()
    response = get_questions(10, 21, token)
    answers1_list = response[1]["answers"]
    correct_ans1 = response[1]["correct_answer"]

    assert isinstance(response, list) == True
    assert len(response) == 10
    assert response != []

    assert isinstance(answers1_list, list) == True
    assert len(answers1_list) == 4
    assert answers1_list != []

    assert isinstance(correct_ans1, str) == True


# testing if the strings are properly encoded on the UI
def test_fix_encoding():
    assert fix_encoding("&#039;The Professor&#039;") == "'The Professor'"
    assert (
        fix_encoding("Who won the &quot;Champions League&quot; in 1999?")
        == 'Who won the "Champions League" in 1999?'
    )
    assert fix_encoding("Test &amp; test &amp; test...") == "Test & test & test..."
