# Full-circle AI demo

This is a demo for operationalizing AI and Calculators in MarkLogic Data Hub.
Advantages:
- The data scientist is able to get curated, harmonized, trusted and secure data for training purposed
- The models are easily operationalized in the transactional, scalable, secure and business critical MarkLogic Data Hub

## Prerequisites

- Docker environment
- Have valid docker credentials in `$DOCKERUSER` and `$DOCKERPW`
- Java 8
- Commands are based on OSX/Linux shell

## Run MarkLogic Docker

On the host machine:

```sh
docker login -u $DOCKERUSER -p $DOCKERPW
mkdir -p /Users/shared/aidata
docker run -d -it -p 8000-8020:8000-8020 \
     -v /Users/shared/aidata:/var/opt/MarkLogic \
     -e MARKLOGIC_INIT=true \
     -e MARKLOGIC_ADMIN_USERNAME=admin \
     -e MARKLOGIC_ADMIN_PASSWORD=admin \
     --name aidata store/marklogicdb/marklogic-server:10.0-1-dev-centos
```

## Run CNTK and Jupyter Docker

Run the container while linking to MarkLogic and setting the current directory as a mount

```sh
docker pull microsoft/cntk:2.3-cpu-python3.5
docker run -d -p 8888:8888 \
     --name cntk-jupyter-notebooks \
     --link aidata -v `pwd`:/mount \
     -t microsoft/cntk:2.3-cpu-python3.5
```
#### Alternative using Anaconda Enterprise Data Science Platform

Alternatively, you could use a Anaconda (https://www.anaconda.com/) distribution to run Jupyter Notebook from.
In that case, skip this one step.

## Starting the data hub framework

On the host machine (use Java 8), leave this command running in its own shell.

```sh
java -jar marklogic-datahub-5.0.2.war
```

### Ingest CBS data

Open the Quickstart (at http://0.0.0.0:8080). Run the `cbs_index` flow.
Now we have trusted, curated, harmonized data for further use.

## Train the model
### Run Jupyter as Data Scientist environment

```sh
docker exec -it cntk-jupyter-notebooks bash -c "source /cntk/activate-cntk && jupyter-notebook --no-browser --port=8888 --ip=0.0.0.0 --notebook-dir=/mount --allow-root"
```
#### Alternative using Anaconda Enterprise Data Science Platform

Alternatively, you could use a Anaconda (https://www.anaconda.com/) distribution to run Jupyter Notebook from.
In that case, just run Jupyter Notebook in a shell using `jupyter notebook`.

### Use the Jupyter notebook for training purposes

Open the Jupyter notebook at http://0.0.0.0:8888/, or better yet follow the link (with the `?token=` parameter) in the output of the above `docker exec` command. Open the `Train_CBS_Linear_Regression_Model.ipynb` notebook and run all steps in sequence.

This step retrieves the data from the Data Hub using SQL (enabling Data Scientists without knowledge of MarkLogic) and uses it to train the model. Then the model is loaded up into the Data Hub to be operationalized.

## Run the model in MarkLogic using Query Console

Open Query Console at http://0.0.0.0:8000/ and load the Workspace called `Workspace.xml`. Now run the tab `Run linear regression`.

### Because the model doesn't work (anti-climax) show another model
Download the model and vocabulary from https://developer.marklogic.com/products/marklogic-server/10.0, see caption "Machine Learning Models".

Run the tabs `Query test summarizer model` to load the model and vocabulary. Then run the tab `Summarize sample text` to show how the trained ONNX model is able to summarize a random text.

## Conclusion
This demo shows:
1. The ability to load trusted valuable data easily in a Data Scientist environment to create models
2. Teh ability to operationalize those models in the MarkLogic Data Hub using the Industry Defacto Standard ONNX as Interchangeable Format.

## Appendix: Some background information

### Convert SQL to Optic plan

This step is informational. The results are already part of the Jupyter notebook that will be run later. On the QConsole (http://0.0.0.0:8000/qconsole), run the following Javascript:

```js
const op = require('/MarkLogic/optic');
op.fromSQL("select * from cbs_index").export();
```

This should return a JSON object like the body of the POST below.

### Get the data from the Rows API

The results of the last command will be used in the body of a POST to the `/v1/rows` API on the FINAL database (http://localhost:8011/v1/rows), with header `Accept: 'text/csv'`, and valid DIGEST credentials.

POST Body:

```json
{
     "$optic": {
     "ns": "op", 
     "fn": "operators", 
     "args": [{
          "ns": "op", 
          "fn": "from-sql", 
          "args": [
               "select * from cbs_index", 
               null
               ]
          }]
     }
}
```

The above JSON is already saved URL-encoded within the Jupyter Notebook, `CBS_Linear_Regression_Model.ipynb`. It can be tested in Postman or with `curl`.

### Training a model that works on CNTK using Keras

As the previous model (CBS Linear Regression) didn't run in MarkLogic due to the lack of support of the LinearRegressor model in the embedded CNTK library/ONNX runtime, here's an example that tries to create a model using the low-level Keras modules.

Start `jupyter notebook` (within the Microsoft CNTK Docker Image) and run all steps in sequence in `Train_Gender_Classifier_Model.ipynb`.

This example was taken from the MarkLogic Blog Post by Anthony Roach: https://www.marklogic.com/blog/now-available-marklogic-embedded-machine-learning/.