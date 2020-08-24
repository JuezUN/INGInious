# UNCode

[![CLA assistant](https://cla-assistant.io/readme/badge/JuezUN/INGInious)](https://cla-assistant.io/JuezUN/INGInious)
[![Gitter](https://badges.gitter.im/uncode-unal/community.svg)](https://gitter.im/uncode-unal/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)


INGInious is an intelligent grader that allows secured and automated testing of code made by students.

It is written in Python and uses Docker_ to run student's code inside a secured environment.

INGInious provides a backend which manages interaction with Docker and grade code, and a frontend which allows students to submit their code in a simple and beautiful interface. The frontend also includes a simple administration interface that allows teachers to check the progression of their students and to modify exercices in a simple way.

The backend is independent of the frontend and was made to be used as a library.

INGInious can be used as an external grader for EDX. The course `Paradigms of Computer Programming - Fundamentals`_ uses INGInious to correct students' code.

[Docker](https://www.docker.com/)

## Documentation

The documentation is available on Read the Docs:

- For the stable branch : http://inginious.readthedocs.org/
- For the master (dev) branch (not always up to date) : http://inginious.readthedocs.org/en/latest/index.html

On Linux, run ``make html`` in the directory ``/doc`` to create a html version of the documentation.


## Notes on security

Docker containers can be used securely with SELinux enabled. Please do not run untrusted code without activating SELinux.

## Mailing list

A mailing list for both usage and development discussion can be joined by registering here_.

## Publications
