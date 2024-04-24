import boto3
import json
import pandas as pd
import streamlit as st
import uuid
import io
import plotly.express as px
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie

# Initialize AWS services
s3 = boto3.client('s3', 
                  region_name='us-east-1',
                  aws_access_key_id='AKIAZI2LHWVWTXGWO7OS',
                  aws_secret_access_key='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')
dynamodb = boto3.resource('dynamodb', 
                          region_name='us-east-1',
                          aws_access_key_id='AKIAZI2LHWVWTXGWO7OS',
                          aws_secret_access_key='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')
comprehend = boto3.client('comprehend', 
                          region_name='us-east-1',
                          aws_access_key_id='AKIAZI2LHWVWTXGWO7OS',
                          aws_secret_access_key='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')
lambda_client = boto3.client('lambda', 
                             region_name='us-east-1',
                             aws_access_key_id='AKIAZI2LHWVWTXGWO7OS',
                             aws_secret_access_key='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')
sns = boto3.client('sns',
                   region_name='us-east-1',
                   aws_access_key_id='AKIAZI2LHWVWTXGWO7OS',
                   aws_secret_access_key='x4z3KO67yVn+EHgTuJgz/WYmSVmoM8PbO67t88en'
                   )


# Lambda function name
lambda_function_name ='sentiment_Lambda'  # Replace with your Lambda function name


def process():
    # Function to upload data to S3 bucket
    @st.cache_data(ttl=(60*60))
    def upload_to_s3(file):
        try:
            bucket_name = 'sentimentdataset'
            file_name = 'dataset.csv'
            s3.upload_fileobj(file, bucket_name, file_name)
            st.success("dataset successfully uploaded to S3 bucket")
            return True
        except Exception as e:
            st.error(f"Error uploading file to S3: {e}")
            return False

    # Function to download data from S3 bucket
    @st.cache_data(ttl=(60*60))
    def download_from_s3(file_name):
        try:
            bucket_name = 'sentimentdataset'
            obj = s3.get_object(Bucket=bucket_name, Key=file_name)
            return pd.read_csv(io.BytesIO(obj['Body'].read()))
        except Exception as e:
            st.error(f"Error downloading file from S3: {e}")
            return None

    # Function to invoke Lambda function for sentiment analysis
    def invoke_lambda(df):
        try:
            df_json = df.to_json(orient='records')
            response = lambda_client.invoke(
                FunctionName='sentiment_Lambda',
                InvocationType='RequestResponse',
                Payload=json.dumps({"data": df_json})
            )
            return response['StatusCode'] == 200
        except Exception as e:
            st.error(f'An error occurred while invoking Lambda function: {str(e)}')
            return False

    # Lambda function handler
    def lambda_handler(event):
        try:
            data = json.loads(event['Payload'])
            df = pd.read_json(json.dumps(data['data']))
            
            for index, row in df.iterrows():
                feedback = row['Feedback']
                response = comprehend.detect_sentiment(Text=feedback, LanguageCode='en')
                sentiment = response['Sentiment']
                df.at[index, 'Sentiment'] = sentiment

            table = dynamodb.Table('sentiment_table')
            for index, row in df.iterrows():
                s_no = str(uuid.uuid4())
                table.put_item(Item={
                    'S_NO': s_no,
                    "Name": row["Name"],
                    "Email": row["Email"],
                    "Phone": row["Phone"],
                    'Feedback': row['Feedback'],
                    "Ratings" : row["Ratings"],
                    'Sentiment': row['Sentiment']
                })

            return {
                'statusCode': 200,
                'body': 'Sentiment analysis completed and data stored in DynamoDB.',
                "Dataframe": df
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': f'An error occurred: {str(e)}'
            }

    # Main Streamlit app
    def main():
        container = st.container()
        try:
            with container:
                @st.cache_data(ttl=60 * 60)
                def load_lottie_file(filepath : str):
                    with open(filepath, "r") as f:
                        gif = json.load(f)
                    st_lottie(gif, speed=1, width=650, height=450)
                        
                load_lottie_file("ratings.json")
        except:
            print("Don't raise exception")
                
        st.title("Sentiment Analysis using AWS Comprehend and DynamoDB")

        file = st.file_uploader("Upload file (CSV format)", type=["csv"])
        if file is not None:
            if upload_to_s3(file):
                df = download_from_s3('dataset.csv')
                if df is not None:
                    st.dataframe(df.head())
                    if 'Feedback' in df.columns:
                        if invoke_lambda(df):
                            st.success("Data processed through Lambda successfully.")
                            st.info("Fetching data from DynamoDB...")

                            response = lambda_handler({'Payload': json.dumps({"data": df.to_dict()})})
                            if response['statusCode'] == 200:
                                st.success(response['body'])
                                df = response["Dataframe"]
                                st.info("After performing sentiment analysis output Dataframe")
                                st.dataframe(df.head())

                                ratings = df['Sentiment'].value_counts().reset_index()
                                ratings.columns = ['Sentiment', 'Count']
                                fig = px.bar(ratings, x='Sentiment', y='Count', title='Sentiment Analysis', color='Sentiment')
                                st.plotly_chart(fig)

                                avg_rating = df['Ratings'].mean()
                                st.info(f"Average Rating: {avg_rating:.2f} out of 5")
                            else:
                                st.error(response['body'])
                        else:
                            st.error("Failed to process data and store it in DynamoDB.")
                    else:
                        st.error("The uploaded file must contain a 'Feedback' column.")
                else:
                    st.error("Failed to download data from S3.")
            else:
                st.error("Failed to upload file to S3.")
        else:
            st.warning("Please upload a CSV file.")

    if __name__ == "__main__":
        main()
def report():
    container = st.container()
    try:
        with container:
            @st.cache_data(ttl=60 * 60)
            def load_lottie_file(filepath : str):
                with open(filepath, "r") as f:
                    gif = json.load(f)
                st_lottie(gif, speed=1, width=650, height=450)
                    
            load_lottie_file("report.json")
    except:
        print("Don't raise exception")
        
    st.title("sending report through email using SNS service")
    email = st.text_input("Enter Email Address")
    with open('average.txt') as file:
        avg = file.read().strip("[]")
    def send_report_email(email):

        report_data = f"Average Customer Feedback Rating: {avg} out of 5"
        try:
        
            # Get the report data from DynamoDB
            # Here, you can modify this part to fetch the data you want to include in the report

            # Publish the report data to SNS topic
            topic_arn = 'arn:aws:sns:us-east-1:637423564141:customerFeedback'
            sns.publish(
                TopicArn=topic_arn,
                Message=report_data,
                Subject='Sentiment Analysis Report',
                MessageAttributes={
                    'email': {
                        'DataType': 'String',
                        'StringValue': email
                    }
                }
            )

            st.success("Report sent through email successfully.")

        except Exception as e:
            st.error(f"Error sending report through email: {e}")

    # Button to send report through email
    if st.button("Send Report through Email"):
        send_report_email(email)
    
menu_options = {"Execution 🚀":"Execution",
                "Report 📊": "Report"
}
# Create the menu bar
with st.sidebar:
    selected = option_menu("", list(menu_options.keys()))

# Display the selected page
page_functions = {
    "Execution": process,
    "Report": report
}
page_functions[menu_options[selected]]()
    





