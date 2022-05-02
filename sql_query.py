from prettytable import PrettyTable, from_db_cursor

def CreateQuery(connection, query, parameter=None, is_str=True):
    cursor = connection.cursor()
    mytable = PrettyTable()
    try:
        if parameter is None:
            cursor.execute(query)
            
        else:
            cursor.execute(query, parameter)              
            x = cursor.fetchall()
            if x == []:
                 return None
            if x[0][0] == 0 or x[0][0] == 1:
                return x[0][0]

        
        if not is_str and parameter is None:
            res = cursor.fetchall()
            res = [ i[0] for i in res ]
            return res
        elif not is_str:
            x = [ i[0] for i in x ]
            return x

        mytable = from_db_cursor(cursor)
        if mytable == None:
            return None
        mytable.align='l'
        return str(mytable)
    except Error as e :
        print(f"The error '{e}' occurred")