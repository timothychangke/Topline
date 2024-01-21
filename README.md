# YOUR PROJECT TITLE
### Video Demo:  https://youtu.be/TrH1bro4mwo
### Description:
My project is a one stop shop for anything related to stocks. It is a website built on flask where its main purpose is to track the stock performance of stocks in a users portfolio as well as provide stock related news and information.
#### Portfolio Tracker
The portfolio tracker stores stocks added by the user into a sql database, where it tracks and returns live prices, in real time profit and loss as well as other useful metrics. The user has to input the stocks he or she owns together with information like the price it was bought at and when it was bought, so that the rate of return can be calculated. The portfolio itself can be manipulated on the site, with options to add, remove and change the purchase price or quantity. Invalid responses such as illogical dates and incorrect stock ticker symbols will return an error pop-up created through flash-messaging. A pie chart of the portfolio will be shown, giving the user a clear representation of what he or she owns.
#### News
The Website can return financial news by retrieving data from a news API. Stock inputs are taken from the stocks in the user's portfolio and sent to the news API so that the output is curated and relevant. Links to the entire article is provided as well.
#### Stock Info
A search bar at the top right hand corner allows for the user to search for any stock of their interest and stock-related information and pricing metrics will be returned. The information is provided by the iexcloud API
#### Account settings
Basic account settings like the changing of username and passwords are available as well.

Everything was built form scratch and the cs50 libraries were not used. It is admitted that the idea is simplistic and more emphasis was placed on functionality and aesthetic, but overall I think the it is a usable piece of code and I myself use it to track my portfolio. 