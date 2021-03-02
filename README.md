# serverless_todo
todo application by serverless

---
# 検証方法

## 検証済み環境
- Python 3.8.3
- cdk 1.88.0

## 必要なmoduleのインストール
仮想環境を有効化して、必要なモジュールをインストール
```bash
$ cd {path/to/project_root}
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```
## cdk deploy
対象のアカウントにデプロイ
```bash
$ cdk deploy --profile {profile_name}
```

## userの作成
0. Userの作成にはAWS CLIを使用する

1. user pool id, client_idを確認してメモする
    ```bash
    $ aws cognito-idp list-user-pools --max-results 10 --profile {profile_name}
    $ aws cognito-idp list-user-pool-clients --user-pool-id {user_pool_id} --profile {profile_name}
    ```
2. ユーザーを作成する
    ```bash
    $ aws cognito-idp admin-create-user \
    --user-pool-id {user_pool_id} \
    --username {username} \
    --user-attributes Name=email,Value={email} Name=email_verified,Value=true \
    --profile {profile_name}
    ```

3. 初回ログイン
    ```bash
    $ aws cognito-idp admin-initiate-auth \
    --user-pool-id {user_pool_id} \
    --client-id {client_id} \
    --auth-flow ADMIN_NO_SRP_AUTH \
    --auth-parameters \
    USERNAME={username},PASSWORD={onetime_password} \
    --profile {profile_name}
    ```
4. 必須項目の入力 ※ {session}の部分は3.の返り値のセッションを使用する
    ```bash
    $ aws cognito-idp admin-respond-to-auth-challenge \
    --user-pool-id {user_pool_id} \
    --client-id {client_id} \
    --challenge-name NEW_PASSWORD_REQUIRED \
    --challenge-response NEW_PASSWORD={password},USERNAME={username},userAttributes.given_name=ユーザー,userAttributes.family_name=テスト,userAttributes.email={email} \
    --session {session} \
    --profile {profile_name}
    ```

5. ログイン
  ログインはusernameでもemailでも可能
    - ユーザーネームでログイン
      ```bash
      $ aws cognito-idp admin-initiate-auth \
      --user-pool-id {user_pool_id} \
      --client-id {client_id} \
      --auth-flow ADMIN_NO_SRP_AUTH \
      --auth-parameters USERNAME={username},PASSWORD={password} \
      --profile {profile_name}
      ```
    - emailでログイン
      ```bash
      $ aws cognito-idp admin-initiate-auth \
      --user-pool-id {user_pool_id} \
      --client-id {client_id} \
      --auth-flow ADMIN_NO_SRP_AUTH \
      --auth-parameters USERNAME={email},PASSWORD={password} \
      --profile {profile_name}
      ```