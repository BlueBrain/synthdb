# Creating revisions

For each change in the model schema, a revision must be created that is able to move a given
database forward to the current schema.

We use Alembic for managing these revisions. See https://alembic.sqlalchemy.org.

In order to generate a new revision, autogenerate a candidate revision file based on a change in
the schema definition and a database that is in the latest revision state::

    $ alembic revision --autogenerate -m "Create new table" --rev-id=XXXX

With XXXX the revision ID. Note that we fix revision IDs to integers (padded with zeros). Before
creating, check the latest revision number, add one, pad with zeros, and include it in the command
using the ``--rev-id`` argument.

Then check the new script generated in ``synthdb/alembic/revisions`` and commit it if it suits you.

Also, note that with SQLite you should use "batch mode" for some operations, read more at
https://alembic.sqlalchemy.org/en/latest/batch.html
