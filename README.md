# RAISE Moodle Backup Tools

This repo contains some simple scripts / library functions to manipulate Moodle backup files.

When developing, you may want to install the project in editable mode:

```bash
$ pip install -e .
```

The code can be linted and tested locally as well:

```bash
$ pip install .[test]
$ flake8
$ pytest
```

Code coverage reports can be generated when running tests:

```bash
$ pytest --cov=mbtools --cov-report=term --cov-report=html
```
