# Quiz creator, loader and saver

A scripts that let's you play a quiz on a series of multi-answer questions divided up into chapters.  
These questions and chapters are fetched from a `.txt` file in a specified format.

## Quickstart
### Requires
- Python 3.9>

```shell
# Install necessary modules
pip3 install InquirerPy termcolor

# Run
python3 main.py
```

## Features

- Score tracking
- Progress saving
- Chapter select

## Supports

- Multi-answer questions
- Multi-answer questions with multiple correct answers

## Screenshots

![image](https://user-images.githubusercontent.com/63741680/159105089-796b8f4e-8ec8-4e83-9a2f-bc3023cb7069.png)

## Text-file format

Use this format in the text file:
```
Chapter *number*
  *number*. Question promt
  *alpha*. Answer
  *alpha*. Answer
```
The files default name is `questions.txt`.

## Command Line Arguments

Use `--update` to update the questions.

Use `--reset` to remove all save-files.

Use `--search` to search through all saved questions.
