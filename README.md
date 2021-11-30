#### Deploy

```
python3 /home/ec2-user/git/meteor2-account/build/build.py
```

#### SQL Permissions

```
GRANT ALL PRIVILEGES ON `meteor2-accounts`.* TO 'meteor2-accounts'@'localhost';
GRANT ALL PRIVILEGES ON `meteor2-accounts`.* TO 'meteor2-accounts'@'172.17.0.%';
```