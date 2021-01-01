# Vontsira
A data registry


## Running it locally

```shell
export PYTHONPATH=`pwd`
cd vontsira/settings
cp local_config_example.py local_config.py
cd ../..
python manage.py local update_database
```

## Architecture Overview

Both a relational database (accessed via the [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) ORM and a document store are used.

The document store at present expects JSON encoded documents. It stores a little bit of meta data alongside the original documents.

The database is a subset of fields held in the document store.

The database isn't the main data repository, it is a subset of data held in the document store. Using a database reduces the number of expensive (in terms of time) operations that would be required of a document store and provides a general purpose way to query. It also makes unique indices easier. For a document store to replace the dual database + document store approach would require a more complex setup (e.g. Elastic search or similar) and would require a more structured document schema which would restrict to a single document encoding.

TODO -- API + UI -  content negotiation