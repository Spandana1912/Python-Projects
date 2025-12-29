import os
import re
import mmh3
from bitarray import bitarray
from urllib.parse import urlparse

# --- Sample malicious domains ---
SAMPLE_DOMAINS = [
    "phishingsite.com", "malware.net", "danger.org", "hackersite.io",
    "badlogin.co", "stealcreds.xyz", "verify-account.org", "secure-update.net",
    "free-gifts-online.com", "banking-alerts.net", "auth-secure.io",
    "update-profile.org", "click-here-now.com", "accountverify.co", "password-reset.net",
    "login-secure.com", "update-payments.com", "online-banking-alerts.com", "confirm-account.info",
    "vault-login.net", "identity-verification.io", "verify-payments.org", "reset-your-password.com",
    "mybank-secure.co", "account-security-alerts.com", "secure-signin.co", "claims-reward.com",
    "reward-claim.xyz", "coupon-freebies.net", "cloud-secure-update.com", "billing-update.net",
    "auth-verify.me", "secure-account-login.org", "suspicious-activity-alert.net", "verify-now-payments.com",
    "confirm-identity.online", "secure-docs-download.com", "sms-authenticate.co", "twofactor-reset.org",
    "account-support-secure.com", "notice-account-update.net", "payment-declined-alerts.com",
    "secure-access-token.io", "update-your-info.today", "urgent-action-required.org"
]


class BloomFilter:
    """Simple Bloom Filter for detecting malicious base domains."""

    def __init__(self, size=1000, hash_count=5):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)
        self.items_added = 0

    def add(self, item):
        if not item:
            return
        item = item.strip().lower()
        for i in range(self.hash_count):
            idx = mmh3.hash(item, i) % self.size
            self.bit_array[idx] = 1
        self.items_added += 1

    def check(self, item):
        if not item:
            return False
        item = item.strip().lower()
        for i in range(self.hash_count):
            idx = mmh3.hash(item, i) % self.size
            if self.bit_array[idx] == 0:
                return False
        return True

    def load_domains_from_file(self, filename):
        if not os.path.exists(filename):
            return 0
        count = 0
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                base = self.get_base_domain(line)
                if base:
                    self.add(base)
                    count += 1
        return count

    @staticmethod
    def get_base_domain(url_or_domain):
        if not url_or_domain:
            return ""
        s = url_or_domain.strip()
        if "://" not in s:
            s = "http://" + s
        parsed = urlparse(s)
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return ""
        parts = hostname.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return hostname


def ensure_sample_file(path="spam_domains.txt"):
    if os.path.exists(path):
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(SAMPLE_DOMAINS))
    return True


if __name__ == "__main__":
    filename = "spam_domains.txt"
    ensure_sample_file(filename)

    bloom = BloomFilter(size=1000, hash_count=5)

    for domain in SAMPLE_DOMAINS:
        base = BloomFilter.get_base_domain(domain)
        if base:
            bloom.add(base)

    loaded = bloom.load_domains_from_file(filename)
    print("Bloom filter loaded with", loaded, "domains from file.\n")

    user_input = input("Enter a URL or domain to check: ").strip()

    if not user_input:
        print("Please enter a valid URL or domain.")
    elif not re.match(r'^(https?://)?[\w\.-]+(\.[a-z]{2,})(/.*)?$', user_input, re.IGNORECASE):
        print("Invalid input: Only valid URLs or domain names are allowed.")
    else:
        base = BloomFilter.get_base_domain(user_input)
        if not base or '.' not in base:
            print("Invalid domain: Must contain at least one '.'")
        else:
            print("(Debug) Checking base domain:", base)
            if bloom.check(base):
                print(user_input, "Possibly Malicious (base domain:", base, ")")
            else:
                print(user_input, "Safe (base domain:", base, ")")
