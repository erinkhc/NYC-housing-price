
## What you have implemented in your dashboard so far and explain what is not yet implemented.

#### All have been implemented at this moment.

##### Overall

Filtering Options: Users can filter properties based on locality and type (houses, condos, etc.), allowing for a search experience that is tailored to specific preferences.

##### Type Section

- Direct Area Selection via Map: 

    The dashboard integrate with a mapping service, likely Google Maps, which allows users to directly select and view properties in a specific area. This feature provides a user-friendly way to find properties by navigating the map, enhancing the search experience by visualizing the location context.

- Price Range Selector: 

A slider is available for users to set a price range, helping them filter properties within their budget.

- Comparative Price Metrics: 

A boxplot is included to compare the price per square foot across different boroughs, assisting users in evaluating market values in various areas.

- Market Composition Analysis: 

The dashboard features a pie chart showing the distribution of property types, which provides an overview of the types of properties available and their prevalence in the market.


##### Borough Section

- Broker Activity Insights: 

A bar chart showing the transaction counts for the top real estate brokers in NYC gives an idea of which brokers are most active.

- Borough-Level Market Overview: 

A color-coded map is present to demonstrate average property prices in different boroughs, providing a geographical perspective on property values.

- Bubble Chart: 

There is a bubble chart that likely visualizes the volume of properties or the average price point in comparison to other variables such as property type or location.

- Bedroom and Bathroom Filters: 

Users have the option to filter properties based on the number of bedrooms and bathrooms, allowing for more refined searches that match specific living space requirements.



## Strengths

- Multi-Dimensional Analysis: 

By offering insights both by type of property and by borough, users can perform a multi-dimensional analysis. 

- Visual Data Representation: 

The use of maps, bubble charts, boxplots, and pie charts provides a visual representation of data, making it easier to understand and analyze trends at a glance.

- Interactivity: 

The filters for price range, house type, and locality suggest a level of interactivity that allows users to narrow down their search according to their preferences.

- Comparative Analysis: 

The boxplot provides a comparison of price per square foot across different boroughs, which can help in understanding the relative market values.




## Limitation

- Lack of Essential Infrastructure Information: 

Access to healthcare and transportation is a significant consideration when purchasing property. Without this information, users may not be able to fully assess the convenience and suitability of a particular area.

- Static Data without Updates: 

The real estate market is dynamic, and new data can significantly affect market trends. If the database does not update in real-time, the information viewed by users may not reflect current market conditions.

- Absence of Trend Analysis: 

The inability to observe historical trends may prevent users from understanding market development and predicting future changes. This is especially important for those trying to make long-term investment decisions.

## Future Improvement  

- Boxplot Clarity: 

Currently, some data points in the boxplot are difficult to discern due to crowding, particularly because of outliers. The plan is to adjust the scale of the x-axis to spread out the data points for better visibility.

- Graph Titles: 

Some graphs are missing titles that explain what they represent. Adding descriptive titles to each graph will provide users with immediate context and understanding of the data being presented.

- Price Display Enhancement: 

At present, the prices are displayed as plain text. The intention is to embed the price within a designated frame or box to make it stand out and improve readability.

