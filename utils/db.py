import sqlalchemy as db


class DataBase():
    def __init__(self):
        self.engine = db.create_engine('sqlite:///series.db')
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()

    # Check if the table already exists
    def table_exists(self, table_name):
        return db.inspect(self.engine).has_table(table_name)

    # Only create the table if it doesn't already exist
    def create_table(self, name_table, *args):
        if not self.table_exists(name_table):
            table = db.Table(name_table, self.metadata,
                             db.Column('id_', db.Integer(), primary_key=True, autoincrement=True),
                             *[db.Column(arg, db.String()) for arg in args],
                             extend_existing=True)
            table.create(self.engine)
            print(f'Table {name_table} created')
        else:
            print(f"Table '{name_table}' already exists.")

    def read_table(self, name_table, return_keys=False):
        table = db.Table(name_table, self.metadata, autoload_with=self.engine)
        if return_keys:
            return table.columns.keys()
        return table

    def add_row(self, name_table, **kwargs):
        table = self.read_table(name_table)

        # Adjust the column title as per your schema for checking duplicates
        if 'title' in kwargs:
            select_stmt = db.select([table]).where(table.c.title == kwargs['title'])
            result = self.connection.execute(select_stmt)
            if result.fetchone():
                print(f"Row with title '{kwargs['title']}' already exists. No new row added.")
                return

        insert_stmt = db.insert(table).values(**kwargs)
        self.connection.execute(insert_stmt)
        print('New row added.')

    def delete_row_by_id(self, table_name, id_):
        table = self.read_table(table_name)

        stmt = db.delete(table).where(table.c.id_ == id_)
        self.connection.execute(stmt)
        print(f'Row id {id_} deleted')

    def select_table(self, name_table):
        table = self.read_table(name_table)
        stm = db.select([table])
        return self.connection.execute(stm).fetchall()
