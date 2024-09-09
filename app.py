import streamlit as st 
import pandas as pd 
import plotly.express as px 
import numpy as np
import matplotlib as plt
import altair 

cars = pd.read_csv('vehicles_us.csv')

cars['is_4wd'] = cars['is_4wd'].fillna(value=0)

cars['paint_color'] = cars['paint_color'].fillna(value='unknown')

avg_odo = cars['odometer'].mean()
med_odo = cars['odometer'].median()

cars['odometer'] = cars['odometer'].fillna(value=avg_odo)
cars['odometer'] = cars['odometer'].round(0)

cars = cars.dropna().reset_index()

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
    
cars['odometer_category'] = cars['odometer'].apply(odometer_category)


# Define your color sequence
color_seq = px.colors.qualitative.Plotly

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
stacked_bar.update_layout(width=800, height=600)
st.plotly_chart(stacked_bar)

st.header('Distribution of Vehicle Cost')

# Create a multiselect dropdown for the user to select two manufacturers
selected_paint = st.multiselect(
    'Select Paint Color',
    options=cars['paint_color'].unique(),
    default=cars['paint_color'].unique()[:2],  # Pre-select the first 2 manufacturers
    max_selections=3
)

# Filter the DataFrame based on the selected manufacturers
paint = cars[cars['paint_color'].isin(selected_paint)]
price_hist = px.histogram(paint,
                        x='price',
                        nbins=20,
                        title='Distribution of Vehicle Costs',
                        text_auto=True,
                        labels={'price': 'Vehicle Price (dollars)',
                                'count': 'Number of Vehicles'},
                        color_discrete_sequence=['#000080'])
price_hist.update_layout(bargap=.2) 
price_hist.update_layout(width=800, height=600)
st.plotly_chart(price_hist)

st.header('Odometer Reading by Manfucturer')
mfr_scat = px.scatter(cars,
                x='odometer',
                y='manufacturer',
                color='listing_category',
                title='Odometer Reading by Manufacturer',
                labels={'odometer': 'Odometer (Miles)',
                        'manufacturer': 'Manufacturer'},
                category_orders={'listing_category': ['Good', 'Fair', 'Poor', 'Very Poor']},
                color_discrete_sequence=color_seq)
mfr_scat.update_layout(width=800, height=600)
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
type_histogram.update_layout(width=800, height=600)
st.plotly_chart(type_histogram)

st.header('Price Distribution Between Manufacturers')

# Create a multiselect dropdown for the user to select two manufacturers
selected_manufacturers = st.multiselect(
    'Select up to 2 manufacturers',
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
price_compare.update_layout(width=800, height=600)
st.plotly_chart(price_compare)

st.header('Odometer Reading by Number of Days Listed')
odo_list = px.scatter(cars,
                    x='days_listed',
                    y='odometer',
                    color='condition',
                    title='Odometer Reading by Number of Listing Days',
                    labels={'odometer': 'Odometer (Miles)',
                            'days_listed': 'Number of Days on Market'},
                    category_orders={'condition': ['new', 'like new', 'excellent', 'good', 'fair', 'salvage']},
                    color_discrete_sequence=color_seq)
odo_list.update_layout(width=800, height=600)
st.plotly_chart(odo_list)

st.header('Odometer Reading by Number of Days Listed')
over_time = px.scatter(cars,
                    x='days_listed',
                    y='price',
                    size='odometer',
                    color='fuel',
                    facet_col='fuel',
                    color_discrete_sequence=color_seq,
                    size_max=35)
over_time.update_layout(width=800, height=600)
st.plotly_chart(over_time)

st.header('Trendlines and Marginal Distribution between Odometer Reading and Price')
scatter = px.scatter(cars,
                    x='price',
                    y='odometer',
                    color='condition',
                    trendline='ols',
                    marginal_x='violin',
                    marginal_y='box',
                    color_discrete_sequence=color_seq,
                    title='Trendlines and Marginal Distribution between Odometer Reading and Price')
scatter.update_yaxes(range=[-100000, 1000000])
scatter.update_layout(width=800, height=600)
st.plotly_chart(scatter)
