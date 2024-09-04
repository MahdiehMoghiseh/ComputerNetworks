import threading 

from server import udp_handler, tcp_handler 

udp_thread = threading.Thread(target=udp_handler)
tcp_thread = threading.Thread(target=tcp_handler)

# Start both threads
udp_thread.start()
tcp_thread.start()

# Wait for both threads to finish
udp_thread.join()
tcp_thread.join()