from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from datetime import datetime, timedelta
import requests
import random
import html
import threading

Window.maximize()

# colors used in the app
white = (0.949, 0.957, 0.988, 1)
blue = (0.502, 0.580, 0.867, 1)
green = (0.000, 0.592, 0.459, 1)
red = (0.957, 0.263, 0.212, 1)
light_green = (0.565, 0.933, 0.565, 1)

w = Window.width
h = Window.height


def main():
    QuizApp().run()


def get_token():
    # retrieve token and use it in a requests so that no questions are repeated
    token_url = "https://opentdb.com/api_token.php?command=request"
    token_response = requests.get(token_url, timeout=10)
    return token_response.json()["token"]


def get_questions(number_of_questions, category, token):
    questions_url = f"https://opentdb.com/api.php?amount={number_of_questions}&category={category}&type=multiple&token={token}"
    response = requests.get(questions_url, timeout=10)
    question_response = response.json()

    questions_data = []

    for item in question_response["results"]:
        answers = item["incorrect_answers"].copy()
        answers.append(item["correct_answer"])
        random.shuffle(answers)

        questions_data.append(
            {
                "question": item["question"],
                "answers": answers,
                "correct_answer": item["correct_answer"],
            }
        )
    return questions_data


def fix_encoding(response):
    return html.unescape(response)


# Configure the first welcome screen of the app
class Quiz_welcome(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical", spacing=h * 0.02, padding=[40, 0, 40, 40]
        )

        self.image = Image(
            source="KNOWITALL.png",
            size_hint=(1, None),
            height=h * 0.3,
            allow_stretch=True,
            keep_ratio=True,
        )

        self.spacer = Label(size_hint=(1, None), height=h * 0.15)

        self.label = Label(
            text="Select category",
            font_size=self.get_font_size(),
            color=green,
            size_hint=(1, None),
            height=h * 0.2,
            # pos_hint={"top": 0.65},
            halign="center",
            # valign="middle",
        )

        if platform == "android":
            grid = GridLayout(
                rows=4,
                spacing=20,
                padding=20,
                size_hint=(0.8, 0.3),
                pos_hint={"center_x": 0.5},
            )
        else:
            grid = GridLayout(
                cols=4,
                spacing=10,
                padding=20,
                size_hint=(0.8, 0.1),
                pos_hint={"center_x": 0.5},
            )

        self.categories = {
            "Sport": 21,
            "Music": 12,
            "History": 23,
            "Politics": 24,
        }

        for category in self.categories:
            cat_button = Button(
                text=category,
                font_size=self.get_font_size(),
                background_normal="",
                background_color=blue,
                on_press=self.on_cat_click,
            )
            grid.add_widget(cat_button)

        self.start_button = Button(
            text="Start quiz",
            font_size=self.get_font_size(),
            size_hint=self.get_button_size(),
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=green,
            bold=True,
            on_release=self.to_next_screen,
        )

        layout.add_widget(self.image)
        layout.add_widget(self.label)
        layout.add_widget(grid)
        layout.add_widget(self.spacer)
        layout.add_widget(self.start_button)

        self.add_widget(layout)
        self.label.bind(size=self.label.setter("text_size"))
        Window.bind(
            size=lambda instance, value: setattr(
                self.label, "font_size", self.get_font_size()
            )
        )

        self.number_of_questions = 10

    def get_font_size(self):
        if platform == "android":
            return w * 0.05
        else:
            return w * 0.04

    def get_button_size(self):
        if platform == "android":
            return (0.4, 0.12)
        else:
            return (0.3, 0.12)

    def on_cat_click(self, instance):
        selected = instance.text
        self.start_button.text = f"Start quiz on {selected}"
        self.start_button.size_hint = (0.6, 0.12)

        # check if token already exists and if it's older than 6 hours
        def check_token():
            if hasattr(self, "token") and hasattr(self, "token_time"):
                time_of_check = datetime.now()
                token_age = time_of_check - self.token_time
                if token_age > timedelta(hours=6):
                    token = get_token()
                    token_time = datetime.now()
                else:
                    token = self.token
                    token_time = self.token_time
            else:
                token = get_token()
                token_time = datetime.now()

            Clock.schedule_once(lambda dt: setattr(self, "token", token))
            Clock.schedule_once(lambda dt: setattr(self, "token_time", token_time))

        # save the category code so I can use it in the API
        self.selected_category_code = self.categories[selected]

        # fetch token in the background thread
        threading.Thread(target=check_token).start()

    def to_next_screen(self, instance):
        if not hasattr(self, "token"):
            return

        def fetch_questions():
            # call an API to fetch questions before switching screens
            self.questions_data = get_questions(
                self.number_of_questions, self.selected_category_code, self.token
            )

            def call_build_ui(dt):
                questions_screen = self.manager.get_screen("Questions screen")
                questions_screen.build_ui()
                self.manager.current = "Questions screen"

            Clock.schedule_once(call_build_ui)

        threading.Thread(target=fetch_questions).start()


# Configure second screen of the app where the questions are shown
class Quiz_questions(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.total_points = 0
        self.current_index = 0
        self.master = BoxLayout(orientation="vertical", spacing=1, padding=60)

        if platform == "android":
            self.q_grid = GridLayout(
                rows=4,
                spacing=50,
                padding=20,
                size_hint=(0.8, 0.3),
                pos_hint={"top": 0.5, "center_x": 0.5},
            )
        else:
            self.q_grid = GridLayout(
                cols=2,
                spacing=50,
                padding=30,
                size_hint=(0.8, 0.2),
                pos_hint={"top": 0.5, "center_x": 0.5},
            )

        self.add_widget(self.master)

    def build_ui(self):
        self.welcome_screen = self.manager.get_screen("Welcome screen")
        # initializing the data for the first question
        self.current_question_data = self.welcome_screen.questions_data[
            self.current_index
        ]
        self.current_question = fix_encoding(self.current_question_data["question"])
        self.current_answers = self.current_question_data["answers"]

        self.ques_num = Label(
            text=f"Question {self.current_index + 1}",
            font_size=self.welcome_screen.get_font_size(),
            color=green,
            size_hint=(1, 0.01),
            # height=h*0.2,
            pos_hint={"top": 0.9, "center_x": 0.5},
            halign="center",
            valign="middle",
            padding=(20, 0),
        )

        self.question = Label(
            text=self.current_question,
            font_size=self.welcome_screen.get_font_size(),
            color=blue,
            size_hint=(1, 0.2),
            # height=h*0.2,
            pos_hint={"top": 0.8, "center_x": 0.5},
            halign="center",
            valign="middle",
            padding=(20, 0),
        )

        # lambda function that makes my question label to dynamically resize and go to multiline
        self.question.bind(
            size=lambda instance, size: setattr(
                self.question, "text_size", ((size[0] - 40), None)
            )
        )

        self.master.add_widget(self.ques_num)
        self.master.add_widget(self.question)
        self.master.add_widget(self.q_grid)

        # creating list with button instances so I can iterate through it to replace the text label on all of them in the answer_clicked()
        self.answer_buttons = []
        for answer in self.current_answers:
            self.btn = Button(
                text=fix_encoding(answer),
                font_size=self.welcome_screen.get_font_size(),
                background_normal="",
                background_color=green,
                bold=False,
                on_press=self.answer_clicked,
            )
            self.answer_buttons.append(self.btn)
            self.q_grid.add_widget(self.btn)

        self.button_clicked = False

    def answer_clicked(self, instance):
        self.welcome_screen = self.manager.get_screen("Welcome screen")
        correct_answer = self.current_question_data["correct_answer"]

        if not self.button_clicked:
            self.button_clicked = True

            if instance.text == correct_answer:
                self.total_points += 1
                instance.background_color = light_green
            elif instance.text != correct_answer:
                instance.background_color = red
                for btn in self.answer_buttons:
                    if btn.text == correct_answer:
                        btn.background_color = light_green

            self.current_index += 1

            def next_question(dt):
                if self.current_index >= len(self.welcome_screen.questions_data):
                    self.master.remove_widget(self.q_grid)
                    self.master.remove_widget(self.ques_num)
                    self.question.text = f"Your total score is {self.total_points}/10!"
                    self.play_again = Button(
                        text="Play again",
                        font_size=self.welcome_screen.get_font_size(),
                        background_normal="",
                        background_color=green,
                        size_hint=self.welcome_screen.get_button_size(),
                        pos_hint={"top": 0.45, "center_x": 0.5},
                        bold=True,
                        on_release=self.restart_game,
                    )
                    self.master.add_widget(self.play_again)
                    return
                else:
                    self.button_clicked = False
                    # fetching new data for new questions
                    self.current_question_data = fix_encoding(
                        self.welcome_screen.questions_data[self.current_index]
                    )
                    self.current_question = fix_encoding(
                        self.current_question_data["question"]
                    )
                    self.current_answers = self.current_question_data["answers"]

                    # updating text for every widget on the page with the current question data
                    for i in range(4):
                        answer = self.current_answers[i]
                        self.answer_buttons[i].text = fix_encoding(answer)
                    self.question.text = self.current_question
                    self.ques_num.text = f"Question {self.current_index + 1}"
                    for btn in self.answer_buttons:
                        btn.background_color = green

            Clock.schedule_once(next_question, 0.8)
        else:
            pass

    def restart_game(self, instance):
        self.total_points = 0
        self.current_index = 0
        self.answer_buttons = []
        self.master.clear_widgets()
        self.q_grid.clear_widgets()
        self.welcome_screen.start_button.text = "Start quiz"
        self.manager.current = "Welcome screen"


class QuizApp(App):
    def build(self):
        Window.clearcolor = white
        sm = ScreenManager()
        sm.add_widget(Quiz_welcome(name="Welcome screen"))
        sm.add_widget(Quiz_questions(name="Questions screen"))

        return sm


if __name__ == "__main__":
    main()
