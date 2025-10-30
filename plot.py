import matplotlib.pyplot as plt
import geopandas
import sys

df = geopandas.read_parquet(sys.argv[1])
df.plot()

plt.savefig(sys.argv[1])