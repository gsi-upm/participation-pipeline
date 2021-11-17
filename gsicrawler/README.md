# GSICrawler

GSICrawler is a service that extracts information from several sources, such as Twitter, Facebook and news outlets.

GSICrawler uses these services under the hood:

* The HTTP API for the scrapers/tasks (web). **This is the public-facing part, the one with which you will interact a user.**
* A frontend for celery (flower)
* A backend that takes care of the tasks (celery)
* A broker for the celery backend (redis)

There are several scrapers available, each accepts a different set of parameters (e.g. a query, a maximum number of results, etc.).
The results of any scraper can be returned in JSON format, or stored in an elasticsearch server.
Some results will take long to process.
If that is the case, the API will return information about the running task, so you can query the service for the result later.
Please, read the API specification for your scraper of interest.


Example:

```
# Scrape NYTimes for articles containing "terror", and store it in an elasticsearch endpoint (`http://elasticsearch:9200/crawler/news`).
$ curl -X GET --header 'Accept: application/json' 'http://0.0.0.0:5000/api/v1/scrapers/nyt/?query=terror&number=5&output=elasticsearch&esendpoint=elasticsearch&index=crawler&doctype=news'

{
  "parameters": {
    "number": 5,
    "output": "elasticsearch",
    "query": "terror"
  },
  "source": "NYTimes",
  "status": "PENDING",
  "task_id": "bf5dd994-9860-4c63-975e-d09fb85a463c"
}


# The task
$ curl --header 'Accept: application/json' 'http://0.0.0.0:5000/api/v1/tasks/bf5dd994-9860-4c63-975e-d09fb85a463c' 

{
  "results": "Check your results at: elasticsearch/crawler/_search",
  "status": "SUCCESS",
  "task_id": "bf5dd994-9860-4c63-975e-d09fb85a463c"
}
```

## Instructions

Some of the crawlers require API keys and secrets to work.
You can configure the services locally with a `.env` file in this directory.
It should look like this:

```
TWITTER_ACCESS_TOKEN=<YOUR VALUE>
TWITTER_ACCESS_TOKEN_SECRET=<YOUR VALUE>
TWITTER_CONSUMER_KEY=<YOUR VALUE>
TWITTER_CONSUMER_SECRET=<YOUR VALUE>
FACEBOOK_APP_ID=<YOUR VALUE>
FACEBOOK_APP_SECRET=<YOUR VALUE>
NEWS_API_KEY=<YOUR VALUE>
NY_TIMES_API_KEY=<YOUR VALUE>
```

Once the environment variables are in place, run:

```
docker compose up
```

This will start all the necessary services, with the default configuration.
Additionally, it will deploy an elasticsearch instance, which can be used to store the results of the crawler.


You can test the service in your browser, using the OpenAPI dashboard: http://localhost:5000/



## Scaling and distribution 

For ease of deployment, the GSICrawler docker image runs three services in a single container (web, flower and celery backend).
However, this behavior can be changed by using a different command (by default, it's `all`) and setting the appropriate environment variables:

```
GSICRAWLER_BROKER=redis://localhost:6379
GSICRAWLER_RESULT_BACKEND=db+sqlite:///usr/src/app/results.db
# If results_backend is missing, GSICRAWLER_BROKER will be used
```


## Developing new scrapers

As of this writing, to add a new scraper to GSICrawler you need to:

* Develop the scraping function
* Add a task to the `gsicrawler/tasks.py` file
* Add the task to the controller (`gsicrawler/controllers/tasks.py`)
* Add the new endpoint to the API (`gsicrawler-api.yaml`).
* If you are using environment variables (e.g. for an API key), add them to your `.env` file.

If you are also deploying this with CI/CD and/or Kubernetes:

* Add any new environment variables to the deployment file (`k8s/gsicrawler-deployment.yaml.tmpl`)
* Add the variables to your CI/CD environment (e.g. https://docs.gitlab.com/ee/ci/variables/)

## Troubleshooting

Elasticsearch may crash on startup and complain about vm.max_heap_count.
This will solve it temporarily, until the next boot:

```
sudo sysctl -w vm.max_map_count=262144 
```

If you want to make this permanent, set the value in your `/etc/sysctl.conf`.
