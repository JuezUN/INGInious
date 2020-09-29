# UNCode

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/73d2fa452a2a480aa36edeea79a725a9)](https://www.codacy.com/gh/JuezUN/INGInious/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=JuezUN/INGInious&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/JuezUN/INGInious.svg?branch=master)](https://travis-ci.org/JuezUN/INGInious)
[![CLA assistant](https://cla-assistant.io/readme/badge/JuezUN/INGInious)](https://cla-assistant.io/JuezUN/INGInious)
[![Gitter](https://badges.gitter.im/uncode-unal/community.svg)](https://gitter.im/uncode-unal/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

INGInious is an intelligent grader that allows secured and automated testing of code made by students.

It is written in Python and uses Docker_ to run student's code inside a secured environment.

INGInious provides a backend which manages interaction with Docker and grade code, and a frontend which allows students to submit their code in a simple and beautiful interface. The frontend also includes a simple administration interface that allows teachers to check the progression of their students and to modify exercices in a simple way.

The backend is independent of the frontend and was made to be used as a library.

INGInious can be used as an external grader for EDX. The course `Paradigms of Computer Programming - Fundamentals`_ uses INGInious to correct students' code.

[Docker](https://www.docker.com/)

## Documentation

The documentation is available on the repository wiki: [documentation](https://github.com/JuezUN/INGInious/wiki)

## Notes on security

Docker containers can be used securely with SELinux enabled. Please do not run untrusted code without activating SELinux.

## Mailing list

A mailing list for both usage and development discussion can be joined by registering here_.

## Publications
