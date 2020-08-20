import unittest
import pandas as pd
from Transactions import Transactions

class TestTransactions(unittest.TestCase):
    def test_gather_all_statements(self):
        self.assertEqual(self.transactions.transaction_df.shape[0], 10)

    def setUp(self):
        self.transactions = Transactions(statements_dir='./test_data')
        self.transactions.gather_all_statements()
        self.transactions.mark_duplicates_2()

    def test_mark_duplicates_run(self):
        bool_list = pd.Series(self.transactions.transaction_df.columns).isin(['isDuplicate'])

        self.assertTrue(bool_list.any())
    def test_get_net_expense(self):
        # print (self.transactions.transaction_df)
        net_expense = self.transactions.get_net_expense(df_to_use=self.transactions.transaction_df)
        self.assertEqual(net_expense.Amount.loc['Credit'], -650.5)
        self.assertEqual(net_expense.Amount.loc['Debit'], 110)


if __name__ == '__main__':
    unittest.main()
