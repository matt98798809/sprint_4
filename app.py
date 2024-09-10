import streamlit as st 
import pandas as pd 
import plotly.express as px 
import numpy as np
import altair 

cars = pd.read_csv('vehicles_us.csv')

# Getting the first word from model to get manufacturer
cars = pd.read_csv('vehicles_us.csv')
cars['manufacturer'] = cars['model'].apply(lambda x:x.split()[0])

# Categorizing Days Listed
def listed_category(days):
    
    if days <= 30:
        return 'Good' 
    elif 31 <= days <= 60:
        return 'Fair' 
    elif 61 <= days <= 90:
        return 'Poor' 
    else:
        return 'Very Poor'
    
cars['listing_category'] = cars['days_listed'].apply(listed_category)   

# Filling in the missing values for cylinders and odometer based on model and model year
cars['cylinders_new'] = cars.groupby(['model', 'model_year'])['cylinders'].transform(lambda x: np.ceil(x.fillna(x.median())))
cars['odometer_new'] = cars.groupby(['model','model_year'])['odometer'].transform(lambda x:  x.fillna(x.median()))

# Categorizing Odometer
def odometer_category(reading):
    
    if reading <= 40000:
        return 'Good' 
    elif 40001 <= reading <= 70000:
        return 'Fair' 
    elif 70001 <= reading <= 100000:
        return 'Poor' 
    else:
        return 'Very Poor'
    
cars['odometer_category'] = cars['odometer_new'].apply(odometer_category)  

# Replacing NaN with 0
cars['is_4wd'] = cars['is_4wd'].fillna(value=0)

# Dropping missing values with model_year and and remaining missing values for cylinders_new
cars = cars.dropna(subset=['model_year','cylinders_new'])


# Define your color sequence
color_seq = px.colors.qualitative.Plotly

# Will be used to sort graph by frequency instead of manufacturer
manufacturer_counts = cars['manufacturer'].value_counts()

st.header('Data viewer')
show_data = st.checkbox('Show Data Table')
if show_data:
    st.write(cars)

st.header('Vehicle Types Produced by Manufacturer')

manufacturer_counts = cars['manufacturer'].value_counts()

stacked_bar = px.bar(cars,
                    x='manufacturer',
                    color='type',
                    title='Vehicle Types by Manufacturer',
                    color_discrete_sequence=color_seq,
                    height=500,
                    category_orders={'manufacturer': manufacturer_counts.index.tolist()})
stacked_bar.update_layout(barmode='stack')
stacked_bar.update_layout(width=1000, height=1000)
st.plotly_chart(stacked_bar)

st.header('Distribution of Vehicle Cost')

price_hist = px.histogram(cars,
                        x='price',
                        nbins=20,
                        title='Distribution of Vehicle Costs',
                        text_auto=True,
                        labels={'price': 'Vehicle Price (dollars)',
                                'count': 'Number of Vehicles'},
                        color_discrete_sequence=['#000080'])
price_hist.update_layout(bargap=.2) 
price_hist.update_layout(width=1000, height=1000)
st.plotly_chart(price_hist)

st.header('Odometer Reading by Manfucturer')
mfr_scat = px.scatter(cars,
                x='days_listed',
                y='price',
                color='listing_category',
                title='Days on Market by Price and Transmission Type',
                labels={'odometer_new': 'Odometer (Miles)',
                        'price': 'Price (dollars)'},
                color_discrete_sequence=color_seq,
                category_orders={'listing_category': ['Good', 'Fair', 'Poor', 'Very Poor']})
mfr_scat.update_layout(width=1000, height=1000)
st.plotly_chart(mfr_scat)

st.header('Vehicle Condition Over Time')

# Create a slider for the user to select the range of model years
year_range = st.slider(
    'Select model year range',
    min_value=int(cars['model_year'].min()),  # Minimum year in the dataset
    max_value=int(cars['model_year'].max()),  # Maximum year in the dataset
    value=(int(cars['model_year'].min()), int(cars['model_year'].max())),  # Default range
    step=1  # Increment step
)

# Filter the DataFrame based on the selected model year range
filtered_year = cars[(cars['model_year'] >= year_range[0]) & (cars['model_year'] <= year_range[1])]
type_histogram = px.histogram(filtered_year,
                            x='model_year',
                            color='condition',
                            color_discrete_sequence=color_seq,
                            category_orders={'condition': ['new','like new', 'excellent', 'good', 'fair', 'salvage']},
                            title='Condition of Vehicles by Year')
type_histogram.update_layout(bargap=.2) 
type_histogram.update_layout(width=1000, height=1000)
st.plotly_chart(type_histogram)

st.header('Price Distribution Between Manufacturers')

# Create a multiselect dropdown for the user to select two manufacturers
selected_manufacturers = st.multiselect(
    'Select up to 5 manufacturers',
    options=cars['manufacturer'].unique(),
    default=cars['manufacturer'].unique()[:2],  # Pre-select the first 2 manufacturers
    max_selections=5
)

# Filter the DataFrame based on the selected manufacturers
filtered_cars = cars[cars['manufacturer'].isin(selected_manufacturers)]
price_compare = px.histogram(filtered_cars,
                            x='price',
                            color='manufacturer',
                            color_discrete_sequence=color_seq,
                            title='Price Distribution Between Manufacturers',
                            height=600)
price_compare.update_layout(bargap=.2) 
price_compare.update_layout(width=1000, height=1000)
st.plotly_chart(price_compare)

st.header('Listing Days Based on Odometer Reading and Cylinders')
odo_list = px.histogram(cars,
                        x='days_listed',
                        y='price',
                        color='cylinders_new',
                        title='Listing Days Based on Odometer Reading and Cylinders',
                        labels={'odometer': 'Odometer (Miles)',
                                'days_listed': 'Number of Days on Market'},
                        color_discrete_sequence=color_seq,
                        category_orders={'cylinders_new': sorted(cars['cylinders_new'].unique(), key=int)})
odo_list.update_layout(width=1000, height=1000)
st.plotly_chart(odo_list)

st.header('Odometer Reading for Vehicle Fuel Types Over Time')
over_time = px.scatter(cars,
                    x='odometer_new',
                    y='model_year',
                    size='price',
                    color='transmission',
                    facet_col='fuel',
                    color_discrete_sequence=color_seq,
                    size_max=35,
                    title='Odometer Reading for Vehicle Fuel Types Over Time')
over_time.update_layout(width=1000, height=1000)
st.plotly_chart(over_time)

st.header('Trendlines and Marginal Distribution between Odometer Reading and Price')
scatter = px.scatter(cars,
                    x='price',
                    y='odometer_new',
                    color='condition',
                    trendline='ols',
                    marginal_x='violin',
                    marginal_y='histogram',
                    color_discrete_sequence=color_seq,
                    title='Trendlines and Marginal Distribution between Odometer Reading and Price',
                    height=800)
scatter.update_yaxes(range=[-100000, 1000000])
scatter.update_layout(width=1000, height=1000)
st.plotly_chart(scatter)
