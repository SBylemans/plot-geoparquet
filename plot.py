import matplotlib.pyplot as plt
import geopandas
import sys
import io
import s3fs


print(f'Reading file: {sys.argv[1]}, Writing to: {sys.argv[2]}')

df = geopandas.read_parquet(sys.argv[1])
df.plot()

img_data = io.BytesIO()
plt.savefig(img_data, format='png')

s3 = s3fs.S3FileSystem()
with s3fs.S3File(mode='wb', s3=s3, path=sys.argv[2]) as f:
    f.write(img_data.getvalue())