import atexit
from typing import Union
import os
import pickle
import re
import sys
from termcolor import colored


def enter(prompt: str) -> str:
    try:
        res = input("\n\n{}> ".format(prompt + " "))
        if res == "exit":
            exit(0)
        else:
            return res
    except KeyboardInterrupt:
        exit(0)


class Question:
    def __init__(self, prompt: str, answers: list[str], correct_answer: list[str]):
        self.prompt = prompt
        self.answers = answers
        self.correct_answer = correct_answer

    def print_question(self):
        print(self.prompt)
        for i in range(len(self.answers)):
            print(self.answers[i])

    def check_answer(self, answer):
        if isinstance(self.correct_answer, list):
            if answer in self.correct_answer:
                return True
            else:
                return False


class Chapter:
    def __init__(self, number: int, questions: list[Question]):
        self.number = number
        self.questions = questions
        self.result = []
        self.score = 0
        self.current_question: int = 0
        self.max_score = 0

        for question in questions:
            self.max_score += len(question.correct_answer)

    def run(self, current: Union[int, bool] = 0):
        print("\n\n\tWelcome to Chapter {}!\n".format(self.number))
        if isinstance(current, int):
            from_question = current
        elif current:
            from_question = self.current_question
        else:
            from_question = 0

        for question in (self.questions[from_question:]):
            self.current_question = self.questions.index(question)
            print(colored("\n\n" + question.prompt, attrs=["bold"]))
            for answer in question.answers:
                print(colored("> {}".format(answer)))
            entered_answers = re.split(" | ,", enter(
                f'Enter your answer ({len(question.correct_answer)})').lower().strip())
            for answer in entered_answers:
                if question.check_answer(answer):
                    self.result.append([question, answer, True])
                    self.score += 1
                else:
                    self.result.append([question, answer, False])
            print(colored("\n\nYour score: {}/{}".format(self.score,
                  self.max_score), self.determine_color()))

    def determine_color(self):
        if self.score == self.max_score:
            return "green"
        elif self.score > 0:
            return "yellow"
        else:
            return "red"


class Quiz:

    def __init__(self, chapters: list[Chapter], quiz_taker: str):
        self.quiz_taker = colored(quiz_taker, "blue", attrs=["bold"])
        self.chapters = chapters
        self.current_chapter = 0
        self.current_question = 0
        self.score = 0

    def run(self):
        atexit.register(quiz.save)
        print(
            f"\n\n\tWelcome {self.quiz_taker} to the quiz! \n\tYour score is saved upon exit.\n\n")

        if self.current_chapter != 0:  # Promt user to continue from last chapter
            print(colored("\n\n\tPick up where you left off? (Chapter {})\n\n".format(
                self.current_chapter), "green"))
            choice = enter("y/n")
            if choice == "y":
                self.chapters[self.current_chapter].run(True)  # Run chapter

        while True:
            print(colored("\n\nSelect chapter: ", attrs=["bold"]))
            for chapter in self.chapters:

                print(
                    colored(f"> Chapter {chapter.number}", chapter.determine_color()))
            choice = enter("Chapter")
            try:
                choice = int((re.findall(r'\d+', choice)[0])) - 1
            except TypeError:
                continue
            # run chapter
            if choice > len(self.chapters) or choice < 0:
                print(colored("\n\tInvalid chapter number!\n", "red"))
                continue

            self.current_chapter = choice  # set current chapter
            self.chapters[choice].run()  # run chapter

    def save(self):
        pickle.dump(self, open("quiz.p", "wb"))  # save quiz
        print(colored("\n\n\tYour score has been saved.\n\n", "green"))

    def stop(self):
        # To be implemented
        pass


def getChapters(file_name: str):
    """Fetch chapters and questions from a text file

    Args:
        file_name (str): Name of the text file

    Returns:
        list[Chapter]: List of Chapter objects
    """
    chapter_list: list[Chapter] = []
    with open(file_name, "r") as f:
        lines = f.readlines()

        chapter_questions: list[Question] = []
        question_prompt: str = ""
        question_answers: list[str] = []
        question_correct_answers: list[str] = []

        question_active: bool = False
        empty_line_count = 0
        line_count = 0
        for line in lines:
            line_count += 1
            # if line is empty continue
            if line == "\n":
                empty_line_count += 1
                print("empty line {}".format(empty_line_count))
                continue

            if line.startswith("Chapter"):
                print("New chapter")
                if chapter_questions:
                    chapter_list.append(
                        Chapter(num, chapter_questions))
                    chapter_questions = []
                try:
                    num = int(line[8:])
                except ValueError:
                    print("Error: Chapter number must be a number")
                    num = 0
            elif line[0].isdigit() and (line[1] == "." or line[2] == "."):
                print("New question")
                if question_answers and question_prompt:  # new question
                    chapter_questions.append(
                        Question(question_prompt, question_answers, question_correct_answers))
                    question_prompt = ""
                    question_answers = []
                    question_correct_answers = []

                question_prompt = line.strip()
                question_active = True
            elif line[0].isalpha() and line[1] == ".":
                line = line.strip()
                question_active = False
                print("New answer")
                if line[0].isupper():
                    question_correct_answers.append(line[0])
                    line = line[0].lower() + line[1:]
                question_answers.append(line)
            elif question_active:
                question_prompt += line
            else:
                print(line)
        if chapter_questions:
            chapter_list.append(Chapter(num, chapter_questions))
        # print out chapters and questions
        print("\nLines: {}".format(line_count))
        print("Chapters {}\n\n".format(len(chapter_list)))
        print(colored("Loaded successfully!\n\n", "green", attrs=["bold"]))
        with open("chapters.p", "wb") as f:
            pickle.dump(chapter_list, f)
        return chapter_list


def getSave():
    """Get previous save

    Returns:
        Quiz | None: Quiz object or None if no save found
    """
    if os.path.exists("quiz.p"):
        with open("quiz.p", "rb") as f:
            return pickle.load(f)


def retrieveChapters():
    """Fetches chapters from a pickle file or creates a new one

    Returns:
        list[Chapter]: List of Chapter objects
    """
    if os.path.exists("chapters.p"):
        with open("chapters.p", "rb") as f:
            return pickle.load(f)
    elif os.path.exists("questions.txt"):
        return getChapters("questions.txt")
    else:
        print(
            colored("No chapters or questions found. \nMake sure questions.txt is availible.", "red"))
        exit(1)


if __name__ == "__main__":
    if "--reset" in sys.argv:
        os.path.exists("quiz.p") and os.remove("quiz.p")
        os.path.exists("chapters.p") and os.remove("chapters.p")
    if "--update" in sys.argv:
        chapters = getChapters("questions.txt")

    quiz = getSave()

    if not quiz:
        chapters = retrieveChapters()
        print(colored("What's your name?", "blue"))
        name = enter("Name")
        quiz = Quiz(chapters, name or "John Doe")

    quiz.run()
