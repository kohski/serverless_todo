# 1. user pool id, clientの確認
```
aws cognito-idp list-user-pools --max-results 10 --profile {profile_name}
aws cognito-idp list-user-pool-clients --user-pool-id {user_pool_id} --profile {profile_name}
```

# 2. ユーザーの作成
```bash
aws cognito-idp admin-create-user \
--user-pool-id {user_pool_id} \
--username {username} \
--user-attributes Name=email,Value={email} Name=email_verified,Value=true \
--profile {profile_name}
```

# 3.初回ログイン
```bash
aws cognito-idp admin-initiate-auth \
--user-pool-id {user_pool_id} \
--client-id {client_id} \
--auth-flow ADMIN_NO_SRP_AUTH \
--auth-parameters \
USERNAME={username},PASSWORD={onetime_password} \
--profile {profile_name}
```

# 4. 必須項目の入力
```bash
aws cognito-idp admin-respond-to-auth-challenge \
--user-pool-id {user_pool_id} \
--client-id {client_id} \
--challenge-name NEW_PASSWORD_REQUIRED \
--challenge-response NEW_PASSWORD={password},USERNAME={username},userAttributes.given_name=ユーザー,userAttributes.family_name=テスト,userAttributes.email={email} \
--session {session} \
--profile {profile_name}
```

# 5. ログイン
- ユーザーネームでログイン
```bash
aws cognito-idp admin-initiate-auth \
--user-pool-id {user_pool_id} \
--client-id {client_id} \
--auth-flow ADMIN_NO_SRP_AUTH \
--auth-parameters USERNAME={username},PASSWORD={password} \
--profile {profile_name}
```
- emailでログイン
```bash
aws cognito-idp admin-initiate-auth \
--user-pool-id {user_pool_id} \
--client-id {client_id} \
--auth-flow ADMIN_NO_SRP_AUTH \
--auth-parameters USERNAME={email},PASSWORD={password} \
--profile {profile_name}
```