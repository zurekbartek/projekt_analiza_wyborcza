import geopandas as gpd
import matplotlib.pyplot as plt


gminy_shp = gpd.read_file("C:\\Users\\zurek\\OneDrive\\Pulpit\\gminy z przyrostem\\powiaty\\A02_Granice_powiatow.shp")
print(gminy_shp.head())

gminy_shp.plot(figsize=(12, 12), edgecolor='black', color='lightblue')
plt.show()