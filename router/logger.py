from router.settings import Settings

class Logger():
    
    def __init__(self, settings: Settings):
        self.settings = settings

    async def print(self, *args):
        message = '\n'.join(args)
        print(message)

