import requests

# URL برای دریافت لیست پکیج‌ها
PACKAGE_URL = "https://admin.talkesim.com/api/package"

# JWT Token
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OTIsImlhdCI6MTczMzMwNjk0MCwiZXhwIjoxNzM1ODk4OTQwfQ.XpCad0C90gudTqPysTHOqzwexQHmhwNOzUJlzQKKrfE"

# Header شامل Authorization
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "api-key": "513b375a-110a-4846-aeff-dde14591f392"
}

# ارسال درخواست GET
response = requests.get(PACKAGE_URL, headers=headers)

# بررسی و چاپ داده‌ها
if response.status_code == 200:
    packages = response.json()
    print("Packages retrieved successfully:")
    print(packages)
else:
    print(f"Failed to retrieve packages: {response.status_code}")
    print(response.text)

