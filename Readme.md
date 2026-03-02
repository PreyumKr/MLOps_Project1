# Project 1 - Vehicle Insurance Domain

* We used a `template_generator` script to generate the skeleton of the project. 
* We will learn the use of `-e .` in `pip install` or `uv add -r req.txt --dev` know as editable mode, we need a setup.py file to install the local code as python package
* We can use `conda create -n vehicle python=3.10 -y`  and then `conda activate vehicle` to create venv with python 3.10 and use it, even if its not already there in the system which is not possible with uv. 
* We created a account in `MongoDB Atlas` Create a `Organization` and `Project`
* Then we want to `create a cluster` in the Project, there we currently chose a `free tier` and default options that comes with it.
* This Cluster will be our `cloud mongoDB` where we will create our `databases` and `collections`
* After cluster creation the UI will prompt to `create a database user`, we copied that credentials and adjusted it as needed
* Then from `Database and Network access` we `add ip address` of `our machine` or `0.0.0.0` i.e. allow access from anywhere. We can create database user from here as well.
* In the project page, scroll down and click on get connection string and get something like `mongodb+srv://preyumkr:<db_password>@cluster0.teb8wrs.mongodb.net/?appName=Cluster0` after selecting `python` and appropriate version matching
* Created own custom exception module while using `import traceback` and doing `tb = traceback.format_exc()` in exception part should be enough
* We looked at a `ML_DataScience` Notebook and will be going to replicate a `MLOps Pipeline` replicating that notebook
* Then we created a `constants init file` to enable the variables to be edited at a single point and be used everywhere in the code and any change needs change only in the single file.
* We have `__init__.py` in all folders so that we can use all of them as package modules
* To save env variables for testing in `powershell` use `$env:AWS_ACCESS_KEY_ID="value"`
* To verify we can do `echo $env:AWS_ACCESS_KEY_ID`
* Created docker image file for the project, `.dockerignore` excludes the files or directories mentioned in it from the docker build context. So, if we do `docker build` with a `.dockerignore` file there in the same directory the files mentioned in it will not be visible to the `docker build` command so even if there is a `copy .` command in the `dockerfile` the build command can't see the ignored files and those will not be copied.
* We created a `AWS ECR` repository for our `docker image`, Created a `AWS EC2` instance and installed docker in it and then used Github Actions for **`AWS EC2`** deployment
* In my case I had to use the `/train` route to create the `model.pkl` before being able to get the predictions.
* To restart the runner service in the instance again we need to go to the runner directory and then run `sudo ./svc.sh install` and then `sudo ./svc.sh start` 