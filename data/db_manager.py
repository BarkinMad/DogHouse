from tinydb import TinyDB, Query
from console import DHConsole

class DBManager:
    _instance = None
    def __init__(self, db_path = "./data/db.json"):
        if not DBManager._instance:
            self.db = TinyDB(db_path)
            self.console = DHConsole()
            DBManager._instance = self
        else:
            self.db = DBManager._instance.db
            self.console = DBManager._instance.console

    def add_service(self, ip:str, port:int, verbose: bool = False) -> None:
        '''Adds service to database'''
        self.db.insert({"ip": ip, "port": port})
        if verbose:
            self._instance.console.print(f"Added service to db: d[<f=ffffff, b>, <{ip}:{port}>]")

    def remove_service(self, ip:str, port:int, verbose: bool = False) -> None:
        '''Removes service from database'''
        query = (Query().ip == ip) & (Query().port == port)
        self.db.remove(query)
        if verbose:
            self._instance.console.print(f"Removed service from db: d[<f=ffffff, b>, <{ip}:{port}>]")

    def check_service(self, ip:str, port:int, verbose: bool = False) -> bool:
        '''Checks if service already exists in database'''
        query = (Query().ip == ip) & (Query().port == port)
        result = self.db.search(query)
        if verbose:
            self._instance.console.print(f"Checking service in db: d[<f=ffffff, b>, <{ip}:{port}>]")
        return len(result) > 0
    
    def get_services(self) -> list:
        '''Returns all services in database'''
        return self.db.all()
    
    def add_if_original(self, ip:str, port:int) -> bool:
        '''Adds service to database if it does not already exist. Returns True if added, False if already exists'''
        result = self.check_service(ip, port)
        if not result:
            self.add_service(ip, port)
            return True
        return False
    
    def clear_db(self) -> None:
        '''Clears database'''
        self.db.truncate()