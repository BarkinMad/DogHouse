import flet as ft

class PageManager:
   _instance = None
   _page = None
   
   def __new__(cls, page=None):
       if cls._instance is None:
           cls._instance = super().__new__(cls)
       if page is not None:
           cls._page = page
       return cls._instance

   @classmethod 
   def get_page(cls):
       return cls._page