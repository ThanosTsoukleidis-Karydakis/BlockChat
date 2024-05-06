import click
import requests
import json


@click.command()
def trigger_transaction():
    """
    Trigger a GET request to the /getBalance endpoint.
    Retrieve the balance of your node.
    Usage : balance
    """
    url = "http://localhost:5000/getBalance"  # Replace with the actual address of your Flask app if needed

    response = requests.get(url)

    if response.status_code == 200:
        click.echo("Transaction was submited successfully!")
        print('Your balance is: ',json.loads(response.text)["balance"])
    else:
        click.echo(f"Error triggering transaction: {response.text}")

if __name__ == "__main__":
    trigger_transaction()