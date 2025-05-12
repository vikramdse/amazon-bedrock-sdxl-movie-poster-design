import json
import boto3
import base64
import datetime

# Create client connection with Bedrock and s3 bucket
client_bedrock = boto3.client('bedrock-runtime')
client_s3 = boto3.client('s3')

def lambda_handler(event, context):
    # TODO implement
    # Store the input data (prompt) in a variable
    input_prompt = event['prompt']
    print(input_prompt)
    
    # Create a request syntax to access the Bedrock Service
    response_bedrock = client_bedrock.invoke_model(
        contentType='application/json',
        accept='application/json',
        modelId='stability.stable-diffusion-xl-v1',
        body=json.dumps({
            "text_prompts": [
                {"text": input_prompt}
            ],
            "cfg_scale": 10,
            "steps": 30,
            "seed": 0
        })
    )
    print(response_bedrock)
    # Convert Streaming Body to Byte using json load
    response_bedrock_byte = json.loads(response_bedrock['body'].read())
    print(response_bedrock_byte)

    # Retrive data with artifacts key
    response_bedrock_base64 = response_bedrock_byte['artifacts'][0]['base64']
    response_bedrock_final_image = base64.b64decode(response_bedrock_base64)
    print(response_bedrock_final_image)

    # Upload the file to s3 using put object method
    poster_name = 'poster-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.png'
    # IMPORTANT: Replace 'S3_BUCKET_NAME' with your own S3 bucket name before deploying
    response_s3 = client_s3.put_object(
        Bucket='S3_BUCKET_NAME',  # Replace with your actual bucket name
        Key=poster_name,
        Body=response_bedrock_final_image
    )

    # Geneate Pre-signed URL
    # IMPORTANT: Replace 'S3_BUCKET_NAME' with your own S3 bucket name before deploying
    presigned_url = client_s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': 'S3_BUCKET_NAME',  # Replace with your actual bucket name
            'Key': poster_name
        },
        ExpiresIn=3600
    )
    print("Presigned URL:")
    print(presigned_url)

    return {
        'statusCode': 200,
        'body': presigned_url
    }