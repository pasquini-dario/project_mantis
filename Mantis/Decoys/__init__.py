from ..utils.logger import logger

class DecoyService:
    def __init__(
        self,
        port,
        host="0.0.0.0",
        name='decoy',
        hparams={}
    ):
        self.port = port
        self.host = host
        self.name = name
        self.hparams = hparams

    def __call__(self, injection_manager):
        raise NotImplementedError
