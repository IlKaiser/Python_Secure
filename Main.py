from Alice import Alice
from Bob import Bob
import threading

a = Alice()
b = Bob()


b.start()
a.start()

a.connect_to_bob()
a.connect_to_cert()

