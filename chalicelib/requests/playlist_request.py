from chalice import Blueprint
import boto3

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb')