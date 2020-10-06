# UNCode

[![License](https://img.shields.io/github/license/JuezUN/INGInious?style=plastic)][license_url]
[![Contributors](https://img.shields.io/github/contributors/JuezUN/INGInious?style=plastic)][contributors_url]
[![GitHub issues](https://img.shields.io/github/issues/JuezUN/INGInious?style=plastic)][issues_url]
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/73d2fa452a2a480aa36edeea79a725a9)][codacy_badge_url]
[![Build Status](https://travis-ci.org/JuezUN/INGInious.svg?branch=master)][travis_status_url]
[![CLA assistant](https://cla-assistant.io/readme/badge/JuezUN/INGInious)][cla_url]
[![Gitter](https://badges.gitter.im/uncode-unal/community.svg)][gitter_url]

This is the main repository of UNCode.

UNCode is an online platform built on top of [INGInious][inginious_url] (**v0.5**) for frequent practice 
and automatic evaluation of computer programming, Jupyter Notebooks and hardware description language (VHDL/Verilog) 
assignments. Also provides a pluggable interface with your existing LMS. 

UNCode is currently used at the Universidad Nacional De Colombia, Campus Bogotá. UNCode supports automatic evaluation 
in languages like: C/C++, Java 7/8, Python 3, Verilog, VHDL and Jupyter Notebooks. Additionally, has been employed in 
courses like: Basic Computer Programming, Data Structures, Machine Learning, Artificial Intelligence, Quantum 
Programming, Programming Languages, among others. See the complete [list of courses][uncode_url].

UNCode provides a backend which manages interaction with Docker and grading code, and a frontend which 
allows students to submit their code in a simple and beautiful interface. The frontend also includes a 
simple administration interface that allows teachers to check the progression of their students and to 
modify exercises in a simple way.

The backend is independent of the frontend and was made to be used as a library.

UNCode can be used as an external grader for Learning Managment Systems (LMS) such as Moodle or OpenEDX.

## Built with

- [Python (with pip) 3.5+][python_url]
- [Docker 1.12+][docker_url]
- [MongoDB][mongo_url]
- Libtidy
- [LibZMQ][libzmq_url]

## Getting started

### Install locally

Depending on the operating system you use, follow the given instructions here: [Installation][install_locally_url]

### Deploy it for your courses

To deploy UNCode in a server and start using it in your courses, please refer to the 
[Deployment repository][deployment_url]. Here you will be able to deploy it following some few steps.

## Documentation

For additional documentation, please refer to the [Wiki][uncode_wiki_url].

## Notes on security

Docker containers can be used securely with SELinux enabled. Please do not run untrusted code without activating SELinux.

## Roadmap

See the [UNCode GitHub Project][project_url] for a list of proposed features, known issues and how they are being 
tackled.

## Contributing

Go to [CONTRIBUTING][contributing_url] to see the guidelines and how to start contributing to UNCode.

## License

Distributed under the AGPL-3.0 License. See [LICENSE][license_url] for more information.

## Contact

In case of technical questions, please use the [gitter communication channel][gitter_url].

In case you want to host your course on our deployment, email us on: **uncode_fibog@unal.edu.co**

UNCode: <https://uncode.unal.edu.co>

Project page: <https://juezun.github.io/UNCode_page/>

## Publications

- F. Restrepo-Calle, J.J. Ramírez-Echeverry, F.A. Gonzalez. "[UNCode: Interactive system for learning and automatic 
evaluation of computer programming skills.][uncode_publication_url]". In Proceedings of the 10th annual International 
Conference on Education  and New Learning Technologies EDULEARN 2018. Palma de Mallorca, Spain, 2nd-4th July 2018, 
pp. 6888-6898. doi: 10.21125/edulearn.2018.1632.

```
    @article{Restrepo-Calle2018,
        title = {{Uncode: Interactive System for Learning and Automatic Evaluation of Computer Programming Skills}},
        year = {2018},
        journal = {EDULEARN18 Proceedings},
        author = {Restrepo-Calle, Felipe and Ram{\'{i}}rez-Echeverry, Jhon Jairo and Gonzalez, Fabio A.},
        number = {July},
        pages = {6888--6898},
        volume = {1},
        isbn = {9788409027095},
        doi = {10.21125/edulearn.2018.1632},
        keywords = {automatic grading tool, computer programming, educational environment}
    }
```

[uncode_url]: https://uncode.unal.edu.co/courselist
[license_url]: https://github.com/JuezUN/INGInious/blob/master/LICENSE
[contributors_url]: https://github.com/JuezUN/INGInious/graphs/contributors
[issues_url]: https://github.com/JuezUN/INGInious/issues
[codacy_badge_url]: https://www.codacy.com/gh/JuezUN/INGInious/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=JuezUN/INGInious&amp;utm_campaign=Badge_Grade
[travis_status_url]: https://travis-ci.org/JuezUN/INGInious
[cla_url]: https://cla-assistant.io/JuezUN/INGInious
[gitter_url]:https://gitter.im/uncode-unal/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
[inginious_url]: https://github.com/UCL-INGI/INGInious
[docker_url]: https://www.docker.com/
[python_url]: https://www.python.org/
[mongo_url]: https://www.mongodb.com/
[uncode_wiki_url]: https://github.com/JuezUN/INGInious/wiki
[libzmq_url]: https://zeromq.org/
[deployment_url]: https://github.com/JuezUN/Deployment
[install_locally_url]: https://inginious.readthedocs.io/en/v0.5/install_doc/installation.html
[project_url]: https://github.com/orgs/JuezUN/projects/3
[contributing_url]: https://github.com/JuezUN/INGInious/blob/master/CONTRIBUTING.md
[uncode_publication_url]: https://library.iated.org/view/RESTREPOCALLE2018UNC