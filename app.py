import boto3
import botocore.config
import json
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
        
        response = bedrock.invoke_model(
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
    

def save_blog_to_s3(s3_key,s3_bucket,generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=generate_blog
        )
        print(f"Blog saved to S3 bucket {s3_bucket} with key {s3_key}")
    
    except Exception as e:
        print(f"Error saving blog to S3: {e}")

    
def lambda_handler(event, context):

    event=json.loads(event['body'])
    blogtopic = event['blog_topic']

    generate_blog = blog_generate_using_bedrock(blogtopic=blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_key=f"blog_output/{current_time}.txt"
        s3_bucket="aws-bedrock-blog-generator"
        save_blog_to_s3(s3_key=s3_key, s3_bucket=s3_bucket, generate_blog=generate_blog)
    
    else:
        print("Blog generation failed.")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Blog generation completed successfully.',
            'blog_topic': blogtopic,
            's3_key': s3_key
        })
    }

