from ctgan import CTGAN
import pandas as pd

#PYTHON = 3.8.5 (Este código ha sido probado para python 3.8.5)

#data = pd.read_csv('./../data/rome_u_journeys.csv').sample(2000)

#discrete_columns = ['idS','tsO','tsD','price','tt','dis','vel','lonO','latO','lonD','latD']

#ctgan = CTGAN(batch_size=50,epochs=5,verbose=False)
#ctgan.fit(data, discrete_columns)
#ctgan.save('journeys.pkl')

model = CTGAN.load('./journeys.pkl')
new_data = model.sample(20)
new_data[['price', 'tt', 'dis', 'vel']] = new_data[['price', 'tt', 'dis', 'vel']].round(2)

new_data.to_csv('prueba.csv', index=False)