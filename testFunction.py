from typing import List, Dict, Optional

class BankAccount:
    def __init__(self, owner: str, starting_balance: float = 0.0):
        self.owner = owner
        self.balance = starting_balance
        self.history = []

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self.balance += amount
        self.history.append(f"Deposited ${amount}")
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        self.history.append(f"Withdrew ${amount}")
        return True

    def transfer(self, target: "BankAccount", amount: float) -> bool:
        if self.withdraw(amount):
            target.deposit(amount)
            self.history.append(f"Transferred ${amount} to {target.owner}")
            return True
        return False

    def get_summary(self) -> Dict:
        return {
            "owner": self.owner,
            "balance": self.balance,
            "transactions": self.history
        }


class BankSystem:
    def __init__(self):
        self.accounts: Dict[str, BankAccount] = {}

    def create_account(self, name: str, initial_deposit: float = 0.0) -> bool:
        if name in self.accounts:
            return False
        self.accounts[name] = BankAccount(name, initial_deposit)
        return True

    def get_account(self, name: str) -> Optional[BankAccount]:
        return self.accounts.get(name)

    def transfer_between(self, sender: str, receiver: str, amount: float) -> bool:
        acc1 = self.get_account(sender)
        acc2 = self.get_account(receiver)

        if not acc1 or not acc2:
            return False

        return acc1.transfer(acc2, amount)

    def apply_interest(self, rate: float):
        for account in self.accounts.values():
            if account.balance > 0:
                interest = account.balance * rate
                account.deposit(interest)
                account.history.append(f"Interest applied: ${interest:.2f}")


def run_demo():
    bank = BankSystem()

    bank.create_account("Alice", 500)
    bank.create_account("Bob", 300)

    alice = bank.get_account("Alice")
    bob = bank.get_account("Bob")

    if alice:
        alice.withdraw(100)
        alice.deposit(50)

    if bob:
        bob.deposit(200)

    bank.transfer_between("Alice", "Bob", 200)

    bank.apply_interest(0.05)

    # Print summaries
    for name, account in bank.accounts.items():
        print(f"\n{name}'s Account Summary:")
        summary = account.get_summary()
        for k, v in summary.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    run_demo()