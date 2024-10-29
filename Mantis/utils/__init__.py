import random
import socket
import requests
import ipaddress


def is_private_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return "Invalid IP address"

def uniform_random_natural(expected_value):
    N = int(2 * expected_value - 1)
    return random.randint(1, N)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Error retrieving local IP: {e}"

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        public_ip = response.json()["ip"]
        return public_ip
    except Exception as e:
        return f"Error retrieving public IP: {e}"


def generate_random_date(seed=None):
    if seed:
        random.seed(seed)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month = random.choice(months)
    day = random.randint(1, 30)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)    
    date_string = f"{month} {day:02} {hour:02}:{minute:02}"
    return date_string