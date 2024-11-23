import platform
import pgsql

class Utils:

    @staticmethod
    def get_database_pass():
        system = platform.system()
        if 'Darwin' == system:
            return '12345'
        else:
            return '12345'

    @staticmethod
    def execute_sql(sql, *params):
        datas = []
        with pgsql.Connection(("localhost", 5432), "postgres", Utils.get_database_pass(), "postgres", tls = False) as db:
            with db.prepare(sql) as statement:
                if None != params:
                    datas = list(statement(*params))
                else:
                    datas = list(statement())
        
        return datas
    
    @staticmethod
    def execute_sql_arow(sql, *params):
        row = ()
        with pgsql.Connection(("localhost", 5432), "postgres", Utils.get_database_pass(), "postgres", tls = False) as db:
            with db.prepare(sql) as statement:
                if None != params:
                    row = statement(*params).row()
                else:
                    row = statement().row()
        
        return row