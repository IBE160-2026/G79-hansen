"""Explicit local ledger initialization/inspection; never reads credentials."""
import argparse
import json
from app.services.model_budget import ModelBudget, BudgetFailure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('init', 'status'))
    parser.add_argument('path')
    args = parser.parse_args()
    try:
        if args.action == 'init':
            ModelBudget.initialize(args.path)
        with ModelBudget(args.path).exclusive():
            print(json.dumps(ModelBudget(args.path).read(), sort_keys=True))
    except (OSError, BudgetFailure):
        parser.exit(1, 'Budget ledger unavailable; existing ledgers are never reset.\n')


if __name__ == '__main__':
    main()
