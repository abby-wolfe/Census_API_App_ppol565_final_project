# Import initial modules needed for data wrangling
import requests
import pandas as pd
import numpy as np

# Import data viz modules
import altair as alt
import plotly.express as px

# Import streamlit
import streamlit as st

# Request data from 2020 5 year ACS estimates at state level
r = requests.get("https://api.census.gov/data/2020/acs/acs5",
                params = {
                    "get":"NAME,B01001_001E,B19058_002E,B19058_003E,B17020I_002E,B06009_002E,B06009_003E,B06009_004E,B06009_005E,B06009_006E,B08137_003E,B25081_002E,B02001_003E,B03001_003E,B02001_004E,B27011_008E,B27011_013E",
                    "for":"state:*",
                })

# Create dataframe from ACS data based on json response
census_df = pd.DataFrame(columns=["state","pop","snap","non_snap","below_fpl","less_than_hs","hs","some_college","college_deg","grad_deg","rent","mortgage","black","hispanic","native","unemployed","not_in_labor_force","id"],
                        data=r.json()[1:])

# Remove observations with missing values (in this case, just Puerto Rico which was missing education statistics)
census_df = census_df.dropna()

# Convert data types in dataframe except state names to integer data
cols=[i for i in census_df.columns if i not in ["state"]]
for col in cols:
    census_df[col]=census_df[col].astype(int)
    
# Convert ACS variables to percentages from whole numbers
census_df["snap_pct"] = round(census_df["snap"]/census_df["pop"],3) # Percent that receive snap
census_df["fpl_pct"] = round(census_df["below_fpl"]/census_df["pop"],3) # Percent that are below the federal poverty level
census_df["deg"] = census_df["some_college"] + census_df["college_deg"] + census_df["grad_deg"] # Number of people w/ greater than high school education
census_df["deg_pct"] = round(census_df["deg"]/census_df["pop"],3) # Percent with more than a high school education
census_df["less_than_hs_pct"] = round(census_df["less_than_hs"]/census_df["pop"],3) # Percent with less than high school education
census_df["hs_pct"] = round(census_df["hs"]/census_df["pop"],3) # Percent with only high school education
census_df["some_coll_pct"] = round(census_df["some_college"]/census_df["pop"],3) # Percent with only some college or associate's degree
census_df["college_deg_pct"] = round(census_df["college_deg"]/census_df["pop"],3) # Percent with only bachelor's degree
census_df["grad_deg_pct"] = round(census_df["grad_deg"]/census_df["pop"],3) # Percent with graduate degree
census_df["rent_pct"] = round(census_df["rent"]/census_df["pop"],3) # Percent of rented properties
census_df["mortgage_pct"] = round(census_df["mortgage"]/census_df["pop"],3) # Percent of owned properties with mortgages
census_df["black_pct"] = round(census_df["black"]/census_df["pop"],3) # Percent of African-Americans
census_df["hispanic_pct"] = round(census_df["hispanic"]/census_df["pop"],3) # Percent of Hispanics
census_df["native_pct"] = round(census_df["native"]/census_df["pop"],3) # Percent of Native Americans
census_df["unemp_pct"] = round(census_df["unemployed"]/census_df["pop"],3) # Percent unemployed
census_df["not_in_lf_pct"] = round(census_df["not_in_labor_force"]/census_df["pop"],3) # Percent not in labor force

# Add state and region codes and merge to dataframe
state_dict = {'state':['Pennsylvania', 'California', 'West Virginia', 'Utah', 'New York',
       'District of Columbia', 'Alaska', 'Florida', 'South Carolina',
       'North Dakota', 'Maine', 'Georgia', 'Alabama', 'New Hampshire',
       'Oregon', 'Wyoming', 'Arizona', 'Louisiana', 'Indiana', 'Idaho',
       'Connecticut', 'Hawaii', 'Illinois', 'Massachusetts', 'Texas',
       'Montana', 'Nebraska', 'Ohio', 'Colorado', 'New Jersey',
       'Maryland', 'Virginia', 'Vermont', 'North Carolina', 'Arkansas',
       'Washington', 'Kansas', 'Oklahoma', 'Wisconsin', 'Mississippi',
       'Missouri', 'Michigan', 'Rhode Island', 'Minnesota', 'Iowa',
       'New Mexico', 'Nevada', 'Delaware', 'Kentucky',
       'South Dakota', 'Tennessee'], 
              'state_code': ['PA','CA','WV','UT','NY','DC','AK','FL','SC','ND','ME','GA','AL',
                             'NH','OR','WY','AZ','LA','IN','ID','CT','HI','IL','MA','TX','MT',
                             'NE','OH','CO','NJ','MD','VA','VT','NC','AR','WA','KS','OK','WI',
                            'MS','MO','MI','RI','MN','IA','NM','NV','DE','KY','SD','TN'],
             'region': ['Northeast','West','South','West','Northeast','South','West','South',
                        'South','Midwest','Northeast','South','South','Northeast','West','West',
                       'West','South','Midwest','West','Northeast','West','Midwest','Northeast',
                       'South','West','Midwest','Midwest','West','Northeast','South','South',
                       'Northeast','South','South','West','Midwest','South','Midwest','South',
                       'Midwest','Midwest','Northeast','Midwest','Midwest','West','West','South',
                       'South','Midwest','South']}
states_df = pd.DataFrame(data=state_dict)
census_df = census_df.merge(states_df, how='left', on='state')

# App title
st.title("SNAP Participation Dashboard")

# App text
"""
## What is SNAP?
SNAP stands for the Supplemental Nutrition Assistance Program. It's a social safety net program designed to give low-income households monthly benefits toward buying groceries. It was first enacted by President Lyndon Johnson as the Food Stamp Program in the Food Stamp Act of 1964. In 2008, the name of the program was changed to SNAP.
## Why is SNAP important?
Despite being one of the wealthiest nations in the world, the United States has a major issue with food insecurity. Today, there are a record number of people who use and rely on SNAP to buy their groceries and get their necessary nutrients. It was especially important at the beginning of the COVID-19 pandemic when worsened economic conditions resulted in a rapid growth in SNAP eligibility and participation. The U.S. Department of Agriculture estimates that 43 million people received SNAP benefits in April 2020, a great increase from 35.7 million people in 2019.
## What is the goal of this project?
The goal of this project is to de-stigmatize social safety net programs like SNAP by giving a holisitic view of the demographic factors that could potentially influence whether someone is eligible for SNAP. By analyzing state trends on a macro level rather than looking at individual determinants, we can get a better picture as to what makes up communities that need better access to nutrition. For instance, by analyzing renting and mortgage rates, we can see what role cost of living plays in SNAP eligibility. Or, by analyzing educational attainment, we can see what role economic mobility plays in SNAP eligibility. Presenting data in this way helps us understand the bigger picture of food insecurity and who it affects.
## How do I use this app?
All you have to do is scroll down to the plot sections of the app and choose which variables and panels you would like to see! For each plot, we have provided an interpretation of the trends observed. All of the plots are interactive, so if you move your cursor over any of the data points, you will find a label that tells you what state your cursor is on and what their SNAP participation rate is.
"""

"""
## Let's look at our data...
Here is a sample of our dataset, featuring our variables of interest taken from the ACS 2020 5-year estimates. Our variables include state, population, SNAP participation rate, poverty rate, unemployment rate, labor force participaton rate, the rate of educational attainment past the high school level, percentages of racial minorities, renting rate, and mortgage rates. All of these variables are state averages over the period of 2016-2020. Our key dependent variable that we'll be analyzing is snap_pct.
"""
st.dataframe(census_df[["state","pop","snap_pct","fpl_pct","unemp_pct","not_in_lf_pct","deg_pct","black_pct","hispanic_pct","native_pct","rent_pct","mortgage_pct"]].head())

"""
The graph below shows the average SNAP participation rate from 2016-2020 by state. If you move your cursor over any of the states in the plot, you'll see both the state code and the percentage of people in that state that rely on SNAP benefits.
"""

px_plot = px.choropleth(census_df,
                    locations='state_code', 
                    locationmode="USA-states", 
                    scope="usa",
                    color='snap_pct',
                    color_continuous_scale="Viridis_r",                   
                    )
st.plotly_chart(px_plot, use_container_width=True)

"""
As we can see, between 2016-2020, the states with the highest concentrations of SNAP participants tend to be concentrated in the eastern half of the country. There are some exceptions, such as New Mexico and Oregon, that are located in the western half of the country. Let's also note that there are some states that have very high SNAP participation rates in the eastern half, such as West Virginia, Louisiana, Mississippi, Rhode Island, New York, Maine, and Pennsylvania.

### Variable Colored Chloropleths

Now, let's look at some of the other variables in our dataset...
"""

# Plot function (chloropleth)
def plot_chloropleth(var):
    '''
    This function takes a variable input and plots a colored chloropleth by state of that variable.
    '''
    px_plot_var = px.choropleth(census_df,
                    locations='state_code', 
                    locationmode="USA-states", 
                    scope="usa",
                    color=var,
                    color_continuous_scale="Viridis_r",                    
                    )
    st.plotly_chart(px_plot_var, use_container_width=True)

# Plot function (scatter plot)
def plot_scatter(var):
    '''
    This function takes a variable input and plots an interactive scatter graph of that variable against snap participation by state.
    '''
    alt_plot = alt.Chart(census_df).mark_circle().encode(
        x=var,
        y='snap_pct',
        color='region',
        size='pop',
        tooltip=['state','snap_pct'])
    st.altair_chart(alt_plot + alt_plot.transform_regression(var,'snap_pct').mark_line(), use_container_width=True)
    
# Choose your own adventure chloropleths    
c_var = st.selectbox("Choose another variable to look at:", ("Poverty Rate", "Unemployment Rate", "Labor Force Participation Rate", "Education Greater than High School", "Percent African-American", "Percent Hispanic", "Percent Native American", "Renting Rate", "Mortgage Rate"))

if "Poverty Rate" in c_var:
    # Plot data
    plot_chloropleth('fpl_pct')
    # Comment on trends
    st.write("As we can see here, the states with the highest concentration of people living below the federal poverty level tend to be most concentrated in the southwest. This includes states like New Mexico, Texas, Arizona, and California.")
elif "Unemployment Rate" in c_var:
    # Plot data
    plot_chloropleth('unemp_pct')
    # Comment on trends
    st.write("We can see a more even distribution in unemployment here. However, it's perhaps worth noting again that many of the states with higher unemployment rates happen to be in the eastern half of the country. Especially, Louisiana, Mississippi, West Virginia, New York, Connecticut, New Jersey, Illinois, and Michigan.")
elif "Labor Force Participation Rate" in c_var:
    # Plot data
    plot_chloropleth('not_in_lf_pct')
    # Comment on trends
    st.write("Despite the label, this plot depicts the percentages of adults not in the labor force by state. As we can see, there is a clear divide here. Many of the states with the highest percentages of adults not in the labor force are located in the south, such as Louisiana, Mississippi, Alabama, Arkansas, West Virginia, and Kentucky.")
elif "Education Greater than High School" in c_var:
    # Plot data
    plot_chloropleth('deg_pct')
    # Comment on trends
    st.write("As we can see, the states with the highest concentration of post-high school education are located in the northeast and the west. Whereas the states with the lowest concentration of post-high school education are located in the southern census region, such as West Virginia, Louisiana, Arkansas, and Mississippi")
elif "Percent African-American" in c_var:
    # Plot data
    plot_chloropleth('black_pct')
    # Comment on trends
    st.write("As we can see, the states with the highest concentrations of African-Americans are in the southern census region, such as Louisiana, Mississippi, and Georgia")
elif "Percent Hispanic" in c_var:
    # Plot data
    plot_chloropleth('hispanic_pct')
    # Comment on trends
    st.write("As we can see, most of the states with the highest concentrations of Hispanics are in the western census region, such as New Mexico and California")
elif "Percent Native American" in c_var:
    # Plot data
    plot_chloropleth('native_pct')
    # Comment on trends
    st.write("Again, most of the states with the highest concentrations of Native Americans are in the western census region. Most notably New Mexico, South Dakota, and Alaska")
elif "Renting Rate" in c_var:
    # Plot data
    plot_chloropleth('rent_pct')
    # Comment on trends
    st.write("Most of the states here have a more even distribution. However, it's worth noting that West Virginia is well below the national average and states like California, Nevada, and New York are well above the national average of renters. This could indicate a higher cost of living for those states with high percentages of renters and thus higher SNAP participation.")
elif "Mortgage Rate" in c_var:
    # Plot data
    plot_chloropleth('mortgage_pct')
    # Comment on trends
    st.write("Most of the states with the highest concentrations of people with mortgages tend to be in the northern half of the country, such as Maine, New Hampshire, Vermont, and Minnesota. In addition to renting rates, mortgage rates could potentially be a good indicator of cost of living.")


# Choose your own adventure stacked bar plots
'''
### Demographics - Stacked Bar Plots

Now let's look at how some demographic information compares across states to get a more complete profile...
'''

b_var = st.selectbox("Choose a demographic level to explore at the state level:", ("Race", "Education level: High School or Less", "Education Level: Greater than High School", "Housing"))

if "Race" in b_var:
    # Plot data
    bar_plot = px.bar(census_df, x="state", y=["black_pct", "hispanic_pct", "native_pct"])
    st.plotly_chart(bar_plot, use_container_width=True)
    # Comment on trends
    st.write("This stacked bar plot shows the composition of racial minorities by percentages. It's worth noting here that according to this plot, the states with the largest percentages of racial minorities are New Mexico, Texas, and the District of Columbia. This plot has some relevance because it's likely that people who are members of a racial minority in the United States will have had less opportunity to build generational wealth because of historic barriers, which could potentially influence SNAP eligibility in the long run.")
elif "Education level: High School or Less" in b_var:
    # Plot data
    bar_plot = px.bar(census_df, x="state", y=["less_than_hs_pct", "hs_pct"])
    st.plotly_chart(bar_plot, use_container_width=True)
    # Comment on trends
    st.write("This stacked bar plot shows the composition of people whose highest level of educational attainment is at the high school level or below. The states with the highest values in this plot are West Virginia, Louisiana, Arkansas, Kentucky, Pennsylvania, and Tennessee. This plot has some relevance as we could use educational attainment level as a proxy for economic mobility. So, the states with proportionately greater numbers of residents with a high school education or less may be more likely to have more residents that are SNAP eligible.")
elif "Education Level: Greater than High School" in b_var:
    # Plot data
    bar_plot = px.bar(census_df, x="state", y=["some_coll_pct","college_deg_pct", "grad_deg_pct"])
    st.plotly_chart(bar_plot, use_container_width=True)
    # Comment on trends
    st.write("This stacked bar plot shows the composition of people whose highest level of educational attainment is at higher than a high school level. This includes people with a bachelor's or graduate degree as well as those with some college education but not a degree and an associate's degree. This plot has some relevance as we could use educational attainment level as a proxy for economic mobility. So, in contrast to the previous plot, we can say that the states with the smallest values on this plot tend to have less upwardly economically mobile residents such as West Virginia or Louisiana. In contrast, the states with the largest values on this plot tend to be more upwardly economically mobile, such as the District of Columbia or Washington.")
else:
    # Plot data
    bar_plot = px.bar(census_df, x="state", y=["rent_pct","mortgage_pct"])
    st.plotly_chart(bar_plot, use_container_width=True)
    # Comment on trends
    st.write("This stacked bar plot shows the composition of people who rent or have a mortgage by state. The intuition behind this panel is that the states with the highest values on this plot are the states that tend to have the highest comparative cost of living and that are perhaps the least affordable. In a manner of speaking, these are the states where you don't get your bang for your buck, meaning that your salary does not go as far in these states as perhaps it would in more affordable states. So, it's likely that with a higher cost of living that there may also be a greater relative proportion of people who are SNAP eligible. Based on this plot, these states include the District of Columbia, Oregon, California, and Colorado.")
    

# Choose your own adventure scatter plots
'''
### Two Variable Scatter Plots

Now let's compare our variables side-by-side using a scatter plot. The datapoints are color coded based on census region and sized proportionate to state population.
'''

s_var = st.selectbox("Choose a variable to plot against SNAP participation rate:", ("Poverty Rate", "Unemployment Rate", "Labor Force Participation Rate", "Education Greater than High School", "Percent African-American", "Percent Hispanic", "Percent Native American", "Renting Rate", "Mortgage Rate"))

if "Poverty Rate" in s_var:
    # Plot data
    plot_scatter('fpl_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the poverty rate and the percentage of people that receive SNAP benefits. As we can see, there is a weak, slightly positive relationship between these two variables. This indicates that there is likely little evidence of feature significance.")
elif "Unemployment Rate" in s_var:
    # Plot data
    plot_scatter('unemp_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the unemployment rate and the percentage of people that receive SNAP benefits. As we can see, there is a strong positive relationship between these two variables. Thus, it's likely that unemployment has some influence on SNAP participation.")
elif "Labor Force Participation Rate" in s_var:
    # Plot data
    plot_scatter('not_in_lf_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the percentage of people not in the labor force and the percentage of people that receive SNAP benefits. As we can see, there is a strong positive relationship between these two variables. Thus, it's likely that not being in the labor force has some influence on SNAP participation.")
elif "Education Greater than High School" in s_var:
    # Plot data
    plot_scatter('deg_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the percentage of people with post-high school education and the percentage of people that receive SNAP benefits. These two variables have a somewhat strong negative relationship. Thus, it's likely that educational attainment has some influence on SNAP participation.")
elif "Percent African-American" in s_var:
    # Plot data
    plot_scatter('black_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the percentage of African-Americans and the percentage of people that receive SNAP benefits. As we can see, there is a weak, slightly positive relationship between these two variables. This indicates that there is likely little evidence of feature significance.")
elif "Percent Hispanic" in s_var:
    # Plot data
    plot_scatter('hispanic_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the percentage of Hispanic people and the percentage of people that receive SNAP benefits. As we can see, there is likely a correlation coefficient close to zero for these two variables. This indicates that this variable is not of any significance.")
elif "Percent Native American" in s_var:
    # Plot data
    plot_scatter('native_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the percentage of Native Americans and the percentage of people that receive SNAP benefits. As we can see, there is likely a correlation coefficient close to zero for these two variables. This indicates that this variable is not of any significance.")
elif "Renting Rate" in s_var:
    # Plot data
    plot_scatter('rent_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the renting rate and the percentage of people that receive SNAP benefits. As we can see, there is a weak, slightly negative relationship between these two variables. This indicates that there is likely little evidence of feature significance.")
else:
    # Plot data
    plot_scatter('mortgage_pct')
    # Comment on trends
    st.write("This scatter plot shows the relationship at the state level between the mortgage rate and the percentage of people that receive SNAP benefits. These two variables have a somewhat strong negative relationship. Thus, it's likely that mortgage rates have some influence on SNAP participation.")

    
# Text box for user input    
'''
## Feedback
Thank you for making it to the end! Now, we would like to hear from you!
'''
st.text_input("What is something you learned from this app?")

# Citations (includes data, python packages, and articles)
'''
## Works Cited
Center on Budget and Policy Priorities. (2022, January 6). *A quick guide to snap eligibility and Benefits.* Center on Budget and Policy Priorities. Retrieved from https://www.cbpp.org/research/food-assistance/a-quick-guide-to-snap-eligibility-and-benefits

Chandra, R. V., & Varanasi, B. S. (2015). *Python requests essentials.* Packt Publishing Ltd.

Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., … Oliphant, T. E. (2020). Array programming with NumPy. *Nature, 585*, 357–362. https://doi.org/10.1038/s41586-020-2649-2

Inc., P. T. (2015). Collaborative data science. Montreal, QC: Plotly Technologies Inc. Retrieved from https://plot.ly

McKinney, W., & others. (2010). Data structures for statistical computing in python. In *Proceedings of the 9th Python in Science Conference* (Vol. 445, pp. 51–56).

Tiehen, L. (2020, August 3). *Taking a closer look at Supplemental Nutrition Assistance Program (SNAP) participation and expenditures. USDA Economic Research Service.* Retrieved from https://www.ers.usda.gov/amber-waves/2020/august/taking-a-closer-look-at-supplemental-nutrition-assistance-program-snap-participation-and-expenditures/#:~:text=Preliminary%20national%20data%20available%20at,SNAP%20benefits%20in%20April%202020. 

U.S. Census Bureau (2022). *2016-2020 American Community Survey 5-year Estimates.* Retrieved from [https://www.census.gov/data/developers/data-sets/acs-5year.html](https://www.census.gov/data/developers/data-sets/acs-5year.html)

U.S. Department of Agriculture. (2018, September 11). *A short history of snap.* USDA Food and Nutrition Service. Retrieved from https://www.fns.usda.gov/snap/short-history-snap 

VanderPlas, J., Granger, B., Heer, J., Moritz, D., Wongsuphasawat, K., Satyanarayan, A., … Sievert, S. (2018). Altair: Interactive statistical visualizations for python. *Journal of Open Source Software*, 3(32), 1057.
'''