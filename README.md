# Example Dash App

Per request, May 2021. WIP.
<br>
Will demonstrate user authentication and session management and dash interactive dashboard.

TODO:
<ol>
<li>Create Flask App with required authentication & test users - DONE</li>
<li>Create data downloader & optimiser - DONE</li>
<li>Create sample dashboard - 50%</li>
</ol>

Update as 2021-05-27
<br>
Callbacks on graph scale and other formatting remains outstanding.

# How to run

<ol>
<li>Clone this repo</li>
<li>run `pip install -r requirements.txt` to install any dependancies</li>
<li>Run main.py</li>
    <ol>
    <li>The sample database and users will be created automatically and auth params presented on home screen</li>
    <li>Sample data from Kaggle will be automatically loaded and formatted (terminal prompts on progress provided)</li>
        <ol>
            <li>[New York Yellow Taxi Trip Data](https://www.kaggle.com/microize/newyork-yellow-taxi-trip-data-2020-2019)</li>
            <li>Approx 13m rows, 1.2gb download size, not stored, then aggregated & optimised to 14kb</li>
        </ol>
    </ol>
    <li>The web page will load once the dataset has finished loading & optimising</li>
</ol>