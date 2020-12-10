from Alice import Alice
from Bob import Bob
from Cert import Cert
import threading
import time

a = Alice()
b = Bob()
c = Cert()

time.sleep(0.1)

c.start()
a.start()
time.sleep(0.1)
b.start()
time.sleep(0.1)



### Initial seutp
"""
    A ----> C
    C <---> B
"""
b.connect_to_cert()
time.sleep(0.5)
a.connect_to_cert()



