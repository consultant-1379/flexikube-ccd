import os
import base64
from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_text
try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

description = '''
This module generates a key of random bytes
and returns it as a base64 encoded string.
'''



class LookupModule(LookupBase):
    '''
      lookup of 32 will return something like 'eJU1OkbI+hgnTJ8r7+fKPx4isuervg8Qn1lR3q/8vJc='
    '''
    def run(self, byteslen, variables=None, **kwargs):
        length=byteslen[0]
        display.vvvv("Generating key of length: %s" % byteslen )
        return [to_text(base64.b64encode(bytes(os.urandom(length))))]



if __name__ == "__main__":
    lm = LookupModule()
    rv = lm.run([32])
    print(rv)
