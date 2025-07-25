from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.core.window import Window
import requests
import random
import html
from pyfiglet import Figlet

Window.size = (800, 600)

# colors used in the app
white = (0.949, 0.957, 0.988, 1)
blue = (0.502, 0.580, 0.867, 1)
green = (0.000, 0.592, 0.459, 1)


def main():
    figlet = Figlet()

    figlet.setFont(font="larry3d")
    text = "KnowItAll"

    print(figlet.renderText(text))

    QuizApp().run()


def get_token():
    # retrieve token and use it in a requests so that no questions are repeated
    token_url = "https://opentdb.com/api_token.php?command=request"
    token_response = requests.get(token_url)
    return token_response.json()["token"]


def get_questions(number_of_questions, category, token):
    questions_url = f"https://opentdb.com/api.php?amount={number_of_questions}&category={category}&type=multiple&token={token}"
    response = requests.get(questions_url)
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
    user_friendly_output = html.unescape(response)
    return user_friendly_output


# Configure the first welcome screen of the app
class Quiz_welcome(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.image = Image(
            source="KNOWITALL.png", size_hint=(1, 0.4), height=300, pos_hint={"top": 1}
        )

        self.label = Label(
            text="Select category",
            font_size=Window.height * 0.04,
            color=green,
            size_hint=(1, None),
            height=50,
            pos_hint={"top": 0.65},
            halign="center",
            valign="middle",
        )

        grid = GridLayout(
            cols=4,
            spacing=10,
            padding=20,
            size_hint=(0.8, 0.1),
            size=(600, 100),
            pos_hint={"top": 0.6, "center_x": 0.5},
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
                font_size=30,
                background_normal="",
                background_color=blue,
                on_press=self.on_cat_click,
            )
            grid.add_widget(cat_button)

        self.start_button = Button(
            text="Start quiz",
            font_size=40,
            size_hint=(0.3, 0.12),
            size=(200, 110),
            pos_hint={"top": 0.4, "center_x": 0.5},
            background_normal="",
            background_color=green,
            bold=True,
            on_release=self.to_next_screen,
        )

        self.add_widget(self.image)
        self.add_widget(self.label)
        self.label.bind(size=self.label.setter("text_size"))
        Window.bind(
            size=lambda instance, value: setattr(
                self.label, "font_size", Window.height * 0.04
            )
        )
        self.add_widget(grid)
        self.add_widget(self.start_button)

        self.number_of_questions = 10

    def on_cat_click(self, instance):
        selected = instance.text
        self.start_button.text = f"Start quiz on {selected}"
        self.start_button.size_hint = (0.4, 0.12)
        # save the category code so I can use it in the API
        self.selected_category_code = self.categories[selected]
        self.token = get_token()

    def to_next_screen(self, instance):
        questions_screen = self.manager.get_screen("Questions screen")
        # call an API to fetch questions before switching screens
        self.questions_data = get_questions(
            self.number_of_questions, self.selected_category_code, self.token
        )
        questions_screen.build_ui()
        self.manager.current = "Questions screen"


# Configure second screen of the app where the questions are shown
class Quiz_questions(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.total_points = 0
        self.current_index = 0
        self.master = BoxLayout(orientation="vertical", spacing=1, padding=60)
        self.q_grid = GridLayout(
            cols=2,
            spacing=50,
            padding=30,
            size_hint=(0.8, 0.2),
            size=(600, 100),
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
            font_size=Window.height * 0.05,
            color=green,
            size_hint=(1, 0.01),
            height=20,
            pos_hint={"top": 0.9, "center_x": 0.5},
            halign="center",
            valign="middle",
            padding=(20, 0),
        )

        self.question = Label(
            text=self.current_question,
            font_size=Window.height * 0.04,
            color=blue,
            size_hint=(1, 0.2),
            height=50,
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
                font_size=30,
                background_normal="",
                background_color=green,
                bold=False,
                on_press=self.answer_clicked,
            )
            self.answer_buttons.append(self.btn)
            self.q_grid.add_widget(self.btn)

    def answer_clicked(self, instance):
        self.welcome_screen = self.manager.get_screen("Welcome screen")
        # if answer is correct do something
        if instance.text == self.current_question_data["correct_answer"]:
            self.total_points += 1

        self.current_index += 1
        if self.current_index >= len(self.welcome_screen.questions_data):
            self.master.remove_widget(self.q_grid)
            self.master.remove_widget(self.ques_num)
            self.question.text = f"Your total score is {self.total_points}/10!"
            self.play_again = Button(
                text="Play again",
                font_size=30,
                background_normal="",
                background_color=green,
                size_hint=(0.4, 0.05),
                height=100,
                pos_hint={"top": 0.45, "center_x": 0.5},
                bold=True,
                on_release=self.restart_game,
            )
            self.master.add_widget(self.play_again)
            return
        else:
            # fetching new data for new questions
            self.current_question_data = fix_encoding(
                self.welcome_screen.questions_data[self.current_index]
            )
            self.current_question = fix_encoding(self.current_question_data["question"])
            self.current_answers = self.current_question_data["answers"]

            # updating text for every widget on the page with the current question data
            for i in range(4):
                answer = self.current_answers[i]
                self.answer_buttons[i].text = fix_encoding(answer)
            self.question.text = self.current_question
            self.ques_num.text = f"Question {self.current_index + 1}"

    def restart_game(self, instance):
        self.total_points = 0
        self.current_index = 0
        self.answer_buttons = []
        self.master.clear_widgets()
        self.q_grid.clear_widgets()
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
