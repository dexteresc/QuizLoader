# Quiz creator, loader and saver

A scripts that let's you play a quiz on a series of multi-answer questions divided up into chapters.  
These questions and chapters are fetched from a `.txt` file in a specified format.

## Quickstart

### Requires

- **Python 3.9** or above

---

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

- Chapters need to start with "Chapter" followed by a number.  
- Questions should start with a number.  
- Answers need to start with the option, which needs to be a lower-case alpha (a-z).  
  The correct answer is an UPPER-CASE alpha.

### Example

```plaintext
Chapter 1 
1. Which of the following protocols are examples of TCP/IP transport layer protocols? (Choose two answers.)
a. Ethernet
b. HTTP
c. IP
D. UDP
e. SMTP
F. TCP
```

The files default name is `questions.txt`.

## Command Line Arguments

Use `--help` to view availible command line arguments.

Use `--new` to overwrite current quiz with a new quiz (from text-file).

Use `--reset` to remove all save-files.
