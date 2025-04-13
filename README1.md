
1.	Application functionality is verified locally using docker images


docker run -d -p 8080:81 129952717198.dkr.ecr.us-east-1.amazonaws.com/flask-app:latest
        
curl http://localhost:8080

2.	Application image is created automatically and pushed to Amazon ECR using GitHub Actions Work perfectly fine. 

test git: 

git add README1.md

git commit -m "Test GitHub Actions"

git push origin main

3.	Application is deployed into empty namespace “final” in Amazon EKS.

kubectl get all -n final

kubectl get pvc -n final

4.	Application is loading the background image from a private Amazon S3

aws s3api get-bucket-acl --bucket eni-bucket-background

kubectl get configmap flask-config -n final -o yaml

kubectl get svc -n final

5.	Data is persisted when the pod is deleted and re-created by the replicaset, Amazon EBS volume and K8s PV (PersistentVolume) are created dynamically when application pod is created

kubectl get pvc -n final

kubectl get pods -n final -l app=mysql

kubectl exec -it <mysql-pod-name> -n final -- bash

mysql -u root -p$DB_PASSWORD

password: mypassword

SHOW DATABASES;

Exit


Delete te pod:

kubectl get pods -n final -l app=mysql

kubectl delete pod <mysql-pod-name> -n final

check for pod recreation: 

kubectl get pods -n final -l app=mysql -w

kubectl exec -it <mysql-pod-name> -n final -- bash

mysql -u root -p$DB_PASSWORD

password: mypassword

SHOW DATABASES;

Exit

6.	Internet users can access the application

kubectl get svc -n final

7. Change the background image URL in the ConfigMap. Make sure a new image is visible in the browser.


Update the ConfigMap with the New Image Path / upload the image.

kubectl apply -f flask-config.yaml

kubectl rollout restart deployment flask-app -n final

