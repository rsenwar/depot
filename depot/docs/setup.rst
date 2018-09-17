Depot Setup
=============

Docker Setup:
-------------
.. _docker-setup:

``Follow the steps:``

    1. Install the docker (if not installed). Go to the `docker <https://docs.docker.com/install/>`_
       and download docker as per your system configuration.

    2. Go to your workspace and clone the repo.

     ::

         $ git clone https://github.com/goibibo/depot.git depot

    3. Create a database named ``depot`` in ``mysql``. [if it is not present in your database]

     ::

        $ mysql -uroot -p

        mysql> CREATE DATABASE depot;

    4. Copy dev settings and change settings for ``DATABASE`` and ``CACHES``.

     .. code:: shell

        $ cp depot/depot_proj/settings/dev.py.dist  depot/depot_proj/settings/dev.py

    5. Run following commands to run the docker container as it is running on production.

     .. code:: shell

        $ make docker-build
        $ make docker-run

    6. Run following commands to run the docker with local changes enabled.

     .. code:: shell

        $ make dc-dev-build
        $ make dc-dev-up

    7. Add git-hooks with command ``make add-git-hooks``.


Local Setup:
------------
.. _local-setup:

``Steps to follow:``

    1. Go to your workspace and clone the repo:

     ::

         $ git clone https://github.com/goibibo/depot.git

    2. Install ``python3`` (if it is not already present in your system)
       and check the version of python3:

     ::

        $ python3 -V

    3. Go to ``depot`` directory

     ::

        $ cd depot

    4. Create virtual environment

     .. code:: shell

        $ python3 -m venv venv_depot
        $ #(or using virtualenv)
        $ virtualenv -p python3 venv_depot
        $ source venv_depot/bin/activate

    5. Install python packages

     .. code:: shell

        $ pip install -r config/pip/requirements.txt
        (for additional modules)
        $ pip install -r config/pip/requirements_dev.txt

    6. Create a database named ``depot`` in ``mysql``. [if it is not present in your database.]

     ::

        $ mysql -u root -p

        mysql> CREATE DATABASE depot;

    7. Copy local settings and change settings for ``DATABASE`` and ``CACHES``.

     .. code:: shell

        $ cp depot_proj/settings/local.py.dist  depot/depot_proj/settings/local.py

    8. Run migrations to create ``django-framework`` tables or dump the database.

     ::

        $ python manage_local.py migrate

    9. Createsuperuser for your account.

     ::

        $ python manage_local.py createsuperuser

    10. Run the local server.

     ::

        $ python manage_local.py runserver 8009


    11. Add git-hooks with command ``make add-git-hooks``.
