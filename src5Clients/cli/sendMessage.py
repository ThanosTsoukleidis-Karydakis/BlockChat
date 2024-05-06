import click
import requests
import json

@click.command()
@click.argument('rec_address')
@click.argument('message')
def trigger_transaction(rec_address, message):
    """
    Trigger a POST request to the /makeTransaction endpoint.

    :param rec_address: The recipient address.
    :param message: The message to be sent.

    Usage: t <rec_adress> <message>
    """
    url = "http://localhost:5000/makeTransaction"  # Replace with the actual address of your Flask app if needed

    data = {"type": "message", "content": (message), "id": int(rec_address), "noFee": False}

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        click.echo("Transaction was submited successfully!")
    else:
        click.echo(f"Error triggering transaction: {response.text}")

if __name__ == "__main__":
    trigger_transaction()