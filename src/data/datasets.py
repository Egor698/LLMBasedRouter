import json
import csv

data = {}

with open('src/data/benchmark.csv', 'w', encoding='utf-8') as f:
      writer = csv.DictWriter(f,
                              fieldnames=('input', 'expected_output', 'context'),
                              lineterminator='\n')
    
      writer.writeheader()
      writer.writerows(data)
    
    