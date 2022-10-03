# bot構築手順

## Github上にbot用のリポジトリを作成する

botアプリやサーバ構成のコードを保存し、後の手順でTerraform Cloudとの連携を容易に行うために、
[Github](https://github.com/) リポジトリを作成します。私は bot というシンプルな名前でこのリポジトリを作ってみました。
このリポジトリをforkして使用していただいても構いません。

## Google Cloud Platformに登録(Sign Up)する

botを永続的に動かすには、botプログラムを動作させる(デプロイする)サーバが必要です。
もちろん他のレンタルサーバや、AWS, Azureのようなクラウドサービスでも構わないのですが、ここではGoogle Cloud Platform (GCP) を使用します。
GCPは2022年10月現在、毎月上限額までずっと無料で使える無料枠があり、 e2-microという小さなサイズのインスタンスであればずっと無料で動かし続けることができます。
他のサービスにも無料枠はありますが、ずっと無料枠が維持されるのは現在GCPだけです。

https://www.google.com/cloud

からGoogle Cloud Platformに登録します。

### Google Cloud Platformにプロジェクトを作成する

インスタンスなどのサーバリソースを作るには、Google Cloud Platform内にまず「プロジェクト」を作る必要があります。
Google Cloud コンソール https://cloud.google.com › cloud-console を開いてサインインし、
新しいプロジェクトを作成します。 ここでは私はtrade-botという名前でプロジェクトを作成しました。


### Google Cloud SDKをインストールする

https://cloud.google.com/sdk/docs/install

### Google Cloudにログインしておく

gcloud auth application-default login

## Terraform Cloudに登録(Sign Up)する

サーバの構築などを自動的に管理してもらうために、Terraform Cloudを使用します。アカウント登録が必要です。
https://app.terraform.io/public/signup/account

アカウントを登録し、メールアドレスの確認などを完了させます。

### どうしてStreamlit Cloudをデプロイ先として使わないのか

https://discuss.streamlit.io/t/does-streamlit-has-a-maximum-run-time-for-functions/22452/3
Streamlitはダッシュボード機能のようなwebアプリを対象にしており、処理のタイムアウトも起きる。
そのため、ユーザから何のアクションが無くとも永続的にデータを取得し、トレードを行うようなbotの用途には向かないと判断しました。

### Terraformをインストールする

https://app.terraform.io/app/getting-started から Try an example configurationを選択し、
内容に従ってTerraformコマンドをインストールします。
https://app.terraform.io/app/getting-started/example

私の場合はmacを使っているので、下記2コマンドを使用してインストールしました。
```bash
$ brew tap hashicorp/tap
$ brew install hashicorp/tap/terraform

$ terraform --version
Terraform v1.3.1
on darwin_arm64
```

## Terraform Cloudを使用してインスタンスを生成する

### Terraform Cloud内にワークスペースを作成する



## サーバ内でボットを動かす
```bash
streamlit run /Users/dakimura/projects/src/github.com/dakimura/bot/bot.py
```