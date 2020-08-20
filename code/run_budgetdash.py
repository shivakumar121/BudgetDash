import argparse
from Transactions import Transactions


def main():
    parser = argparse.ArgumentParser(description=' Budget analyzer.')
    parser.add_argument('--statements-dir', type=str, required=True,
                        help='Path to the directory containing statements.')

    args = parser.parse_args()
    transactions = Transactions(statements_dir=args.statements_dir)
    transactions.gather_all_statements()
    transactions.mark_duplicates_2()
    print (transactions.transaction_df)
    df = transactions.get_net_expense(df_to_use=transactions.transaction_df)
    print (df)
    print (df.index.values)
    print(transactions.transaction_df.dtypes)
    transactions.generate_month_labels()
    print(transactions.transaction_df.head())
    transactions.mark_duplicates_2()
    print(transactions.transaction_df)

if __name__ == '__main__':
    main()
