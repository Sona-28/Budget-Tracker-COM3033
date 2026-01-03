import requests

AUTH_SERVICE = "http://localhost:5000"
TRANSACTION_SERVICE = "http://localhost:5002"
CATEGORY_SERVICE = "http://localhost:5003"


def get_user_details(user_id):
    try:
        res = requests.get(f"{AUTH_SERVICE}/auth/users/{user_id}")
        return res.json() if res.status_code == 200 else None
    except:
        return None


def get_total_spent(user_id, category=None):
    try:
        params = {}
        if category:
            params["category"] = category

        res = requests.get(
            f"{TRANSACTION_SERVICE}/transactions/{user_id}",
            params=params
        )

        if res.status_code == 200:
            tx = res.json()
            return sum(t["amount"] for t in tx)
    except:
        pass

    return 0.0


def get_category_budget(user_id, category):
    try:
        res = requests.get(
            f"{CATEGORY_SERVICE}/budgets/{user_id}/{category}"
        )
        if res.status_code == 200:
            data = res.json()
            return float(data.get("budget", 0))
    except:
        pass

    return 0.0
