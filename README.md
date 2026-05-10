# Aviation Crisis Management Simulation

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aviationcrisismanagementsimulation-g8tdpjvenk879p6dtn4xc3.streamlit.app/)

## Project Overview
The Aviation Crisis Management Simulation is an advanced Business Intelligence (BI) dashboard designed to quantify the financial and operational impacts of sudden aviation disruptions (cancellations, diversions, and weather delays). 

Built as a strategic framework, this project acts as a "Crisis Simulator" that helps C-level executives and operations directors understand the domino effect of weather delays, identify bottleneck airports, and calculate estimated financial bleeding versus unplanned revenue during crises.

## Quick Links
* **Live Interactive Dashboard:** [View Streamlit App](https://aviationcrisismanagementsimulation-jd5fe3nu7bkczbjnc3fvzt.streamlit.app/)
* **Executive Presentation (Pitch Deck):** [View Gamma Presentation](https://gamma.app/docs/Aviation-Crisis-Management-Financial-Impact-Operational-Efficienc-ku6jklysn7clket)
* **Data Link in Kaggle:** [kaggle link](https://www.kaggle.com/datasets/usdot/flight-delays)


## Key Strategic Insights Discovered
1. **The Margin Killer:** While major airlines lose higher absolute dollar amounts during crises, regional and budget airlines suffer a much more severe "Margin Erosion" relative to their total revenue.
2. **The Snow Belt Bottleneck:** Unlike Southern airports that face sudden catastrophic closures, Northern airports experience "Operational Paralysis." Snow heavily impacts *Taxi-Out* times due to de-icing processes, causing cascading schedule delays rather than immediate cancellations.
3. **The Holiday Myth:** Data proves that holiday seasons actually see a *decrease* in average delays due to the absence of corporate travelers and padded airline scheduling.

## Dashboard Features (Power BI Style Experience)
* **Dynamic Theme Engine:** Fully functional Light/Dark mode toggle with custom CSS targeting for crisp KPI visibility.
* **Smart KPI Strip:** Real-time metrics tracking total flights, cancellations, average taxi-out delays, and dynamically formatted financial impacts (Millions/Billions).
* **Financial Analysis Tab:** Visualizes top airline financial bleeding, airport revenue gains (from diversions), and the critical **Margin Killer** comparison chart.
* **Operations Analysis Tab:** Breaks down the primary reasons for cancellations and tracks the **Winter Domino Effect** (Weather Delays vs. Taxi-Out Congestion) using multi-axis charts.
* **Geographic Crisis Explorer:** An interactive, optimized geospatial map plotting crisis hotspots and delay severity across the USA.

## Performance Optimization (Handling Big Data)
To ensure sub-second dashboard loading times with millions of records, the following Data Engineering techniques were applied:
* **Selective Sampling:** Retained 100% of "Crisis Outliers" (cancellations, diversions, weather delays) while sampling normal flights down to 5%. This preserved absolute analytical accuracy while drastically reducing memory footprint.
* **Static Coordinate Mapping:** Replaced live API Geocoding (`Geopy/Nominatim`) with pre-processed latitude/longitude columns to eliminate API rate limits and network bottlenecks.
* **Column Pruning & Parquet:** Stripped unnecessary columns and stored the final dashboard data in a highly compressed `.parquet` format.

## Technology Stack
* **Language:** Python
* **Web Framework:** Streamlit
* **Data Engineering & Manipulation:** Pandas, NumPy, PyArrow/FastParquet
* **Data Visualization:** Plotly Express, Plotly Graph Objects

## Local Installation

To run this project locally on your machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/somia-moslhy/Aviation_Crisis_Management_Simulation.git](https://github.com/somia-moslhy/Aviation_Crisis_Management_Simulation.git)
   cd Aviation_Crisis_Management_Simulation
