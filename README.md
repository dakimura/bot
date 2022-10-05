# Simple Bot environment

In order to operate an automated trading bot, it is necessary to prepare a mechanism that 
allows the bot to automatically run without the operator having to start and stop it manually.
This is a high hurdle for those who are not experts in infrastructure or networking. 
Even if they know complex machine-learning algorithms, they may find it difficult to put them into actual operation.

In this repository, We will explain how to build a simple environment for running a bot.
Even if you do not understand some network/infrastructure/cloud computing terms,
we aim for you to be able to start bot operation by following the steps.

Of course, we are aware that this is not enough to operate a full-fledged, production-scale service.
Databases, log collection, a mechanism to send alerts when the server is down, CD/CI, and so on would be necessary.
However, we hope this procedure will be helpful for those who are taking their first steps in automatic trading.

# Server environment created by this repository

![](img/system_arch.png)
https://docs.google.com/presentation/d/1SyGSNEX8N3V8m4CkujqgTyiVN-Eeu1zUN4UCOVIs5Ss/edit?usp=sharing

## Create a Github repository for the bot

To store the code for the bot and network/infra configuration,
a [Github](https://github.com/) repository is needed.
I created dakimura/bot repository.
You can start from forking the repo.
If you don't want to make the repository public, 
you can create an empty repository and copy-paste the contents of this repository.

## Sign up for Google Cloud Platform

To run the bot for 24/7, you need a server on which to run (deploy) the bot program.
Here we will use Google Cloud Platform (GCP). Of course, other rental servers or cloud services such as AWS and Azure are acceptable, 
but As of October 2022, GCP has a free tier that allows you to keep running a small(e2-micro) instance for free for as long as you want,
up to the maximum amount each month. Other services also offer free allowances, 
but AFAIK GCP is the only one that keeps the free allowance for a long time.

Sign up for Google Cloud Platform from [here](https://www.google.com/cloud)

### Create a project on Google Cloud Platform

To create a server resource such as an Google Compute Engine instance, 
you must first create a "project" on Google Cloud Platform.
Open the Google Cloud console https://cloud.google.com' > cloud-console,
sign in and Create a new project. I have created a project named `trade-bot`.

### install gcloud (Google Cloud SDK command line interface)

https://cloud.google.com/sdk/docs/install
Make sure the `gcloud` command is available from the terminal.

### Sign in Google Cloud and create a service account
A service account is a special type of Google account intended to represent 
a non-human user that needs to authenticate and be authorized to access data in Google APIs.

In the steps that follow, we will build our server on the Google Cloud Platform using a service called Terraform.
To automatically build a server using Terraform on your Google Cloud Platform account, 
 you need to pass the service account information to Terraform.

Let's use the `gcloud auth login` command to first make sure that the gcloud command is properly installed.
After logging in to your Google account, You have succeeded if the screen [You are now authenticated with the gcloud CLI!](https://cloud.google.com/sdk/auth_success) appears in your browser.

Let's create a service account by referring to https://cloud.google.com/iam/docs/creating-managing-service-accounts.

Confirm the GCP project you created and set the project. 
Please replace the project name(trade-bot-123456) below with your own,
```bash
 $ gcloud projects list
PROJECT_ID              NAME                  PROJECT_NUMBER
trade-bot-123456        trade-bot             123456789012

$ gcloud config set project trade-bot-123456
Updated property [core/project].
```

and create a service account.
```bash
$ gcloud iam service-accounts create trade-bot \
--description="ServiceAccount for my trading bot" \
--display-name="trade-bot"

Created service account [trade-bot].
```

Grant the `roles/owner` role (privilege) to the service account.
This is a very strong permission, so please be very careful when handling the service account.

```bash
gcloud projects add-iam-policy-binding trade-bot-123456 \
--member="serviceAccount:trade-bot@trade-bot-123456.iam.gserviceaccount.com" \
--role=roles/owner

Updated IAM policy for project [trade-bot-123456].
bindings:
- members:
  - serviceAccount:trade-bot@trade-bot-123456.iam.gserviceaccount.com
  - user:example@example.com
  role: roles/owner
etag: XXXXXXXXXXXX
version: 1
```

To pass the service account information, create a key and download it to your localhost.
https://cloud.google.com/iam/docs/creating-managing-service-account-keys#iam-service-account-keys-create-gcloud

(Please replace the local file path, service account name, and project ID to your own)
```bash
$ gcloud iam service-accounts keys create /Users/dakimura/Desktop/sa-trade-bot-private-key.json \
    --iam-account=trade-bot@trade-bot-123456.iam.gserviceaccount.com
    
created key [XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX] of type [json] as [/Users/dakimura/Desktop/sa-trade-bot-private-key.json] for [trade-bot@trade-bot-123456.iam.gserviceaccount.com]
```
DO NOT share the downloaded private key file with anyone.

Once again, because it's important.

DO NOT share the downloaded private key file with anyone.

Also, you cannot download the private key file again. If you accidentally lose the file or share the file with someone,
please immediately delete it by the following command:
```bash
gcloud iam service-accounts keys delete /Users/dakimura/Desktop/sa-trade-bot-private-key.json --iam-account=trade-bot@trade-bot-123456.iam.gserviceaccount.com
```

## Sign up for Terraform Cloud
To configure the bot server automatically, we use Terraform Cloud.
Please register an account with [Terraform Cloud](https://app.terraform.io/public/signup/account).
and confirm your e-mail address after the registration.

### Create a workspace in Terraform Cloud
Create a workspace by following the steps at: https://www.terraform.io/cloud-docs/workspaces/creating#create-a-workspace.
Set the service account you created as a variable in Terraform Cloud.

### Connect Terraform to your Github repository
//TODO:

### Register Service account key to Terraform Cloud
After creating a workspace, we register the downloaded GCP service account key to Terraform cloud.


![](img/reg_env_var_tf_cloud.png)
Environmental Variable does not accept new lines, so remove the value by the following command and copy-paste.
(If)
```bash
$ brew install jq
$ jq -c < /Users/dakimura/Desktop/sa-trade-bot-private-key.json
```
Please check on `Sensitive`, and save the variable.


## FAQ

### What are Terraform and Terraform cloud, and why are they necessary?

Terraform is an open-source infrastructure as code(IaaC) software tool that
enables you to safely and predictably create, change, and improve infrastructure.
Here we are going to create a server for the bot, but probably you don't want to care about:
- Does the server cost a lot?
- Is the server opening a proper port?
- Can I delete the server when I want to?

You don't have to worry because all those kind of settings are stored in the text files (.tf files) on this repository.
You can reproduce the infrastructure anytime without learning much about Google Cloud.

In short, Terraform will manage the state of your server and network settings.
To store the state, Terraform needs to be integrated with your Github repository and GCP account.
Terraform Cloud does it, and you don't have to care where the Terraform commands are run.

As of October 2022, Terraform Cloud is free to use for up to 5 users with unlimited number of workspaces. 
https://www.hashicorp.com/products/terraform/pricing

Of course, you can build a server and network infrastructure at GCP console(=Web UI), 
so Terraform is not a must if you know how to do it.

### Your python code uses Streamlit. Why don't you use Streamlit Cloud?

https://discuss.streamlit.io/t/does-streamlit-has-a-maximum-run-time-for-functions/22452/3
Streamlit is intended for web applications such as dashboard feature, and it has processing timeouts.
So we determined that it is not suitable for bot applications that persistently retrieve data and make trades without any action from the user.

### Install Terraform command line interface

Choose "Try an example configuration" at https://app.terraform.io/app/getting-started
and install Terraform command by following the instruction.
https://app.terraform.io/app/getting-started/example

I'm using mac, so installed it by the following 2 commands:
```bash
$ brew tap hashicorp/tap
$ brew install hashicorp/tap/terraform

$ terraform --version
Terraform v1.3.1
on darwin_arm64
```

## Create a server using Terraform Cloud



## run a bot on your server
```bash
streamlit run /Users/dakimura/projects/src/github.com/dakimura/bot/bot.py
```

Probably you want to run it as a daemon(=a kind of background process)
and use 443 port, so you would use the following command to start the bot:
```bash
```

### Don't we use Docker?
Actually, we should use Docker.
But it's time-consuming and difficult to register the docker image to Google Container Registry and 
configure the permission to pull the image from the GCE instance, so we think it as a nice-to-have but not must-have thing.

Also, because we are using a tiny([e2-micro](https://cloud.google.com/compute/vm-instance-pricing?hl=ja#e2_sharedcore_machine_types)) instance,
so we should not use much resource to the Docker daemon.

### Don't we register the bot as a systemctl service?
For simplicity, we didn't explain how to do it.
You can do so if you know how to do it.


### How can I SSH to the server?

You can SSH-login to the server by using the following command:
(Replace the project name and instance name with your own.)
```bash
gcloud compute --project "trade-bot-123456" ssh --zone "us-central1" "trade-bot"
```

