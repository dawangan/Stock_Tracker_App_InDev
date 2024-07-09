# Stock_Tracker_App_InDev/Visual Augment Stock Tracking Tool (VASTT) 

This application is a concept program intended to visualize a user's portfolio, show similar assets using various vectorized metrics, and abstract the code underneath a user-friendly interface. 

# Setup
First, you'll want to download all files and store them in a singular folder. Next, navigate to the 'RecModule.py' file and press ctrl+F. Enter in "TODO" in the textbox, and proceed to the "return_my_assets" function. Replace your username and password in the rh.robinhood.login command. Do the same for the pyqt5_App.py file by also entering  in "TODO" in the textbox, and proceeding to the "download_data" function. Replace your username and password in the rh.robinhood.login command.

Upon running the pyqt5_App.py, you may encounter an API request from Robinhood in your cmdline which will require a mobile authenticator. 

After clearing this checkpoint, you may run pyqt5_App.py as is!

# Functionality Guide
![image](https://github.com/dawangan/Stock_Tracker_App_InDev/blob/main/imagefolder/345260479-143f5088-9c5b-4db4-9779-56ecead6d698.png)

This is what the GUI looks like for me when I run "pyqt5_App.py".

![image](345260748-11ffc06b-48e3-4fd4-9314-87379bff4e38.png)

The first dropdown menu (shown in red) is the current stock being shown in the figure. 

![image](345260903-d2cfedc0-b713-493b-9eeb-717d864b1d40.png)

The second dropdown menu (shown in red) is a list of all similar stocks as determined by the algorithm in 'RecModule.py'. 

![image](345261227-ade98a2b-ad8b-47b2-9b1e-c176205fbc92.png)

The scroller can be used to show the current stock price as shown in the textbox below the scroller (red for the scroller, blue for the textbox). 

![image](345261469-8b1ee5af-1f6a-4c6e-a2c2-6a895be7311b.png)

The 'Update Data' button is used to update the chart with the current selected stock shown in the upper dropdown menu.

![image](345261504-a98937a1-769b-403c-8f66-b4e536023e87.png)

The 'Plot Overlay' function plots the chosen recommended stock (lower dropdown menu) on the graph. 
![image](345264946-f5e94142-12e6-4034-8199-43c0dd337e01.png)

The 'Update Stock Data' Button scrapes through every ticker listed in 'company_tickers_mod', a list of 500 of the largest companies currently available on exchanges. Upon pressing, the application will lag out for a bit, but a progress bar will become green as soon as all available data is downloaded. This process generally takes around ~5 minutes, but is dependent upon a user's network as well as the 'yfinance' API (https://pypi.org/project/yfinance/). 

This project is currently around 2 months old but is being periodically updated when I'm not at work; future features will be added for further convenience of analyis and as an exercise. 
