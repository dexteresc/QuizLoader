import atexit
import os
import pickle
import sys
from typing import Union

from termcolor import colored
from InquirerPy import prompt as prompt_inquirer

SHOW_SCORE = True


def prompter(prompt_type: str, prompt: str, choices: list[str] = None,  options: dict = None):
    """Prompt user with InquirerPy

    Args:
        type (str): Type of prompt
        prompt (str): Prompt text
        choices (list[str], optional): List of choices. Defaults to None.
        options (dict, optional): Options for InquirerPy. Defaults to None.
    """
    try:
        question = {
            "type": prompt_type,
            "message": prompt,
        }
        if choices:
            question["choices"] = choices
        if options:
            question.update(options)
        return prompt_inquirer(question)
    except KeyboardInterrupt:
        sys.exit(0)


class Question:
    """Question class that contains a prompt, a list of answers, and a list of correct answers"""

    def __init__(self, prompt: str, answers: list[str], correct_answers: list[str]):
        self.prompt = prompt
        self.answers = answers
        self.correct_answers = correct_answers

    def check_answer(self, answer: list[str]) -> bool:
        """Check if the answer is correct

        Args:
            answer (str): User input

        Returns:
            bool: True if correct, False if incorrect
        """
        return answer in self.correct_answers

    def print_question(self) -> None:
        """Print the question"""
        print(colored(self.prompt, "green"))
        for i, answer in enumerate(self.answers):
            print(f"{i + 1}. {answer}")


class Chapter:
    """Chapter class that contains the chapter number, a list of questions, and a list of results"""

    def __init__(self, number: int, questions: list[Question]):
        self.number = number
        self.questions = questions
        self.score = 0
        self.current_question: int = 0
        self.max_score = 0

        for question in questions:
            self.max_score += len(question.correct_answers)

    def run(self, current: Union[int, bool] = 0):
        """Runs a quiz for the chapter

        Args:
            current (Union[int, bool], optional): If quiz should start at current question or not.
            Defaults to No.
        """
        print(f"\n\n\tWelcome to Chapter {self.number}!\n")
        if isinstance(current, int):
            from_question = current
        elif current:
            from_question = self.current_question
        else:
            from_question = 0

        for question in self.questions[from_question:]:
            if len(question.correct_answers) > 1:
                try:
                    answers = prompter("checkbox", question.prompt, question.answers, {
                        "validate": lambda answer, ca_len=len(question.correct_answers):
                            len(answer) == ca_len,
                        "invalid_message":
                            f"Please select {len(question.correct_answers)} answers",
                        "transformer": lambda answers: "\n" + "\n".join(answers),
                        "filter": lambda answers: [answer[0] for answer in answers]
                    })[0]
                except KeyboardInterrupt:
                    sys.exit(0)
            else:
                try:
                    answers = prompter(
                        "list", question.prompt, question.answers,
                        options={
                            "transformer": lambda answer: "\n" + answer,
                            "filter": lambda answer: answer[0]
                        })[0]
                except KeyboardInterrupt:
                    sys.exit(0)
            # Check if the answer is correct
            if answers == question.correct_answers:
                self.score += len(question.correct_answers)
                if SHOW_SCORE:
                    print(colored("Correct!", "green"))
            elif SHOW_SCORE:
                print(colored("Incorrect!", "red"))
            print()

    def determine_color(self):
        """Determines the color of the score

        Returns:
            str: Color of the score
        """
        if self.score == self.max_score:
            return "green"
        elif self.score > 0:
            return "yellow"
        else:
            return "red"


class Quiz:
    """Quiz class that contains a list of chapters,
    current chapter, name of the quiz taker, and total score"""

    def __init__(self, chapters: list[Chapter]):
        self.quiz_taker = ""
        self.chapters = chapters
        self.current_chapter = 0
        self.score = 0

    def run(self):
        """Runs the quiz"""
        atexit.register(quiz.save)
        if not self.quiz_taker:
            self.quiz_taker = prompter("input", "What's your name?", options={
                "validate": lambda name: name != "" and len(name) < 20})[0]
        print(
            f"\n\n\tWelcome {colored(self.quiz_taker, 'magenta')} to the quiz! \n\tYour score is saved upon exit.\n\n")

        if self.current_chapter != 0:  # Promt user to continue from last chapter
            pick_up = prompter(
                "confirm", "Continue from last chapter?")[0]

            if pick_up:
                self.chapters[self.current_chapter].run(True)  # Run chapter

        while True:
            choice: int = prompter("list", "Select chapter: ", [
                f"Chapter {chapter.number} ({chapter.score}/{chapter.max_score})" for chapter in self.chapters],
                options={"filter": lambda choice: int(choice.split(" ")[1])})[0]
            print("choice:", choice)
            self.current_chapter = choice  # set current chapter
            self.chapters[choice-1].run()  # run chapter

    def save(self):
        """Saves the quiz to a file"""
        with open("quiz.p", "wb") as file:
            pickle.dump(self, file)
        print(colored("\n\n\tYour score has been saved.\n\n", "green"))

    def stop(self):
        """To be implemented"""

    def reset(self):
        """Resets the quiz"""
        for chapter in self.chapters:
            chapter.score = 0
            chapter.current_question = 0
            chapter.result = []
        self.score = 0
        self.quiz_taker = ""
        self.current_chapter = 0


def get_chapters(file_name: str):
    """Fetch chapters and questions from a text file

    Args:
        file_name (str): Name of the text file

    Returns:
        list[Chapter]: List of Chapter objects
    """
    chapter_list: list[Chapter] = []
    with open(file_name, "r", encoding="utf-8") as file:
        lines = file.readlines()

        chapter_questions: list[Question] = []
        question_prompt: str = ""
        question_answers: list[str] = []
        question_correct_answers: list[str] = []

        question_active: bool = False
        line_count = 0
        for line in lines:
            line_count += 1
            # if line is empty continue
            if line == "\n":
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
                    question_correct_answers.append(line[0].lower())
                    line = line[0].lower() + line[1:]
                question_answers.append(line)
            elif question_active:
                question_prompt += line
            else:
                print(line)
        if chapter_questions:
            chapter_list.append(Chapter(num, chapter_questions))
        # print out chapters and questions
        print(f"\nLines: {line_count}")
        print(f"Chapters {len(chapter_list)}\n\n")
        print(colored("Loaded successfully!\n\n", "green", attrs=["bold"]))

        return chapter_list


def get_save():
    """Get previous save

    Returns:
        Quiz | None: Quiz object or None if no save found
    """
    if os.path.exists("quiz.p"):
        with open("quiz.p", "rb") as file:
            try:
                return pickle.load(file)
            except (pickle.UnpicklingError, EOFError):
                print(colored("\n\n\tError: Save file is corrupted\n\n",
                      "red", attrs=["bold"]))
                return None
    else:
        return None


def search_questions(quiz_chapters: list[Chapter], question_prompt: str):
    """Search for a question in a list of chapters

    Args:
        chapters (list[Chapter]): List of Chapter objects
        question_prompt (str): Question prompt
    """
    found_questions = []
    print(
        colored(f"Searching for: {colored(question_prompt, 'magenta')}", 'blue'))
    for chapter in quiz_chapters:
        for question in chapter.questions:
            if question_prompt.lower() in question.prompt.lower():
                found_questions.append({
                    "chapter": chapter.number,
                    "question": question
                })
    if len(found_questions) == 0:
        print(colored("No questions found!", "red"))
    else:
        print(colored(f"Found {len(found_questions)} questions:", "green"))
        for question in found_questions:
            print(colored(f"\nChapter {question['chapter']}", "green"))
            print(f"{question['question'].prompt}")
            for answer in question["question"].answers:
                print(colored(f"\t{answer}", "yellow"))
            print(colored(
                f'Correct answers: {" ".join(question["question"].correct_answers)}', "green"))


if __name__ == "__main__":
    question_path = "questions.txt"  # pylint: disable=invalid-name
    # Check for questions file
    if (not os.path.exists(question_path)) or (not os.path.isfile(question_path)):  # default file not found
        print(colored("\n\tNo questions file found!\n", "red"))
        question_path = prompter("input", "Enter file name")
        if (not os.path.exists(question_path)) or (not os.path.isfile(question_path)):  # input file not found
            print(colored(
                f"\n\tNo file named {question_path} found (include file extension)!\n", "red"))
            sys.exit()

    quiz = get_save()  # get previous save

    if "--reset" in sys.argv or "-R" in sys.argv and quiz:
        quiz.reset()
    if not quiz:
        # Create quiz object from questions file
        quiz = Quiz(get_chapters(question_path))
    if "--update" in sys.argv or "-U" in sys.argv:
        quiz.chapters = get_chapters(question_path)
    if "--search" in sys.argv or "-S" in sys.argv:
        if len(sys.argv) != 3:
            print(colored("\n\n\tCan't search argument", "red"))
            sys.exit(1)
        else:
            search_questions(quiz.chapters, sys.argv[2])
            sys.exit(0)

    quiz.run()
