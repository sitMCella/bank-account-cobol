<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AppBar from './AppBar.vue'
import Navigation from './Navigation.vue'

interface Account {
  'account_id': string,
  'amount': string,
  'last_credit_transaction': string,
  'last_debit_transaction': string
}

interface Accounts {
  'accounts': Account[]
}

interface Transaction {
  'transaction_id': string,
  'source_id': string,
  'destination_id': string,
  'amount': string,
  'date_yyyy': string,
  'date_mm': string,
  'date_dd': string,
  'time_hh': string,
  'time_mm': string,
  'time_ss': string,
  'time_ms': string,
  'type': string,
  'timestamp': number
}

interface Transactions {
  'transactions': Transaction[]
}

const accounts = ref<Accounts>()

let transactions = ref<Transactions>()

let processed_transactions = ref<Transactions>()

let not_processed_transactions = ref<Transactions>()

const errorMessage = ref('')

const selectedAccount = ref<Account>({
  'account_id': '',
  'amount': '',
  'last_credit_transaction': '',
  'last_debit_transaction': ''
})

const getAccounts = async () => {
  await axios
    .get<Account[]>('/api/accounts')
    .then(async (response) => {
      if (response.status !== 200) {
        errorMessage.value = 'Cannot retrieve Accounts'
        console.error('Accounts retrieve error: ', response.status, response.data)
        return
      }
      const data = await response.data
      accounts.value = { accounts: [] }
      const isJson = response.headers['content-type'].includes('application/json')
      if (isJson) {
        accounts.value = data.accounts
      }
    })
    .catch((error) => {
      errorMessage.value = 'Cannot retrieve Accounts'
      console.error('Accounts retrieve error: ', error)
    })
}

const getTransactions = async (account_id: string, type: string): Promise<Transactions> => {
  return await axios
    .get<Account[]>('/api/accounts/' + account_id + '/transactions?type=' + type + '&start=0')
    .then(async (response) => {
      if (response.status !== 200) {
        errorMessage.value = 'Cannot retrieve Transactions'
        console.error('Transactions retrieve error: ', response.status, response.data)
        return
      }
      const data = await response.data
      let transactions = ref<Transactions>()
      transactions.value = []
      const isJson = response.headers['content-type'].includes('application/json')
      if (isJson) {
        transactions.value = data.transactions
      }
      return transactions
    })
    .catch((error) => {
      errorMessage.value = 'Cannot retrieve Transactions'
      console.error('Transactions retrieve error: ', error)
    })
}

const getAllTransactions = async (id: string) => {
  const account_id = parseInt(id, 10)
  if (isNaN(account_id)) {
    console.log('Not numeric account_id: ' + id)
    return
  }
  let all_transactions: Transactions = []
  await getTransactions(account_id, 'credit').then(async (credit_transactions) => {
    credit_transactions.value.forEach((t) => {
      t.type = 'credit'
      t.timestamp = parseTimestamp(t)
    })
    all_transactions = [...credit_transactions.value]
  })
  await getTransactions(account_id, 'debit').then(async (debit_transactions) => {
    debit_transactions.value.forEach((t) => {
      t.type = 'debit'
      t.timestamp = parseTimestamp(t)
    })
    all_transactions = [...all_transactions, ...debit_transactions.value]
  })
  transactions.value = all_transactions.sort(
    (a, b) => a.timestamp - b.timestamp
  )
  selectProcessedTransactions()
  selectNotProcessedTransactions()
}

const selectProcessedTransactions = () => {
  processed_transactions.value = transactions.value.filter((t) => t.transaction_id <= selectedAccount.value.last_credit_transaction || t.transaction_id <= selectedAccount.value.last_debit_transaction)
}

const selectNotProcessedTransactions = () => {
  not_processed_transactions.value = transactions.value.filter((t) => t.transaction_id > selectedAccount.value.last_credit_transaction && t.transaction_id > selectedAccount.value.last_debit_transaction)
}

const parseTimestamp = (t: Transaction): number => {
  return new Date(
    parseInt(t.date_yyyy), 
    parseInt(t.date_mm) - 1, // Month is 0-based
    parseInt(t.date_dd),
    parseInt(t.time_hh),
    parseInt(t.time_mm),
    parseInt(t.time_ss),
    parseInt(t.time_ms) / 1000
  ).getTime()
}

const parseDateTime = (t: Transaction): Date => {
  return new Date(
    parseInt(t.date_yyyy), 
    parseInt(t.date_mm) - 1, // Month is 0-based
    parseInt(t.date_dd),
    parseInt(t.time_hh),
    parseInt(t.time_mm),
    parseInt(t.time_ss),
    parseInt(t.time_ms) / 1000
  )
}

const selectAccount = (id: string) => {
  const account = accounts.value.filter((a) => a['account_id'] === id)
  if (account.length > 0) {
    selectedAccount.value = account[0]
    getAllTransactions(id)
  } else {
    selectedAccount.value = {
      'account_id': '',
      'amount': '',
      'last_credit_transaction': '',
      'last_debit_transaction': ''
    }
  }
}

const formatDateTime = (dateTime: Date): string => {
  const pad = (num: number, size: number) => num.toString().padStart(size, '0')

  const year = dateTime.getFullYear()
  const month = pad(dateTime.getMonth() + 1, 2)
  const day = pad(dateTime.getDate(), 2)

  const hours = pad(dateTime.getHours(), 2)
  const minutes = pad(dateTime.getMinutes(), 2)
  const seconds = pad(dateTime.getSeconds(), 2)
  const milliseconds = pad(dateTime.getMilliseconds(), 3)

  return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}.${milliseconds}`
}

const displayDate = (t: Transaction): string => {
  const dateTime = parseDateTime(t)
  return formatDateTime(dateTime)
}

const displayLastEvaluatedDate = (): string => {
  if(transactions.value === undefined || transactions.value.length === 0) {
    return ''
  }
  const last_credit_transaction = processed_transactions.value.filter((t) => t.transaction_id === selectedAccount.value.last_credit_transaction)
  const last_credit_transaction_datetime = last_credit_transaction[0] !== undefined ? parseDateTime(last_credit_transaction[0]): new Date(-8640000000000000)
  const last_debit_transaction = processed_transactions.value.filter((t) => t.transaction_id === selectedAccount.value.last_debit_transaction)
  const last_debit_transaction_datetime = last_debit_transaction[0] !== undefined ? parseDateTime(last_debit_transaction[0]): new Date(-8640000000000000)
  const higherDataTime = last_credit_transaction_datetime > last_debit_transaction_datetime ? last_credit_transaction_datetime: last_debit_transaction_datetime
  return formatDateTime(higherDataTime)
}

const displayDebit = (t: Transaction): string => {
  return t.source_id === selectedAccount.value.account_id ? t.amount: ''
}

const displayCredit = (t: Transaction): string => {
  return t.destination_id === selectedAccount.value.account_id ? t.amount: ''
}

onMounted(async () => {
  await getAccounts()
})
</script>

<template>
  <v-app>
    <AppBar />
    <Navigation />
    <v-main>
      <v-container style="max-width: 100%">
        <v-row>
          <v-col cols="3"></v-col>
          <v-col cols="6">
            <v-card rounded="0">
              <v-card-text>
                <h1>Personal Account</h1>
                <v-select
                  :items="accounts"
                  item-value="account_id"
                  item-title="account_id"
                  :menu-props="{ scrim: true, scrollStrategy: 'close' }"
                  label="Account"
                  @update:modelValue="selectAccount"
                ></v-select>
                <div class="mt-5"></div>
                <h1>Transactions</h1>
                <v-table>
                  <thead>
                    <tr>
                      <th class="text-left">
                        Date
                      </th>
                      <th class="text-left">
                        Source
                      </th>
                      <th class="text-left">
                        Destination
                      </th>
                      <th class="text-left">
                        Debit
                      </th>
                      <th class="text-left">
                        Credit
                      </th>
                      <th class="text-left">
                        Currency
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(transaction, index) in processed_transactions"
                      :key="index"
                    >
                      <td>{{ displayDate(transaction) }}</td>
                      <td>{{ transaction.source_id }}</td>
                      <td>{{ transaction.destination_id }}</td>
                      <td>{{ displayDebit(transaction) }}</td>
                      <td>{{ displayCredit(transaction) }}</td>
                      <td>EUR</td>
                    </tr>
                  </tbody>
                </v-table>
                <div class="mt-5"></div>
                <h1>Balance</h1>
                <v-table>
                  <thead>
                    <tr>
                      <th class="text-left">
                        Date
                      </th>
                      <th class="text-left">
                        Amount
                      </th>
                      <th class="text-left">
                        Currency
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>{{ displayLastEvaluatedDate() }}</td>
                      <td>{{ selectedAccount.amount }}</td>
                      <td>EUR</td>
                    </tr>
                  </tbody>
                </v-table>
                <div class="mt-5"></div>
                <h1>Not Processed Transactions</h1>
                <v-table>
                  <thead>
                    <tr>
                      <th class="text-left">
                        Date
                      </th>
                      <th class="text-left">
                        Source
                      </th>
                      <th class="text-left">
                        Destination
                      </th>
                      <th class="text-left">
                        Debit
                      </th>
                      <th class="text-left">
                        Credit
                      </th>
                      <th class="text-left">
                        Currency
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(transaction, index) in not_processed_transactions"
                      :key="index"
                    >
                      <td>{{ displayDate(transaction) }}</td>
                      <td>{{ transaction.source_id }}</td>
                      <td>{{ transaction.destination_id }}</td>
                      <td>{{ displayDebit(transaction) }}</td>
                      <td>{{ displayCredit(transaction) }}</td>
                      <td>EUR</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="3"></v-col>
        </v-row>
      </v-container>
    </v-main>

    <v-alert
      v-if="errorMessage !== ''"
      border="start"
      elevation="2"
      density="compact"
      title="Error"
      type="error"
      variant="tonal"
      class="bottom-right-alert"
      >{{ errorMessage }}</v-alert
    >
  </v-app>
</template>

<style scoped>
.bottom-right-alert {
  position: fixed;
  bottom: 20px;
  right: 20px;
  max-width: 500px;
  width: 100%;
  z-index: 9999;
}
</style>