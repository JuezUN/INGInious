# UNCode

[![License](https://img.shields.io/github/license/JuezUN/INGInious?style=plastic)][license_url]
[![Contributors](https://img.shields.io/github/contributors/JuezUN/INGInious?style=plastic)][contributors_url]
[![GitHub issues](https://img.shields.io/github/issues/JuezUN/INGInious?style=plastic)][issues_url]
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/73d2fa452a2a480aa36edeea79a725a9)][codacy_badge_url]
[![Build Status](https://travis-ci.com/JuezUN/INGInious.svg?branch=master)][travis_status_url]
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

In case you want to host your course on our deployment, email us on: <uncode_fibog@unal.edu.co>

UNCode: <https://uncode.unal.edu.co>

Project page: <https://juezun.github.io/>

## Publications

- F. Restrepo-Calle, J.J. Ramírez-Echeverry, F.A. Gonzalez. "[UNCode: Interactive system for learning and automatic 
evaluation of computer programming skills.][uncode_publication_2018_url]". In Proceedings of the 10th annual International 
Conference on Education  and New Learning Technologies EDULEARN 2018. Palma de Mallorca, Spain, 2nd-4th July 2018, 
pp. 6888-6898. doi: 10.21125/edulearn.2018.1632.

```
    @InProceedings{Restrepo-Calle2018,
        author = {Restrepo-Calle, F. and Ram{\'{i}}rez-Echeverry, J.J. and Gonzalez, F.A.},
        title = {{UNCode: Interactive System for Learning and Automatic Evaluation of Computer Programming Skills}},
        series = {10th International Conference on Education and New Learning Technologies},
        booktitle = {EDULEARN18 Proceedings},
        isbn = {978-84-09-02709-5},
        issn = {2340-1117},
        doi = {10.21125/edulearn.2018.1632},
        url = {http://dx.doi.org/10.21125/edulearn.2018.1632},
        publisher = {IATED},
        location = {Palma, Spain},
        month = {2-4 July, 2018},
        year = {2018},
        pages = {6888-6898}
    }
```

- F. Restrepo-Calle, J.J. Ramírez-Echeverry, F.A. González, "[Using an Interactive Software Tool for the Formative and Summative Evaluation in a Computer Programming Course: an Experience Report][uncode_publication_2020_url]," Glob. J. Eng. Educ., vol. 22, no. 3, pp. 174–185, 2020.

```
    @article{Restrepo-Calle2020,
        author = {Restrepo-Calle, Felipe and Ram{\'{i}}rez-Echeverry, Jhon Jairo and Gonz{\'{a}}lez, Fabio A},
        journal = {Global Journal of Engineering Education},
        keywords = {automatic assessment,computer programming,computer science education,formative evaluation,summative evaluation},
        number = {3},
        pages = {174--185},
        title = {{Using an Interactive Software Tool for the Formative and Summative Evaluation in a Computer Programming Course: an Experience Report}},
        volume = {22},
        year = {2020}
    }
```

- Cristian D. González-Carrillo, F. Restrepo-Calle, J.J. Ramírez-Echeverry, F.A. Gonzalez. "[Automatic Grading Tool for Jupyter Notebooks in Artificial Intelligence Courses][uncode_publication_gonzalez_2021_url]". Sustainability 2021, 13, 12050. doi.org/10.3390/su132112050

```
    @Article{Gonzalez2021AutomaticCourses,
        AUTHOR = {González-Carrillo, Cristian D. and Restrepo-Calle, Felipe and Ramírez-Echeverry, Jhon J. and González, Fabio A.},
        TITLE = {Automatic Grading Tool for Jupyter Notebooks in Artificial Intelligence Courses},
        JOURNAL = {Sustainability},
        VOLUME = {13},
        YEAR = {2021},
        NUMBER = {21},
        ARTICLE-NUMBER = {12050},
        URL = {https://www.mdpi.com/2071-1050/13/21/12050},
        ISSN = {2071-1050},
        DOI = {10.3390/su132112050}
    }
```

- Edna Chaparro, Felipe Restrepo-Calle and Jhon Jairo Ramírez-Echeverry. "[Learning analytics in computer programming courses][uncode_publication_lala_2021_url]". In Proceedings of the LALA'21: IV Latin American Conference on Learning Analytics, October 19–21, 2021, Arequipa, Perú. URL: https://ceur-ws.org/Vol-3059/paper8.pdf

```
    @InProceedings{Chaparro2021,
        author = {Chaparro, Edna and Restrepo-Calle, Felipe and Ram{\'{i}}rez-Echeverry, Jhon Jairo},
        title = {{Learning analytics in computer programming courses}},
        series = {CEUR Workshop Proceedings},
        booktitle = {Proceedings of the LALA'21: IV Latin American Conference on Learning Analytics},
        issn = {1613-0073},
        url = {https://ceur-ws.org/Vol-3059/paper8.pdf},
        publisher = {CEUR-WS},
        location = {Arequipa, Perú},
        month = {October 19–21},
        year = {2021},
        pages = {78-87}
    }
```

- J.J. Ramírez-Echeverry, F. Restrepo-Calle, F.A. González, “[A case study in technology-enhanced learning in an introductory computer programming course][uncode_publication_gjee_2022_url],” Glob. J. Eng. Educ., vol. 24, no. 1, pp. 65–71, 2022.

```
    @article{Ramirez-Echaverry2022,
        author = {Ram{\'{i}}rez-Echeverry, Jhon Jairo and Restrepo-Calle, Felipe and Gonz{\'{a}}lez, Fabio A},
        journal = {Global Journal of Engineering Education},
        keywords = {Computer programming, technology-enhanced learning, computer science education},
        number = {1},
        pages = {65--71},
        title = {{A case study in technology-enhanced learning in an introductory computer programming course}},
        volume = {24},
        url = {http://www.wiete.com.au/journals/GJEE/Publish/vol24no1/10-Restrepo-Calle-F.pdf},
        year = {2022}
    }
```

- Edna Johanna Chaparro Amaya, Felipe Restrepo-Calle, Jhon J Ramírez-Echeverry, “[Discovering Insights in Learning Analytics Through a Mixed-Methods Framework: Application to Computer Programming Education][uncode_publication_jite_2023_url],” Journal of Information Technology Education: Research, Vol. 22, pp. 339-372, 2023.

```
    @article{Chaparro2023,
        author = {Chaparro Amaya, Edna Johanna and Restrepo-Calle, Felipe and Ram{\'{i}}rez-Echeverry, Jhon Jairo},
        journal = {Journal of Information Technology Education: Research},
        keywords = {learning analytics, mixed methods, computer programming, correlation analysis, content analysis},
        pages = {339--372},
        title = {{Discovering Insights in Learning Analytics Through a Mixed-Methods Framework: Application to Computer Programming Education}},
        volume = {22},
        doi = {https://doi.org/10.28945/5182},
        month={Aug.},
        year = {2023}
    }
```

- Corso Pinzón, A.F., Ramírez-Echeverry, J.J. and Restrepo-Calle, F. 2024. [Automated grading software tool with feedback process to support learning of hardware description languages][uncode_publication_rptel_2024_url]. Research and Practice in Technology Enhanced Learning. 19, (Jan. 2024), 015. DOI:https://doi.org/10.58459/rptel.2024.19015.

```
    @article{Corso2024,
        author = {Corso Pinzón, Andrés Francisco and Ramírez-Echeverry, Jhon J. and Restrepo-Calle, Felipe},
        journal = {Research and Practice in Technology Enhanced Learning},
        pages = {015},
        title = {{Automated grading software tool with feedback process to support learning of hardware description languages}},
        volume = {19},
        url={https://rptel.apsce.net/index.php/RPTEL/article/view/2024-19015},
        doi = {https://doi.org/10.58459/rptel.2024.19015},
        month={Jan.},
        year = {2024}
    }
```


[uncode_url]: https://uncode.unal.edu.co/courselist
[license_url]: https://github.com/JuezUN/INGInious/blob/master/LICENSE
[contributors_url]: https://github.com/JuezUN/INGInious/graphs/contributors
[issues_url]: https://github.com/JuezUN/INGInious/issues
[codacy_badge_url]: https://www.codacy.com/gh/JuezUN/INGInious/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=JuezUN/INGInious&amp;utm_campaign=Badge_Grade
[travis_status_url]: https://travis-ci.com/github/JuezUN/INGInious
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
[uncode_publication_2018_url]: https://library.iated.org/view/RESTREPOCALLE2018UNC
[uncode_publication_2020_url]: http://www.wiete.com.au/journals/GJEE/Publish/vol22no3/06-Echeverry-J.pdf
[uncode_publication_gonzalez_2021_url]: https://www.mdpi.com/2071-1050/13/21/12050
[uncode_publication_lala_2021_url]: https://ceur-ws.org/Vol-3059/paper8.pdf
[uncode_publication_gjee_2022_url]: http://www.wiete.com.au/journals/GJEE/Publish/vol24no1/10-Restrepo-Calle-F.pdf
[uncode_publication_jite_2023_url]: https://doi.org/10.28945/5182
[uncode_publication_rptel_2024_url]: https://doi.org/10.58459/rptel.2024.19015

