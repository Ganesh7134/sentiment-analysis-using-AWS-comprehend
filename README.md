# sentiment-analysis-using-AWS-comprehend
This Streamlit application enables users to perform sentiment analysis on customer feedback data using AWS Comprehend and DynamoDB. Users can upload CSV files containing customer feedback, which are then processed using AWS Lambda and stored in DynamoDB. Additionally, users can send sentiment analysis reports via email using AWS SNS.

## Features
* Upload CSV files containing customer feedback data.
* Perform sentiment analysis on the uploaded data using AWS Comprehend.
* Store the analyzed data in DynamoDB for further analysis.
* Visualize sentiment analysis results using interactive charts.
* Send sentiment analysis reports via email using AWS SNS.

## Usage
* **Upload Data**: Click on the "Upload file (CSV format)" button to upload a CSV file containing customer feedback data.
* **Perform Sentiment Analysis**: Once the file is uploaded, the application will process the data using AWS Comprehend and display the sentiment analysis results in a tabular format and interactive charts.
* **Send Report via Email**: In the "Report 📊" section, enter the email address and click on the "Send Report through Email" button to send the sentiment analysis report via email using AWS SNS.

## Conclusion
The Sentiment Analysis Dashboard provides a convenient way to analyze customer feedback data and extract valuable insights. By leveraging AWS services such as Comprehend, DynamoDB, and SNS, the application offers scalability, reliability, and ease of use. Whether it's understanding customer sentiment, tracking trends over time, or generating actionable reports, this dashboard empowers users to make data-driven decisions and improve customer satisfaction.
