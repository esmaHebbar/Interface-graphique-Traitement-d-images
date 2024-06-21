import time
import zmq
from random import randint

# Configure ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind("tcp://127.0.0.1:5555")

iterations = 0
max_iterations = 100


while iterations < max_iterations:
    # Generate a random temperature value
    temperature = randint(20, 40)
    # Send the temperature value
    socket.send_json({"temperature": temperature})
    # Wait for a short period before generating the next value
    time.sleep(0.3)
    iterations += 1
