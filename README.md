#### Deploy

```
docker load -i /home/ec2-user/git/meteor2-account/dist/meteor2-account.tar.gz
docker run --name meteor2-account -itd -p12351:80 meteor2-license
```