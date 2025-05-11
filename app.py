import boto3
import botocore.config

def blog_generate_using_bedrock(blogtopic:str) -> str:
    
    prompt=f"""
    <s>[INST] Human:  write a 200 words blog about {blogtopic}
    Assistant:[/INST]
    """
    