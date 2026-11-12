import requests
from config import Config

class WhatsApp:
    URL = f"https://7107.api.greenapi.com/waInstance{Config.INSTANCIA_GREENAPI}"
    
    @classmethod
    def verificar_conexao(cls):
        url = f"{WhatsApp.URL}/getStateInstance/{Config.TOKEN_GREENAPI}"

        r = requests.get(url, timeout=30)
        
        r.raise_for_status()
        
        return r.json().get("stateInstance")
    
    @classmethod
    def qrcode(cls):
        url = f"{WhatsApp.URL}/qr/{Config.TOKEN_GREENAPI}"
        
        
        r = requests.get(url, timeout=30)
         
        r.raise_for_status()
        
        return r.json()
    
    @classmethod
    def reconectar(cls):
        url = f"{WhatsApp.URL}/reboot/{Config.TOKEN_GREENAPI}"
        
        r = requests.get(url, timeout=30)
        
        r.raise_for_status
        
        return r.json()
    
    @classmethod
    def desconectar(cls):
        url = f"{WhatsApp.URL}/logout/{Config.TOKEN_GREENAPI}"
        
        r = requests.get(url, timeout=30)
        
        r.raise_for_status
        
        return r.json()