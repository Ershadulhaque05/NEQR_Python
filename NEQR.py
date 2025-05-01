from qiskit import QuantumCircuit, Aer, execute
import numpy as np
from PIL import Image

# Step 1: Create a small 4x4 grayscale image
small_img = np.array([
    [0, 85, 170, 255],
    [85, 170, 255, 0],
    [170, 255, 0, 85],
    [255, 0, 85, 170]
], dtype=np.uint8)

# Step 2: Parameters
size = 4  # 4x4 image
n = int(np.log2(size))  # number of qubits for x and y (2 each for 4x4)
color_bits = 8  # grayscale from 0 to 255

total_qubits = 2 * n + color_bits  # total qubits = address + color

# Step 3: Initialize quantum circuit
qc = QuantumCircuit(total_qubits)

# Step 4: Superposition on address qubits (first 2n qubits)
for i in range(2 * n):
    qc.h(i)

# Step 5: Encode grayscale values
for x in range(size):
    for y in range(size):
        pixel_value = small_img[x, y]
        binary_value = format(pixel_value, '08b')  # 8-bit grayscale value

        x_bin = format(x, f'0{n}b')
        y_bin = format(y, f'0{n}b')

        # Temporary circuit for each pixel encoding
        qc_temp = QuantumCircuit(total_qubits)

        # Apply X to match the address bits with control
        for idx, bit in enumerate(x_bin + y_bin):
            if bit == '0':
                qc_temp.x(idx)

        # Apply multi-controlled X (Toffoli) to encode 1s in grayscale bits
        for j, bit in enumerate(binary_value):
            if bit == '1':
                controls = list(range(2 * n))
                target = 2 * n + j
                qc_temp.mcx(controls, target)

        # Uncompute the X gates
        for idx, bit in enumerate(x_bin + y_bin):
            if bit == '0':
                qc_temp.x(idx)

        # Compose with main circuit
        qc = qc.compose(qc_temp)

# Step 6: Show the circuit
print(qc.draw(output='text'))

# Step 7: Simulate the quantum state
simulator = Aer.get_backend('statevector_simulator')
result = execute(qc, backend=simulator).result()
statevector = result.get_statevector()

# Display size of statevector (should be 2^qubits long)
print(f"Statevector has {len(statevector)} amplitudes.")
