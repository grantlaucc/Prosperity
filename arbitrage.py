from math import inf, log

matrix = (
    (1, 0.5, 1.45, 0.75),
    (1.95, 1, 3.1, 1.49),
    (0.67, 0.31, 1, 0.48),
    (1.34, 0.64, 1.98, 1),
)
labels = 'Pizza Slice', 'Wasabi Root', 'Snowball', 'Shells'
source = labels.index('Shells')
count = len(matrix)
edges \
    = [(i, j, -log(matrix[i][j])) for i in range(count) for j in range(count)]
distances = [inf for _ in range(count)]
predecessors = [None for _ in range(count)]
distances[source] = 0

for i in range(count):
  for u, v, w in edges:
    if distances[u] + w < distances[v]:
      distances[v] = distances[u] + w
      predecessors[v] = u

for node in range(count):
    label = labels[node]

    if distances[node] < 0:
        print(f'Arbitrage opportunity found for {label}...')

        nodes = set()
        order = []

        while node not in nodes:
            nodes.add(node)
            order.append(node)
            node = predecessors[node]

        order.reverse()
        multiplier = 1

        for i in range(len(order)):
            multiplier *= matrix[order[i]][order[(i + 1) % len(order)]]

        print(f'Cycle: ({node}) -> {order} yields x{multiplier}')
    else:
        print(f'No arbitrage opportunity found for {label}...')


path = ['Shells', 'Pizza Slice', 'Wasabi Root', 'Snowball', 'Pizza Slice', 'Shells']
multiplier = 1
capital = 2000000

for i in range(len(path)):
    print(path[i], multiplier, multiplier * capital)

    if i + 1 < len(path):
        multiplier *= matrix[labels.index(path[i])][labels.index(path[i + 1])]
