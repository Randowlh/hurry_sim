import matplotlib.pyplot as plt

with open('throughput_50000_1s.txt', 'r') as f:
    throughput_table = [float(line.strip()) for line in f]
    
with open('throughput_with_isl_50000_1s.txt', 'r') as f:
    throughput_table_with_isl = [float(line.strip()) for line in f]

# plt.plot(throughput_table_with_isl)


plt.plot(throughput_table, label='Without ISL')
plt.plot(throughput_table_with_isl, label='With ISL')
plt.ylabel('Throughput')
plt.xlabel('Time')
# plt.legend()
plt.show()
plt.show()