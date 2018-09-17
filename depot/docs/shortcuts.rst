Shortcut
========

Make Command Shortcuts:
-----------------------
.. _make-commands:

::

    bootstrap              - Setup the local environment.
    runserver              - Python django runserver @ port 8009.
    docs                   - Build Documentation.
    coverage               - Show coverage of tests.
    readme                 - Regenerate README.rst file.
    test                   - Run unittests using current python.
       pytestcheck         - Run pytest using current python.
       lint ------------   - Check codebase for problems.
         readmecheck       - Check README.rst encoding.
         flakes --------   - Check code for syntax and style errors.
            flakecheck     - Run flake8 on the source code.
            pylintcheck    - Run pylint on the source code.
            pep257check    - Run pep257 on the source code.
    clean --------------   - Non-destructive clean
        clean-pyc          - Remove .pyc/__pycache__ files.
        clean-docs         - Remove documentation build artifacts.
        clean-build        - Remove setup artifacts.
        clean-test         - Remove test and coverage artifacts.
    bump                   - Bump patch version number.
    bump-minor             - Bump minor version number.
    bump-major             - Bump major version number.
    catversion             - Print the current version number.
    latest-tag             - Print the latest tag.
    docker -------------   - Build and run the docker image
        docker-build       - Build docker image.
        docker-run         - run the built docker image.
    dc-dev-build           - Docker new image build and run with docker-compose.
    dc-dev-up              - Docker image build and run with docker-compose.
    add-git-hooks          - Add git hooks to your .git configs.
