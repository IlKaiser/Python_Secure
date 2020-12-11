import threading
import time

from Alice import Alice
from Bob import Bob
from Cert import Cert

a = Alice()
b = Bob()
c = Cert()

time.sleep(0.1)

c.start()
time.sleep(0.1)
a.start()
time.sleep(0.1)
b.start()
time.sleep(0.1)



### Initial seutp
"""
    A --Connect_to--> C
    C <--Connected--> B
"""
### Protocol
"""
0. B --Pk_bc--> C
   A --Pk_ac--> C

1. A --------Nonce,Timestamp--------> C
   C --Pk_ac(Nonce,Timestamp),Pk_c--> A

2. A --Pk_ac(Ab_key,Timestamp,Port)-------------> C
   C --Pk_bc(Ab_key,Timestamp,Alice_Port)--> B

3. B --K_ab(Timestamp)--> A 

"""

b.connect_to_cert()
time.sleep(0.5)
a.connect_to_cert()

###### Done


