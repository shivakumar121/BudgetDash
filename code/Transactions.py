import pandas as pd
import os
import numpy as np
from pandas.tseries.offsets import MonthEnd


class Transactions:
    def __init__(self, statements_dir):
        self.statements_dir = statements_dir

    def rename_cols(self, df_to_rename, schema_to_use):
        for old_names in schema_to_use.old_col_name:
            new_name = schema_to_use.new_col_name.values[schema_to_use.old_col_name == old_names][0]
            df_to_rename[new_name] = df_to_rename[old_names]
        return df_to_rename

    def get_net_expense(self, df_to_use):
        # print (df_to_use)
        df_to_use = df_to_use[df_to_use.isDuplicate == 'unique']
        df_to_use.loc[df_to_use.Amount > 0, 'Type'] = 'Debit'
        df_to_use.loc[df_to_use.Amount <= 0, 'Type'] = 'Credit'
        df_to_use['Amount_abs'] = df_to_use.Amount.abs()
        # print (df_to_use[df_to_use.Amount>0])
        return df_to_use.groupby('Type').sum()

    def gather_all_statements(self):
        all_dirs = os.listdir(self.statements_dir)
        all_dirs = [os.path.join(self.statements_dir, x) for x in all_dirs if not x.startswith('.')]
        all_dirs = [x for x in all_dirs if os.path.isdir(x)]
        self.transaction_df = pd.DataFrame([], columns=['Datetime', 'Description', 'Category', 'Amount'])
        for curr_dir in all_dirs:
            all_files = os.listdir(curr_dir)

            schema_file = [x for x in all_files if x.startswith('schema_file')]

            try:
                curr_schema = pd.read_csv(os.path.join(curr_dir, schema_file[0]), header=0, index_col=False)
            except Exception as e:
                print('Unable to read schema file.')
                print(e)
            statement_files = [x for x in all_files if
                               (not x.startswith('schema_file')) and (not x.startswith(('ignore'))) and (
                                   not x.startswith(('.')))]
            print('statetment file {}'.format(statement_files))
            for curr_file in statement_files:

                curr_file = os.path.join(curr_dir, curr_file)

                try:
                    temp_df = pd.read_csv(os.path.abspath(curr_file), header=0, index_col=False)
                    ignore_file = os.path.join(curr_dir, 'ignore.txt')
                    if os.path.isfile(ignore_file):
                        ignore_ser = pd.read_csv(ignore_file)
                        print(ignore_ser)
                        print(temp_df.Description.isin(ignore_ser.columns).values)
                        temp_df = temp_df[~temp_df.Description.isin(ignore_ser.columns).values]

                    # print(temp_df)
                    temp_df = self.rename_cols(df_to_rename=temp_df, schema_to_use=curr_schema)
                    # print(temp_df)
                    cols_to_take = temp_df.columns[temp_df.columns.isin(['Datetime', 'Description',
                                                                         'Category', 'Amount'])]
                    self.transaction_df = pd.concat([self.transaction_df, temp_df[cols_to_take]], sort=True, axis=0)

                except FileNotFoundError as e:
                    print('Unable to read file {}, moving to next file'.format(curr_file))
                    print(e)
                except Exception as e:
                    print('Encountered exception.')
                    print(e)
        # print(transaction_df.head())
        # print(transaction_df.shape)
        # tt = self.get_net_expense(df_to_use=transaction_df)
        # print(tt)
        self.transaction_df['Datetime'] = pd.to_datetime(self.transaction_df['Datetime'], infer_datetime_format=True)
        self.transaction_df['Amount_abs'] = self.transaction_df.Amount.abs()
        self.transaction_df = self.transaction_df.drop_duplicates()
        self.transaction_df = self.transaction_df.sort_values(by='Datetime')

    def generate_month_labels(self):

        self.transaction_df['Month_string'] = self.transaction_df.Datetime.dt.strftime('%B_%Y')

    def filter_by_month_string(self, month_string=None):
        if month_string is None:
            return self.transaction_df
        else:
            time_month_year = pd.to_datetime(month_string, format='%B_%Y')
            month_end = time_month_year + MonthEnd(1)
            print (time_month_year)
            print (month_end)
            filtered_df = self.transaction_df[(self.transaction_df.Datetime >= time_month_year) & (self.transaction_df.Datetime <= month_end)]
            return filtered_df

    def mark_duplicates(self):
        amount_counts = self.transaction_df.Amount_abs.value_counts()
        amount_counts = amount_counts[amount_counts >= 2]
        self.transaction_df['isDuplicate'] = np.repeat('unique', repeats=self.transaction_df.shape[0])
        self.transaction_df.Description = self.transaction_df.Description.str.lower()
        mask = self.transaction_df.Amount_abs.isin(amount_counts.index.values)
        payment_mask = self.transaction_df.Description.str.contains('payment')
        self.transaction_df.isDuplicate[(mask.values) & (payment_mask.values)] = 'mark_duplicate'

    def mark_duplicates_2(self):
        amount_counts = self.transaction_df.Amount_abs.value_counts()
        # print ("value counts")
        # print (amount_counts)
        amount_counts = amount_counts[amount_counts >= 2]
        # print("value counts")
        # print(amount_counts)
        self.transaction_df['isDuplicate'] = np.repeat('unique', repeats=self.transaction_df.shape[0])
        mask = self.transaction_df.Amount.isin(-1*(amount_counts.index.values))
        # print ('mask values')
        # print (mask.values)
        idx = np.arange(self.transaction_df.shape[0])[mask.values]
        print (idx)
        for i in idx:
            curr_date = self.transaction_df.Datetime.iloc[i]
            amount_to_check = self.transaction_df.Amount.iloc[i]
            # print ('Current date is {}, and next five day is {}'.format(curr_date,(curr_date + pd.DateOffset(days=5))))
            next_fiveday_df = self.transaction_df[(self.transaction_df.Datetime >= (curr_date - pd.DateOffset(days=3)))
                                                  &
                                                  (self.transaction_df.Datetime <= (curr_date + pd.DateOffset(days=5)))]
            # print (next_fiveday_df)
            # print ((-1*next_fiveday_df.Amount.iloc[0]))
            # print ('i is {}'.format(i))
            # print ('Amunt is {}'.format(self.transaction_df.Amount.iloc[i]))
            # print (next_fiveday_df)
            if any((next_fiveday_df.Amount == (-1*amount_to_check)).values):
                # submask = next_fiveday_df.Amount == (-1*amount_to_check)
                date_pair = next_fiveday_df.Datetime[next_fiveday_df.Amount == (-1*amount_to_check)]
                # print (date_pair.values)
                # print (len ((self.transaction_df.Amount == (-1*amount_to_check)).values))
                # print (len ((self.transaction_df.Datetime == date_pair.values[0]).values))
                submask = np.logical_and((self.transaction_df.Amount == (-1*amount_to_check)).values,
                                         (self.transaction_df.Datetime == date_pair.values[0]).values)
                sub_idx = np.arange(self.transaction_df.shape[0])[submask]
                self.transaction_df.isDuplicate.iloc[i] = 'mark_duplicate'
                self.transaction_df.isDuplicate.iloc[sub_idx] = 'mark_duplicate'

        # self.transaction_df.Description = self.transaction_df.Description.str.lower()
        # mask = self.transaction_df.Amount_abs.isin(amount_counts.index.values)
        # payment_mask = self.transaction_df.Description.str.contains('payment')
        # self.transaction_df.isDuplicate[(mask.values) & (payment_mask.values)] = 'mark_duplicate'


