#### Deploy

```
python3 /home/ec2-user/git/meteor2-account/build/build.py
```

#### SQL Permissions

```
GRANT SELECT, INSERT, UPDATE, DELETE ON `meteor2-account`.* TO 'meteor2-account'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON `meteor2-account`.* TO 'meteor2-account'@'172.17.3.%';
GRANT SELECT, INSERT, UPDATE, DELETE ON `meteor2-account`.* TO 'meteor2-account'@'172.17.4.%';
GRANT SELECT, INSERT, UPDATE, DELETE ON `meteor2-account`.* TO 'meteor2-account'@'172.17.5.%';
GRANT SELECT, INSERT, UPDATE, DELETE ON `meteor2-account`.* TO 'meteor2-account'@'172.17.6.%';
```

### AWS Policy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ecs:UpdateService",
                "iam:PassRole",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:CompleteLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:InitiateLayerUpload",
                "ecr:BatchCheckLayerAvailability",
                "ecr:PutImage"
            ],
            "Resource": [
                "arn:aws:ecs:eu-west-1:633757032102:service/meteor2-account",
                "arn:aws:ecr:eu-west-1:633757032102:repository/meteor2-account",
                "arn:aws:iam::633757032102:role/ecsTaskExecutionRole"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ecs:RegisterTaskDefinition",
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        }
    ]
}
```

### Enable docker build for multi platforms

```
# wget latest binary (https://github.com/docker/buildx/releases)
# rename binary to 'docker-buildx' and place it in '~/.docker/cli-plugins/docker-buildx'
chmod a+x ~/.docker/cli-plugins/docker-buildx
yum install qemu-user-static
reboot
```

### Remove docker cached build data

```
docker builder prune
```