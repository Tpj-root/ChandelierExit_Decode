import json
import requests
import websocket


class DerivClient:

    BASE_URL = "https://api.derivws.com"

    def __init__(self, app_id, auth_token, account_id):
        self.app_id = app_id
        self.auth_token = auth_token
        self.account_id = account_id
        self.ws = None

    def get_socket_url(self):
        url = (
            f"{self.BASE_URL}"
            f"/trading/v1/options/accounts/{self.account_id}/otp"
        )

        headers = {
            "Deriv-App-ID": self.app_id,
            "Authorization": f"Bearer {self.auth_token}",
        }

        response = requests.post(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "error" in data:
            raise RuntimeError(
                f"Deriv API Error: {data['error']}"
            )

        socket_url = data["data"]["url"]

        return socket_url

    def connect(self):
        socket_url = self.get_socket_url()

        print("Socket URL received")
        print("Connecting to Deriv...")

        self.ws = websocket.create_connection(socket_url)

        print("Connected!")

    def subscribe_ticks(self, symbol):
        request = {
            "ticks": symbol,
            "subscribe": 1
        }

        self.ws.send(json.dumps(request))

        print(f"Subscribed: {symbol}")

    def receive_ticks(self):
        while True:

            message = self.ws.recv()
            data = json.loads(message)

            if data.get("msg_type") != "tick":
                continue

            tick = data["tick"]

            epoch = tick["epoch"]
            quote = tick["quote"]

            print(f"{epoch}  {quote}")

    def close(self):
        if self.ws:
            self.ws.close()
            self.ws = None
            print("Disconnected")


def main():

    APP_ID = "APP_ID"
    AUTH_TOKEN = "AUTH_TOKEN"
    ACCOUNT_ID = "ACCOUNT_ID"


    client = DerivClient(
        app_id=APP_ID,
        auth_token=AUTH_TOKEN,
        account_id=ACCOUNT_ID
    )

    try:
        client.connect()

        client.subscribe_ticks("R_10")

        client.receive_ticks()

    except KeyboardInterrupt:
        print("\nStopped")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()