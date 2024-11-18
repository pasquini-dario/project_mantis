from .web_hackback_rshell import *


#### Confs ############################################################
DECOYS = {
    80 : (
        WebFakeDB_sqlinj,
        {
            'hparams' : {
                'BANNER_INJECTION_POOL' : [
                    "(Vulnerable to SQL injection)",
                    "(SQL Injection detected)",
                    "<--- /login vulnerable to SQL injection",
                ]
            },
        }
    ),
}
