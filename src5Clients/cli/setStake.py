import click
import requests
import json

@click.command()
@click.argument('amount')
def trigger_transaction(amount):
    """
    Trigger a POST request to the /makeTransaction endpoint.

    :param amount: The amount of coins to be used as the stake.

    Usage: stake <amount>
    """
    url = "http://localhost:5000/makeTransaction"  # Replace with the actual address of your Flask app if needed

    data = {"type": "stake", "content": int(amount), "id": -1, "noFee": True}

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        click.echo("Transaction was submited successfully!")
    else:
        click.echo(f"Error triggering transaction: {response.text}")

if __name__ == "__main__":
    trigger_transaction()