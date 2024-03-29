# NYC-housing-price

This dashboard provides users with a comprehensive overview of the New York real estate market, allowing them to browse property information through interactive maps and filtering features. The predictive tools and real estate agent rankings assist users in making informed purchasing decisions.

## Dash App Link:

Heroku Link: [NYC_housing_price_heroku](https://nyc-b429e9209531.herokuapp.com/)

## Dash App Description

This Dash application page is designed for investors looking to enter the New York real estate market and individuals hoping to settle in New York, offering users a comprehensive analysis of the New York housing market. It aims to provide an information-rich and easy-to-use platform through integrated data views and user-friendly interaction, enabling users to make informed choices in the complex New York real estate market. Its core value lies in enabling users to better understand property values and their distribution through intuitive data visualization.

### Page 1 description and preview 

The navigation bar on the left side of the page serves as the quick navigation tool for the entire Dash application, acting as the starting point for users. It allows users to access housing price information based on different data views (maps, types, areas), thus exploring the market from multiple dimensions.

The interactive map in the center displays the geographical distribution of properties, cleverly conveying information about property prices and sizes through the color and size of the dots. The gradient of colours from light to dark maps the price range from low to high, while the size of the dots is directly linked to the actual area of the properties, providing a seamless interpretation experience for users. When users hover their mouse over a point on the map, it displays detailed data for each property, such as address, area, pricing, and the specific layout of the house. These instantly displayed data points ensure that users have sufficient information when making decisions. And after a point on the map is clicked, the lower right area of the page will display richer information, such as key infrastructure near the property. This includes medical institutions, leisure parks, and shopping centers, which are crucial for assessing the convenience of living near the property.

The filter in the upper right corner offers customized search functionality, allowing users to narrow down their search based on specific locations, house types, and price ranges, making the process of finding the ideal property more direct and personalized.


![NYC sketch 1](https://github.com/erinkhc/NYC-housing-price/blob/main/page_1_0.png)

![NYC sketch 1](https://github.com/erinkhc/NYC-housing-price/blob/main/page_1_1.png)

### Page 2 description and preview
This Type page allows users to navigate the New York housing market by selecting specific types of properties to view detailed data on. Users can choose from several housing types using the dropdown menu, which includes options for all properties, condos,  houses, multi-family, townhouses, and other property types not categorized under the previous options. Once a selection is made, the page updates to show the price per square foot and the number of properties in each of the five boroughs of New York City: Bronx, Brooklyn, Manhattan, Queens, and Staten Island.

The left side is the boxplot presents the price per square foot, with each borough indicated on the vertical axis and a range from $0 to $20,000 on the horizontal axis. Different colors represent individual properties.On the right, a pie chart presents the distribution of property counts across the regions, with each borough denoted by a unique color that matches the legend provided. This intuitive design offers potential buyers or renters a custom-tailored insight into market trends and property availability, based on their housing preferences.

![NYC sketch 1](https://github.com/erinkhc/NYC-housing-price/blob/main/page_2.png)

### Page 3 description and preview

To use this web application for exploring real estate in New York City, users would start by selecting one of the boroughs from the map in the upper left-hand side. After a borough is selected, the following should happen:

1. Update of the Bubble Chart: The bubble chart in the upper right-hand side will update to display the distribution of property types within the selected borough. Each bubble represents a different type of property (such as Co-op, Condo, House, Multi-family, Townhouse, and others) and shows the quantity of available properties as well as the average rate for that property type.

2. Update of the Broker Chart: Concurrently, the bar chart in the lower right-hand side will update to show the top 5 real estate brokers in the selected borough. This chart lists brokers by name and shows a count of their transaction volume.

3. Using the Filters: On the lower left-hand side, users can use filters to select the desired number of bedrooms and bathrooms for a property. Once these filters are applied, the application will display the lowest and highest price range for the properties that meet the selected criteria.

By default, the application displays data for all properties across all boroughs. As users interact with the map and filters, the application dynamically updates the charts and data displayed to match their selections, providing a tailored view of the real estate market based on their preferences.

![NYC sketch 1](https://github.com/erinkhc/NYC-housing-price/blob/main/page_3.png)

## Sketch Description

The first page of this dashboard contains an interactive map with a filter. By clicking on the red icons on the map, users can view detailed property information like area, price, district, etc. And they can filter their desired house on the map by region, type, and price. In the lower half page, the left-side filter allows users to select the type of house they are interested in, which updates the boxplot to display the price distributions for each region of New York of the selected housing type. The pie chart illustrates the market shares of this housing type across different regions of New York.

![NYC sketch 1](https://github.com/erinkhc/NYC-housing-price/blob/main/sketch1.png)

The second page of the dashboard offers a window into each locality of New York. It showcases essential data like average real estate prices, income statistics, and amenities (e.g. parks). This interactive map highlights the socio-economic pulse of the districts. While users select one locality, predictive tools on the left-bottom can predict the housing price range factoring in bedrooms, bathrooms, and space they selected. The bar plot in the bottom right also lists top-5 real estate brokers by the volume of their listings, guiding buyers to the most active agents in the selected locality. 

![NYC sketch 2](https://github.com/erinkhc/NYC-housing-price/blob/main/sketch2.png)

