# pip install py4j
from py4j.java_gateway import (JavaGateway, GatewayParameters)

addr = '127.0.0.1'
port = 25333

# if you need to launch a gateway manually, you can use py4j.launch_gateway() function

# Connect to the gateway
params = GatewayParameters(addr,port, auto_convert=True)
gateway = JavaGateway(gateway_parameters=params)

# Instanciates a WarpScript stack
stack = gateway.entry_point.newStack()

# Push objects onto the stack
stack.push(0)
stack.push([1,2,3,4])

# Execute WarpScript
stack.execMulti('<% + %> FOREACH')

# Extract top of the stack and print it
print(stack.pop())

# Print fields and methods
print(dir(stack))
#stack = stack.execMulti('<My_WarpScript_code_here>')

# Extract top of the stack and store it in a Python variable
# @see https://www.py4j.org/advanced_topics.html#collections-conversion
#my_var = stack.pop()
