<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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

const accounts = ref<Accounts>([])

const amount = ref<string>('')

const principalAccount = ref<Account>({
  'account_id': '',
  'amount': '',
  'last_credit_transaction': '',
  'last_debit_transaction': ''
})

const beneficiaryAccount = ref<Account>({
  'account_id': '',
  'amount': '',
  'last_credit_transaction': '',
  'last_debit_transaction': ''
})

const beneficiaryAccountId = ref<string>(null)

const errorMessage = ref('')

const notificationMessage = ref('')

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
      accounts.value = []
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

const createTransaction = async () => {
  await axios
    .post<Transaction>('/api/accounts/' + principalAccount.value.account_id.replace(/^0+/, '') + '/transactions',
    {
      "destination_id": beneficiaryAccount.value.account_id.replace(/^0+/, ''),
      "amount": amount.value
    })
    .then(async (response) => {
      if (response.status !== 200) {
        errorMessage.value = 'Cannot create Transaction'
        console.error('Transaction create error: ', response.status, response.data)
        return
      }
      const data = await response.data
      const isJson = response.headers['content-type'].includes('application/json')
      if (isJson) {
        notificationMessage.value = 'Created Transaction with key ' + data.transaction_id
        errorMessage.value = ''
      }
    })
    .catch((error) => {
      errorMessage.value = 'Cannot create Transaction'
      console.error('Transaction create error: ', error)
    })
}

const executeTransaction = async () => {
  if(principalAccount === undefined || principalAccount.value.account_id === '') {
    errorMessage.value = 'Cannot proceed: Principal Account not defined'
    return
  }
  if(beneficiaryAccount === undefined || beneficiaryAccount.value.account_id === '') {
    errorMessage.value = 'Cannot proceed: Beneficiary Account not valid or not existent'
    return
  }
  if(!(/^\d+(\.\d{1,2})?$/.test(amount.value)) || isNaN(parseFloat(amount.value)) || !isFinite(amount.value)) {
    errorMessage.value = 'Cannot proceed: Amount not valid'
    return
  }
  await createTransaction()
}

const selectPrincipalAccount = (id: string) => {
  const account = accounts.value.filter((a) => a['account_id'] === id)
  if (account.length > 0) {
    principalAccount.value = account[0]
  } else {
    principalAccount.value = {
      'account_id': '',
      'amount': '',
      'last_credit_transaction': '',
      'last_debit_transaction': ''
    }
  }
  errorMessage.value = ''
  notificationMessage.value = ''
}

const selectBeneficiaryAccount = (value) => {
  const id = value.data as string
  const account = accounts.value.filter((a) => a['account_id'].replace(/^0+/, '') === id)
  if (account.length > 0) {
    beneficiaryAccount.value = account[0]
  } else {
    beneficiaryAccount.value = {
      'account_id': '',
      'amount': '',
      'last_credit_transaction': '',
      'last_debit_transaction': ''
    }
  }
  errorMessage.value = ''
  notificationMessage.value = ''
}

const updateAmount = () => {
  errorMessage.value = ''
  notificationMessage.value = ''
}

const rules = {
  required: value => !!value || 'Field is required',
  number: value => !isNaN(parseFloat(value)) && isFinite(value),
  money: value => /^\d+(\.\d{1,2})?$/.test(value)
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
                <v-form @submit.prevent>
                  <h1>Principal Account</h1>
                  <v-select
                    :items="accounts"
                    item-value="account_id"
                    item-title="account_id"
                    :menu-props="{ scrim: true, scrollStrategy: 'close' }"
                    label="Account"
                    @update:modelValue="selectPrincipalAccount"
                    :rules="[rules.required]"
                    required
                  ></v-select>
                  <div class="mt-5"></div>
                  <h1>Beneficiary Account</h1>
                  <v-text-field
                    label="Account"
                    v-model="beneficiaryAccountId"
                    :rules="[rules.required]"
                    required
                    @input="selectBeneficiaryAccount"
                  ></v-text-field>
                  <div class="mt-5"></div>
                  <h1>Payment Details</h1>
                  <v-text-field
                    label="Amount (EUR)"
                    v-model="amount"
                    :rules="[rules.required, rules.number, rules.money]"
                    @input="updateAmount"
                    required
                  ></v-text-field>
                  <div class="mt-5"></div>
                  <v-btn
                    @click="executeTransaction"
                    type="submit"
                    block
                  >
                    Proceed
                  </v-btn>
                </v-form>
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
    <v-alert
      v-if="notificationMessage !== ''"
      border="start"
      elevation="2"
      density="compact"
      title="Message"
      type="success"
      variant="tonal"
      class="bottom-right-alert"
      >{{ notificationMessage }}</v-alert
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