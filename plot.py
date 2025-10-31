import matplotlib.pyplot as plt
import geopandas
import sys

print(f'Reading file: {sys.argv[1]}, Writing to: {sys.argv[2]}')

df = geopandas.read_parquet(sys.argv[1])
df.plot()

plt.savefig(sys.argv[2])