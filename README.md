# Easy Reading
#### A website for reading lovers to easily discover novels and use convenient bookshelf features.
####  🌐 Website Link: https://novel.likedream.life/novels/home
####  📖 Demo Account: test / Password: 0101test


## Table of Content
- [Technologies](#Technologies)
- [Architecture](#Architecture)
- [Database Schema](#Database-Schema)
- [Main Features](#Main-Features)
- [Author](#Author)

## Technologies
### Back-End
- Python
- RESTful API
- Linux
- NGINX
- Crontab
- Django

### Front-End
- HTML
- CSS
- JavaScript
- Bootstrap

### Cloud Service 
#### AWS
- Elastic Compute Cloud (EC2)
- Relational Database Service (RDS)
- Load Balancer (LB)
- Auto Scaling Group (ASG)
#### GCP
- Google Compute Engine 


### Database
- MySQL
- Elasticsearch


### Networking
- HTTP
- HTTPS / SSL
- Domain Name System (DNS)

### Others
- Version Control: Git, GitHub
- Agile: Trello (Srum)


## Architecture
![](https://github.com/vul358/assets/blob/main/structure.png)

## Main Features
### Novels Search & Recommendation
- Classic search function:
    - Search novel title will return the most similar 3 results.(Optional)
    - Search novel author will return all the match results.(Optional)
    - Recommend novels based on category chosen(default Romance) and tag chosen(Optional),
      return the most popular 3 compliant results.
  ![](https://github.com/vul358/assets/blob/main/classic_search.gif)

- Recommend based on keywords input by user
  ![](https://github.com/vul358/assets/blob/main/keyword_search.gif)
- Star &. Ban button to add novels into bookshelf
  ![](https://github.com/vul358/assets/blob/main/star_and_ban.gif)
- Custom recommendation based on the user’s settings and whether the novel exists in the bookshelf or not
  ![](https://github.com/vul358/assets/blob/main/custom_recommend.gif)

