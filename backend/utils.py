

def read_version():
    try:    
        with open(file='./VERSION', mode='r') as file:
            VERSION = file.read().strip()
    except Exception as e:
        VERSION = "Unknown"
    
    return VERSION