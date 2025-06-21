import boto3
import botocore.config
import json
import response
from datetime import datetime

def blog_generate_using_bedrock(blogtopic:str) -> str:
    
    prompt=f"""
    <s>[INST] Human:  write a 400 words blog about {blogtopic}
    Assistant:[/INST]
    """

    body={
        "prompt": prompt,
        "max_gen_len":512,
        "temperature": 0.7,
        "top_p": 0.9,
    }

    try:
        bedrock = boto3.client("bedrock-runtime",region_name="us-east-1", 
                               config=botocore.config.Config(read_timeout=300, retries={"max_attempts": 10}))
        
        bedrock.invoke_model(
            body=json.dumps(body),
            model_id="meta.llama3-2-1b-instruct-v1:0"
        )

        response_content = response.get('body').read()
        response_data=json.loads(response_content)

        print(response_data)
        blog_details = response_data['generation']
        return blog_details
    
    except Exception as e:
        print(f"Error generating blog: {e}")
        return "An error occurred while generating the blog. Please try again later."
    
def lambda_handler(event, context):

    event=json.loads(event['body'])
    blogtopic = event['blog_topic']

    generate_blog = blog_generate_using_bedrock(blogtopic=blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_key=f"blog_output/{current_time}.txt"
        s3_bucket="aws-bedrock-blog-generator"
    
    else:
        print("Blog generation failed.")

