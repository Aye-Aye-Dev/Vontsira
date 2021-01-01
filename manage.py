'''
Created on 26 Dec 2020

@author: si
'''
import os
import sys

from vontsira.app import create_app
from vontsira.database import create_database, migrate_database


def create_user(deployment):
    raise NotImplementedError("TODO")


def run_locally(deployment):
    """
    Run the local flask server for `app`. Just for local development, not production use.

    Parameters
    ----------
    deployment : str
        If the 'vontsira.settings.local_config.Config' is to be used
        deployment=local_config
    """
    app = create_app(f'vontsira.settings.{deployment}_config.Config')
    app.run(debug=app.config['DEBUG'],
            use_reloader=app.config['DEBUG'],
            port=app.config['HTTP_PORT'],
            host='0.0.0.0'
            )


def create_update_db(deployment):
    """
    Build table schema within database and run database migrations.

    Parameters
    ----------
    deployment : str
        If the 'vontsira.settings.local_config.Config' is to be used
        deployment=local_config

    Returns
    -------
    app (instance of :class:`Flask.app`)
    """
    app = create_app(f'vontsira.settings.{deployment}_config.Config')
    print(f"Creating/checking db: {app.config['SQLALCHEMY_DATABASE_URI']}...")
    create_database(app)

    print("Updating migration state...")
    migrate_database(app)

    return app


if __name__ == '__main__':

    if len(sys.argv) != 3:
        msg = ("usage: python manage.py <settings label> <task>\n"
               "  where <task> is: create_user | run | update_database\n"
               )
        sys.stderr.write(msg)
        sys.exit(-1)

    deployment_environment = sys.argv[1]
    task = sys.argv[2]

    # alembic's env.py uses this
    os.environ['deployment_environment'] = deployment_environment

    if task == 'create_user':
        if not create_user(deployment_environment):
            print("Problem adding user")
            sys.exit(1)

    elif task == 'update_database':
        if not create_update_db(deployment_environment):
            print("Problem updating db schema")
            sys.exit(1)

    elif task == 'run':
        run_locally(deployment_environment)
        print("Finished running")

    else:
        msg = "Unknown task"
        print(msg)
        sys.exit(1)

    print("All done!")
