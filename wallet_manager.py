import os, json
class WalletManager:
    def __init__(self):
        self.wallets = json.loads(os.getenv("WALLETS", "[]"))
        self.index = 0
    def rotate_wallets(self):
        if not self.wallets:
            return "⚠️ No wallets configured"
        self.index = (self.index + 1) % len(self.wallets)
        active = self.wallets[self.index]
        return f"🔄 Using wallet {self.index+1}/{len(self.wallets)}: {active['address']}"
    def collect_fees(self, target):
        return f"💰 Fees collected to {target}"
