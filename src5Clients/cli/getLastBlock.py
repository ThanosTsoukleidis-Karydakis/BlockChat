import click
import requests
import json


@click.command()
def trigger_transaction():
    """
    Trigger a GET request to the /getLastBlock endpoint.
    Retrieve the last validated block of the blockchain and its validator.
    Usage : view
    """
    url = "http://localhost:5000/getLastBlock"  # Replace with the actual address of your Flask app if needed

    response = requests.get(url)

    if response.status_code == 200:
        click.echo("Transaction was submited successfully!")
        print('The last validated block:\n ',json.loads(response.text)['lastBlock'])
        print('\nThe validator of the last validated block: ',json.loads(response.text)['validator'])
    else:
        click.echo(f"Error triggering transaction: {response.text}")

if __name__ == "__main__":
    trigger_transaction()