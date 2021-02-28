# Import necessary libraries

from flask import Flask, render_template, redirect
import pymongo
import scrape_mars
import config

# Create an instance of Flask
app = Flask(__name__)

# Connect to mongo db and collection
client = pymongo.MongoClient(config.mongo_conn)
db = client[config.db_name]
mars_scrape = db.scrape

# Route to render index.html template using data from Mongo
@app.route("/")
def home():
    # Statement that finds all the items in the db and sets it to a variable
    mars_data = mars_scrape.find_one()

    # Make sure we have data if not go get it.
    if mars_data is None:
        # Redirect to scrape data 
        return redirect("/scrape")

    # Render an index.html template and pass it the data you retrieved from the database
    return render_template("index.html", mars=mars_data)



# Route that will run the scrape function
@app.route("/scrape")
def scrape():
    # Run the scrape function
    mars_scrape_data = scrape_mars.scrape()

    # Update the Mongo database using update and upsert=True
    mars_scrape.update({}, mars_scrape_data, upsert=True)

    # Redirect back to home page
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
