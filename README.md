# Manual tagging app

Allows manual tagging of photos by users to be used for training of image classification models.  

Link to app: http://tagging.eizee.xyz

**Table of Contetnts**
- [Description](#description)
- [Docker](#Docker)

### **Description:**

This application allows users to manually tag images to later be used for training image
classification models. More than 10,000 images downloaded from Flickr.com
are recorded on an **Amazon **S3**** instance. The images' metadata are stored on **Amazon RDS**. 
The app shows a user a randomly selected image. The user may choose the relevant tags 
(Is the image taken indoors/outdoors? Is it taken in day/nighttime? Are there people and/or pets in the image?)

The tags selected by the user will be recorded in a relational database using AWS RDS (PostgresSQL) service.

### **Docker:**

After creating the docker image from the Dockerfile, Run:

docker run -v [Path/to/.aws]:/root/.aws -p [host port]:8501 mannualtagging:latest  