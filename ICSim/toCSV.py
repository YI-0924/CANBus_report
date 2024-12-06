import pandas as pd

output = "test_value.csv"

df = pd.read_csv('candumpFile.log', engine='python')
df.to_csv(output, index=None)
