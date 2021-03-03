# serverless_todo
todo application by serverless

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
6. APIリクエスト  
  ログインのレスポンスのidTokenをAPI HeaderのAuthorizationヘッダーに格納して、APIリクエストする
  コマンド例
  ```bash
  # 新規のタスクの作成
  $ curl -X POST -H "Authorization: {id_token}" \
  -d '{"title":"test from cli", "content":"test command", "is_done": "false", "priority": "high"}' \
  https://rmp14p63v5.execute-api.ap-northeast-1.amazonaws.com/prod/task/

  # タスクの取得
  $ curl -X GET -H "Authorization: {id_token}" \
  https://rmp14p63v5.execute-api.ap-northeast-1.amazonaws.com/prod/task/{task_id}

  # タスクの修正
  $ curl -X POST -H "Authorization: {id_token}" \
  -d '{"title":"test from cli modifiesd", "content":"test command modifiesd", "is_done": "true", "priority": "medium"}' \
  https://rmp14p63v5.execute-api.ap-northeast-1.amazonaws.com/prod/task/{task_id}

  # タスクの削除
  $ curl -X DELETE -H "Authorization: {id_token}" \
  -d '{"title":"test from cli modifiesd", "content":"test command modifiesd", "is_done": "true", "priority": "medium"}' \
  https://rmp14p63v5.execute-api.ap-northeast-1.amazonaws.com/prod/task/{task_id}
  ```


# ドキュメント関連

### APIドキュメント
/docs/swagger.yaml

### データストア設計
https://docs.google.com/spreadsheets/d/1-Y4x7S1cdg1fYqbsL68ZiJM_g_dyW8dhbIzOw4DS4lM/edit#gid=0

### テストケース設計
https://docs.google.com/spreadsheets/d/1-Y4x7S1cdg1fYqbsL68ZiJM_g_dyW8dhbIzOw4DS4lM/edit#gid=839085431
https://docs.google.com/spreadsheets/d/1-Y4x7S1cdg1fYqbsL68ZiJM_g_dyW8dhbIzOw4DS4lM/edit#gid=2004027084