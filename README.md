<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://github.com/Alhajras/webscraper/assets/36598060/fc2a1efe-132b-4619-a16b-6e623a0332fd" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Scriburg Search Engine</h3>

  <p align="center">
    Master thesis project at the University of Freiburg
    <br />
    <a href="https://github.com/Alhajras/webscraper/blob/main/Report/ThesisTemplate/thesis_main.pdf"><strong>Read thesis »</strong></a>
    <br />
    <br />
<a class="mailto" href="mailto:alhajras.algdairy@gmail.com">Report Bug</a>
    ·
<a class="mailto" href="mailto:alhajras.algdairy@gmail.com">Request Feature</a>    
  </p>
</div>


# Contents

- [About The Project](#about-the-project)
  - [Built With](#built-With)
  - [Screenshots](#screenshots) 
- [Getting Started](#getting-started) 
  - [Installation](#installation)
- [Usage](#usage) 
  - [Uni Ranking](#Use-Case---1-World-University-Rankings-2023)
  - [Comparing Prices](#Use-Case---2-Comparing-Products-Prices)
- [Contact](#contact)


<!-- ABOUT THE PROJECT -->
## About The Project

If you are looking for a free scalable tool to collect and index information from a specific set of domains on the Internet, **Scriburg** is the right tool for you.

Examples of valid use cases:
* Compare prices and find the cheapest product in the market
* Track job positions with a keyword
* Find an affordable apartment to rent
* Follow news
* Monitor social media content

### Screenshots

| Crawlers Dashboard | Crawler Configuration |
| --------  | ------------------- |
| ![showcase scene](https://raw.githubusercontent.com/Alhajras/webscraper/main/Report/Scriburg%20Master%20thesis/figures/demo-6.png) | ![showcase scene 3](https://raw.githubusercontent.com/Alhajras/webscraper/main/Report/Scriburg%20Master%20thesis/figures/demo-7.png) |

| Indexers Dashboard | Search Result |
| --------  | ------------------- |
| ![showcase scene](https://raw.githubusercontent.com/Alhajras/webscraper/main/Report/Scriburg%20Master%20thesis/figures/demo-10.png) | ![showcase scene 3](https://raw.githubusercontent.com/Alhajras/webscraper/main/Report/Scriburg%20Master%20thesis/figures/demo-12.png) |

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

[![Django][Django.com]][Django-url] [![Angular][Angular.io]][Angular-url] [![Docker][Docker.com]][Docker-url] [![Postgres][Postgres.com]][Postgres-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To simplify the installations process, `docker compose` is used and recommended. 

### Installation

Installing `docker compose` (Recommended)
The docker compose version supported is: `v2.16.0`
run `docker compose version` to print your local version. 

If you do not have docker compose you can install it from here [Docker compose](https://docs.docker.com/compose/install/)
- Building all images:
    ```
    docker compose build
    ```

- Run containers:
    ```
    docker compose up -d
    ```
- If you want to only run the pbs cluster run:
    ```
    docker compose up -d pbs-head-node pbs-sim-node
    ```
- To register the simulation node in the head node, first you have to invlike the head container and run the following: 
    ```
    . /etc/profile.d/pbs.sh
    qmgr -c "create node pbs-sim-node"
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

 
## Usage 

### Use Case - 1: World University Rankings 2023
You are a university professor and would like to maintain a local version list of the universities worldwide and their ranking. To do this, we will use the website [timeshighereducation](www.timeshighereducation.com) to download and index the information. **The Times Higher Education World University Rankings 2023** include 1,799 universities across 104 countries and regions, making them the largest and most diverse university rankings to date.

<details>
<summary>Read more ...</summary>

This is a screenshot on how the table we want to extract information from looks like:

![image](https://github.com/Alhajras/webscraper/assets/36598060/47decc10-d491-4ff8-b1dc-4ec156f30d18)

**Goal:** We would like to extract the following Fields: **University ranking, University name** and **University location** 

To do so, we will follow the next steps: 

------------------------

## 1 - Templates

![image](https://github.com/Alhajras/webscraper/assets/36598060/ce1b5e88-b483-4232-a020-8c8fd5bcff6c)
 
We start by creating a _**Template**_, which is the blueprint that maps to the fields that want to be downloaded as a document. 

### Steps:

- Go to the [Templates](http://localhost:4200/templates) page
-  Click on `Create a template` button
-  Give a name of the template `uni-ranking-template` and click on `save`.
-  Expand the template you created by clicking on the `>` button.
-  Now we want to create the fields we want to capture from the page: `uni-name`, `uni-location` and `uni-ranking`. 
-  Click on `Create an inspector` button and create the following inspectors:

```
Name: uni-name
Selector: //*[contains(@class, 'ranking-institution-title')]
Type: text

Name: uni-location
Selector: //*[contains(concat(' ', normalize-space(@class), ' '), ' location ')]	
Type: text

Name: uni-ranking
Selector: //*[contains(@class, 'rank') and contains(@class, 'sorting_1') and contains(@class, 'sorting_2')]
Type: text
```

This is how your inspector's list should look like:

![image](https://github.com/Alhajras/webscraper/assets/36598060/6609c955-dd8e-435e-9f10-f29888384045)


------------------------

## 2 -  Crawlers

After creating a _Template_, we want to create and configure a _Crawler_.

### Steps:

- Navigate to the Crawlers page
- Click on `Create a crawler` and expand `Advanced options`
- Fill the next values:
```
Name: {yourname}-uni-crawler
Template: {your-name}-uni-ranking 
Max pages: 10000
Max collected docs: 300000
Seed URL: https://www.timeshighereducation.com/world-university-rankings/2023/world-ranking
Allow multi elements crawling: Enable
Links Scope (Pagination): //*[contains(@class, 'pagination')]
Threads: 4
Max depth: 10000
```
This is how it should look like:

![image](https://github.com/Alhajras/webscraper/assets/36598060/45c8f3e0-b5a0-4860-bf73-024c56367cdf)

- Click on `Create` button

------------------------

## 3 - Runners

Runners are jobs that run the crawling process in a cluster or locally. After creating the _Crawler_, we create a _Runner_.
Now, we can run/stop the crawlers from the Runners page.

### Steps:

- Navigate to the Runners page:
- Click on `Create a Runner`
- Fill the following:

```
Name: {yourname}-uni-runner
Crawler: {yourname}-uni-crawler
Machine: localhost

```
- Click on Create

Find your runner in the list. Click on the burger menu to start crawling and click on `Start`.

![image](https://github.com/Alhajras/webscraper/assets/36598060/df26e6f5-3b3c-45de-988d-f0fb83ee76ad)

The list will keep refreshing. You don't have to keep reloading the page.
You can monitor the progress by looking at the `progress` column and `status` column.

You can see the log and statistics by clicking on: 
![image](https://github.com/Alhajras/webscraper/assets/36598060/ee956f61-817a-46f5-ab09-07e50eff5e26)


------------------------

## 4 - Indexing

After the runner is completed, we can start indexing the results.

### Steps:

- Navigate to Indexers
- Click on `create an indexer`
- Fill the following:
```
name: {yourname}-uni-indexer
Inspectors:  {yourname}-uni-crawler (Uni name {yourname})
``` 
- Click on Create.
- Find your indexer from the list and click on `Start indexing`.
- Watch the indexing going from status `New` to `Completed`
------------------------

## 5 - Searching

After crawling (Collecting data) and Indexing (Preparing them for searching), we can test if searching returns the right results.

### Steps:

- Navigate to Search
- Select your indexer
- Search for:
  - `university` (Covering a normal query case)
  -  `what is freiburg` (Covering a case where only one word should be more important than others)
  - `show me hamburg unis` (Long query)
  - `berlin` (Covering a normal query case)
  - `Humboldt Berlin` (Covering a normal query case)
  - `Electronic` (Covering a normal query case)
  - `college` (Covering a normal query case)
- Testing the suggestions list:
  - Enter `Universi`, Should correctly suggest `university`
  - Enter `univsrity`, Misspelling should be forgiven, and the result should be `university`
  - Enter  `university oxford`, should show results including `university of oxford` 
</details>

### Use Case - 2: Comparing Products Prices
You are a small business owner who would like to monitor and track the competitors. You can create more than one crawler to monitor different websites and for this use case, we will focus on Douglas.

<details>
<summary>Read more ...</summary>

This is a screenshot on how the products we want to extract information from looks like:

![image](https://github.com/Alhajras/webscraper/assets/36598060/489d206a-e444-40dc-a007-280fd938c03d)

**Goal:** We would like to extract the following Fields: **Brand, Image, name** and **Price** 

To do so, we will follow the next steps: 

------------------------

## 1 - Templates

![image](https://github.com/Alhajras/webscraper/assets/36598060/ce1b5e88-b483-4232-a020-8c8fd5bcff6c)
 
We start by creating a _Template_, which is the blueprint that maps to the fields that want to be downloaded as a document. 

### Steps:

- Go to the Templates page
-  Click on `Create a template` button
-  Give a name of the template `{your-name}-douglas` and click on save.
-  Expand the template you created.
-  Now we want to create the fields we want to capture from the page: `Product brand`, `Product image`, `Product name` and `Product price`. 
-  Click on `Create an inspector` button and create the following inspectors:

```
Name: product-name-{yourname}
Selector: //*[contains(@class, 'text')][contains(@class, 'name')]
Type: text

Name: product-brand-{yourname}
Selector: //*[contains(@class, 'top-brand')]	
Type: text

Name: product-image-{yourname}
Selector: //a[contains(@class, 'product-tile__main-link')]/div[1]/div/img
Type: image

Name: product-price-{yourname}
Selector: //div[contains(concat(' ', normalize-space(@class), ' '), ' price-row ')]
Type: text
```

This is how your inspector's list should look like with different names:

![image](https://github.com/Alhajras/webscraper/assets/36598060/1be60cba-5e65-40e5-a363-8cadc3a6d512)

------------------------

## 2 -  Crawlers

After creating a _Template_, we want to create and configure a _Crawler_.

### Steps:

- Navigate to the Crawlers page
- Click on `Create a crawler` and expand `Advanced options`
- Fill the next values:
```
Name: {yourname}-douglas
Template: {your-name}-douglas 
Max pages: 20000
Max collected docs: 200000
Seed URL: https://www.douglas.de/de/c/parfum/damenduefte/duftsets/010111
Allow multi elements crawling: Enable
Links Scope (Pagination): This is a list field, meaning after each entry press enter button
- //*[contains(@class, 'pagination')] 
- //*[contains(@class, 'left-content-slot')]  
- //*[contains(@class, 'navigation-main__container')] 
- //*[contains(@class, 'header')]
Threads: 4
Max depth: 100
```
This is how it should look like:

![image](https://github.com/Alhajras/webscraper/assets/36598060/1c6aeaf6-704b-4dc2-8999-31ac8b4ab718)

- Click on `Create` button

------------------------

## 3 - Runners

Runners are jobs that run the crawling process in a cluster or locally. After creating the _Crawler_, we create a _Runner_.
Now, we can run/stop the crawlers from the Runners page.

### Steps:

- Navigate to the Runners page:
- Click on `Create a Runner`
- Fill the following:

```
Name: {yourname}-douglas
Crawler: {yourname}-douglas
Machine: localhost

```
- Click on Create

Find your runner in the list. Click on the burger menu to start crawling and click on `Start`.

![image](https://github.com/Alhajras/webscraper/assets/36598060/df26e6f5-3b3c-45de-988d-f0fb83ee76ad)

The list will keep refreshing. You don't have to keep reloading the page.
You can monitor the progress by looking at the `progress` column and `status` column.

You can see the log and statistics by clicking on: 
![image](https://github.com/Alhajras/webscraper/assets/36598060/ee956f61-817a-46f5-ab09-07e50eff5e26)


------------------------

## 4 - Indexing

After the runner is completed, we can start indexing the results.

### Steps:

- Navigate to Indexers
- Click on `create an indexer`
- Fill the following:
```
name: {yourname}-douglas
Inspectors:  product-name-{yourname} ({your-name}-douglas)
``` 
- Click on Create.
- Find your indexer from the list and click on `Start indexing`.
- Watch the indexing going from status `New` to `Completed`
------------------------

## 5 - Searching

After crawling (Collecting data) and Indexing (Preparing them for searching), we can test if searching returns the right results.

### Steps:

- Navigate to Search
- Select your indexer
- Search for:
  - `set` (Covering short query)
  -  `water` (Covering short query)
  - `Micellar Water` (Covering exact product name)
  - `black` (Covering normal query)
  - `black in` (Covering a case were the tokens are in the wrong order)
  - `set spring dadadadadad` (Covering a random word)
- Testing the suggestions list:
  - Enter `Universi`, Should correctly suggest `university`
  - Enter `univsrity`, Misspelling should be forgiven, and the result should be `university`
  - Enter  `university oxford`, should show results including `university of oxford` 
</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

------------------------

<!-- CONTACT -->
## Contact

Alhajras Algdairy - [Linkedin](https://www.linkedin.com/in/alhajras-algdairy/) - alhajras.algdairy@gmail.com

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/Alhajras/webscraper/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/Alhajras/webscraper/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/Alhajras/webscraper/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/Alhajras/webscraper/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/Alhajras/webscraper/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
[Django.com]: https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white
[Django-url]: http://www.djangoproject.com 
[Docker.com]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com
[Postgres.com]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white
[Postgres-url]: https://www.postgresql.org/
