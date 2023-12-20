import requests

class YooKassaIntegration:
    """
    YooKassaIntegraiton
    """
    def __init__(self, shop_id, secret_key):
        """
        initial

        :param self: self
        :param shop_id: shop id
        :param secret_key: secret key
        """
        self.base_url = "https://api.yookassa.ru/v3/"
        self.auth = (shop_id, secret_key)

    def create_payment(self, amount, currency="RUB", return_url="https://your-return-url.com"):
        """
        create payment

        :param self: self
        :param amount: amount
        :param currency: currency
        :param return_url: url
        :return: payment
        """
        headers = {"Idempotence-Key": "your_unique_key"}  # Generate a unique key for each transaction
        payload = {
            "amount": {
                "value": amount,
                "currency": currency
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            }
        }

        response = requests.post(self.base_url + "payments", json=payload, auth=self.auth, headers=headers)
        if response.status_code == 200:
            return response.json()['confirmation']['confirmation_url'], response.json()['id']
        else:
            return None, None

    def check_payment_status(self, payment_id):
        """
        check payment status

        :param self: self
        :param payment_id: payment id
        :return: status
        """
        response = requests.get(self.base_url + "payments/" + payment_id, auth=self.auth)
        if response.status_code == 200:
            return response.json()['status']
        else:
            return None

    def handle_webhook(self, data):
        """
        handle webhook

        :param self: self
        :param data: data
        :return: payment id and status
        """
        # This method should process webhook data sent by YooKassa
        # For example, it might look something like this:
        payment_id = data.get('object', {}).get('id')
        status = data.get('object', {}).get('status')
        return payment_id, status
