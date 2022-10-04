# bot用サーバの構築

自動トレードを行うbotを運用するには、運用者がいちいち起動や終了をしなくとも自動的にbotが動き続ける仕組みを用意する必要があります。
インフラやネットワークが専門でない方にとってはここが高いハードルとなり、複雑なアルゴリズムを学んでもそれを実運用に持っていくことが難しいと感じるケースがあると思います。

本リポジトリでは、10年サーバ開発・運用を行っている立場としてなるべくシンプルでおすすめのbot運用環境の構築方法を説明します。
いくつか専門用語がわからなくとも、手順に従って作業をすすめることで誰でもbot運用が開始できることを目指します。

データベース、ログ収集、サーバがダウンしたときにアラートを送る仕組み、CD/CI等、本格的なサービスを運用するにはこれだけでは足りないことは重々承知です。
しかし個人がbot運用の第一歩を踏み出すにあたって、こちらの手順が参考になれば幸いです。

# 本リポジトリで作るサーバ環境

![](img/system_arch.png)
https://docs.google.com/presentation/d/1SyGSNEX8N3V8m4CkujqgTyiVN-Eeu1zUN4UCOVIs5Ss/edit?usp=sharing

## Github上にbot用のリポジトリを作成する

botアプリやサーバ構成のコードを保存し、後の手順でTerraform Cloudとの連携を容易に行うために、
[Github](https://github.com/) リポジトリを作成します。私は bot というシンプルな名前でこのリポジトリを作ってみました。
このリポジトリをforkして使用していただいても構いません。
botのコードを公開したくない場合は、プライベートなリポジトリとして作成しても構いません。

## Google Cloud Platformに登録(Sign Up)する

botを永続的に動かすには、botプログラムを動作させる(デプロイする)サーバが必要です。
もちろん他のレンタルサーバや、AWS, Azureのようなクラウドサービスでも構わないのですが、ここではGoogle Cloud Platform (GCP) を使用します。
GCPは2022年10月現在、毎月上限額までずっと無料で使える無料枠があり、 e2-microという小さなサイズのインスタンスであればずっと無料で動かし続けることができます。
他のサービスにも無料枠はありますが、ずっと無料枠が維持されるのは現在GCPだけです。

https://www.google.com/cloud からGoogle Cloud Platformに登録します。

### Google Cloud Platformにプロジェクトを作成する

インスタンスなどのサーバリソースを作るには、Google Cloud Platform内にまず「プロジェクト」を作る必要があります。
Google Cloud コンソール https://cloud.google.com › cloud-console を開いてサインインし、
新しいプロジェクトを作成します。 ここでは私は `trade-bot` という名前でプロジェクトを作成しました。

### Google Cloud SDKをインストールする

https://cloud.google.com/sdk/docs/install
を参考に、`gcloud` コマンドがターミナルから使用できるようにしましょう。

### Google Cloudにログインし、サービスアカウントを作成する

あなたのGoogle Cloud Platformアカウント上にTerraformを使ってサーバを自動的に構築するには、
Terraformに認証情報を渡す必要があります。Google Cloud Platform上では、
権限を付与したサービスアカウントという情報を用いてそれを実現することができます。

`gcloud auth application-default login` コマンドを使って、まずgcloudコマンドが正しくインストールされているか確かめましょう。
Googleアカウントにログインした後、[Cloud SDK 認証の完了](https://cloud.google.com/sdk/auth_success) という画面がブラウザ上に表示されたら成功です。

https://blog.blackcoffy.net/posts/create-service-accounts-on-gcloud-iam を参考に、サービスアカウントを作成しましょう。

```bash
gcloud iam service-accounts create trade-bot \
--description="システムトレード用のServiceAccount" \
--display-name="trade-bot"
```

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

こちらの作業に関しては
https://www.niandc.co.jp/sol/tech/date20191002_1814.php
のページが参考になります。
サービスアカウントの作成とその環境変数への設定も必要になります。

## サーバ内でボットを動かす
```bash
streamlit run /Users/dakimura/projects/src/github.com/dakimura/bot/bot.py
```

デーモン(≒バックグラウンドで動き続ける)ようにしたいですし、最低限のログは見たい。
ポートは443番を使いたい…etcを考えると、 以下のようなコマンドを使うとよいでしょう。

### systemctlのサービスとして登録しないのですか？
分かる方はもちろん書いてもいいです。ここでは


```bash
```

### Dockerは使わないのですか？
もちろん使ってよいです！Google Container RegistryへのDockerイメージの登録やサーバインスタンス側でのDocker pull設定など
面倒な作業も増えるので、それはまた次のステップと考え、ここでは
小さなインスタンス([e2-micro](https://cloud.google.com/compute/vm-instance-pricing?hl=ja#e2_sharedcore_machine_types))を使用しているので
Dockerにリソースを取られるのももったいないという考えもあります。

### 作ったサーバにSSHしたいのですが

`gcloud compute --project "trade-bot" ssh --zone "us-central1" "trade-bot"`
こちらのコマンドでサーバにSSHできるはずです。
もちろん分かる方はSSH鍵ペアを作って `.ssh/authorized_keys` に公開鍵を登録してSSH用のポートを開放して...という手順をとっても構いません。

