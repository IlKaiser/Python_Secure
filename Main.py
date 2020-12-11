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
"""
1. B --Pk_bc--> C
   A --Pk_ac--> C

2. A --------Nonce,Timestamp--------> C
   C --Pk_ac(Nonce,Timestamp),Pk_c--> A

3. A --Pk_ac(Ab_key,Timestamp)-------------> C
   C --Pk_bc(Ab_key,Timestamp,Alice_Port)--> B

4. B --K_ab(Timestamp)--> A 

"""

b.connect_to_cert()
time.sleep(0.5)
a.connect_to_cert()

###### Done


