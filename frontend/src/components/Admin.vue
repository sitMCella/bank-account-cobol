<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import AppBar from "./AppBar.vue";
import Navigation from "./Navigation.vue";

interface Account {
  account_id: string;
  amount: string;
  last_credit_transaction: string;
  last_debit_transaction: string;
}

interface Accounts {
  accounts: Account[];
}

const accounts = ref<Account[]>([]);

const accountId = ref<string>("");

const balanceTotal = ref<string>("");

const errorMessage = ref("");

const notificationMessage = ref("");

const getAccounts = async () => {
  await axios
    .get<Accounts>("/api/accounts")
    .then(async (response) => {
      if (response.status !== 200) {
        errorMessage.value = "Cannot retrieve Accounts";
        console.error(
          "Accounts retrieve error: ",
          response.status,
          response.data,
        );
        return;
      }
      const data: Accounts = await response.data;
      accounts.value = [];
      const isJson =
        response.headers["content-type"].includes("application/json");
      if (isJson) {
        accounts.value = data.accounts;
      }
    })
    .catch((error) => {
      errorMessage.value = "Cannot retrieve Accounts";
      console.error("Accounts retrieve error: ", error);
    });
};

const createAccount = async () => {
  await axios
    .post<Account>("/api/accounts/" + accountId.value.replace(/^0+/, ""), {
      balance_total: balanceTotal.value,
    })
    .then(async (response) => {
      if (response.status !== 200) {
        errorMessage.value = "Cannot create Account";
        console.error("Account create error: ", response.status, response.data);
        return;
      }
      const data: Account = await response.data;
      const isJson =
        response.headers["content-type"].includes("application/json");
      if (isJson) {
        accounts.value.push(data);
        errorMessage.value = "";
        notificationMessage.value = "Account created";
      }
    })
    .catch((error) => {
      errorMessage.value = "Cannot create Account";
      console.error("Account create error: ", error);
    });
};

const processAccountTransactions = async (account: Account) => {
  await axios
    .put(
      "/api/accounts/" +
        account.account_id.replace(/^0+/, "") +
        "/transactions",
      {},
    )
    .then(async (response) => {
      if (response.status === 404) {
        console.log(
          "The Account " +
            account.account_id +
            " does not have any transactions.",
        );
      } else if (response.status !== 200) {
        errorMessage.value =
          "Cannot process Transactions for the Account " + account.account_id;
        console.error(
          "Transactions process error: ",
          response.status,
          response.data,
        );
        return;
      }
      await response.data;
    })
    .catch((error) => {
      errorMessage.value =
        "Cannot process Transactions for the Account " + account.account_id;
      console.error("Transactions process error: ", error);
    });
};

const verifyAccountParameters = () => {
  if (accountId.value == undefined || accountId.value == "") {
    return false;
  }
  if (
    !/^\d+(\.\d{1,2})?$/.test(balanceTotal.value) ||
    isNaN(parseFloat(balanceTotal.value)) ||
    !isFinite(parseFloat(balanceTotal.value))
  ) {
    return false;
  }
  const existentAccount = accounts.value.filter(
    (a) =>
      a["account_id"].replace(/^0+/, "") === accountId.value.replace(/^0+/, ""),
  );
  if (existentAccount.length > 0) {
    return false;
  }
  return true;
};

const isMoneyValue = (value: string) => {
  if (
    !/^\d+(\.\d{1,2})?$/.test(value) ||
    isNaN(parseFloat(value)) ||
    !isFinite(parseFloat(value))
  ) {
    return false;
  }
  return true;
};

const executeCreateAccount = async () => {
  if (accountId.value == undefined || accountId.value == "") {
    errorMessage.value = "Provide an account key";
    return;
  }
  if (!isMoneyValue(balanceTotal.value)) {
    errorMessage.value = "Cannot proceed: Balance value not valid";
    return;
  }
  const existentAccount = accounts.value.filter(
    (a) =>
      a["account_id"].replace(/^0+/, "") === accountId.value.replace(/^0+/, ""),
  );
  if (existentAccount.length > 0) {
    errorMessage.value =
      "The account with key " + accountId.value + " already exists";
    return;
  }
  await createAccount();
};

const executeProcessTransactions = async () => {
  for (const account of accounts.value) {
    await processAccountTransactions(account);
  }
  await getAccounts();
};

const rules = {
  required: (value: string) => !!value || "Field is required",
  number: (value: string) =>
    !isNaN(parseFloat(value)) && isFinite(parseFloat(value)),
  money: (value: string) => /^\d+(\.\d{1,2})?$/.test(value),
};

onMounted(async () => {
  await getAccounts();
});
</script>

<template>
  <v-app>
    <AppBar />
    <Navigation />
    <v-main>
      <v-container style="max-width: 100%">
        <v-toolbar>
          <v-toolbar-items>
            <v-dialog class="action-dialog">
              <template v-slot:activator="{ props: activatorProps }">
                <v-btn
                  v-bind="activatorProps"
                  text="Account"
                  prepend-icon="mdi-plus"
                  @click="[
                    (accountId = ''),
                    (balanceTotal = ''),
                    (errorMessage = ''),
                    (notificationMessage = ''),
                  ]"
                ></v-btn>
              </template>
              <template v-slot:default="{ isActive }">
                <v-card title="Create Account">
                  <v-card-text>
                    <v-form @submit.prevent>
                      <h2>Account Key</h2>
                      <v-text-field
                        label="Account Key"
                        v-model="accountId"
                        :rules="[rules.required]"
                        required
                      ></v-text-field>
                      <div class="mt-5"></div>
                      <h2>Initial Balance</h2>
                      <v-text-field
                        label="Balance Total (EUR)"
                        v-model="balanceTotal"
                        :rules="[rules.required, rules.number, rules.money]"
                        required
                      ></v-text-field>
                    </v-form>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                      text="Create"
                      @click="[
                        executeCreateAccount(),
                        verifyAccountParameters()
                          ? (isActive.value = false)
                          : (isActive.value = true),
                      ]"
                    ></v-btn>
                    <v-btn text="Close" @click="isActive.value = false"></v-btn>
                  </v-card-actions>
                </v-card>
              </template>
            </v-dialog>

            <v-dialog class="action-dialog">
              <template v-slot:activator="{ props: activatorProps }">
                <v-btn
                  v-bind="activatorProps"
                  text="Process Transactions"
                  prepend-icon="mdi-plus"
                  @click="[(errorMessage = ''), (notificationMessage = '')]"
                ></v-btn>
              </template>
              <template v-slot:default="{ isActive }">
                <v-card title="Process Transactions">
                  <v-card-text>
                    Approve and synchronize the transactions for all bank
                    accounts.
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                      text="Confirm"
                      @click="[
                        executeProcessTransactions(),
                        (isActive.value = false),
                      ]"
                    ></v-btn>
                    <v-btn text="Close" @click="isActive.value = false"></v-btn>
                  </v-card-actions>
                </v-card>
              </template>
            </v-dialog>
          </v-toolbar-items>
        </v-toolbar>
        <v-row>
          <v-col cols="1"></v-col>
          <v-col cols="10">
            <v-card rounded="0">
              <v-card-text>
                <h1>Accounts</h1>
                <v-table>
                  <thead>
                    <tr>
                      <th class="text-left">Key</th>
                      <th class="text-left">Last Credit Transaction</th>
                      <th class="text-left">Last Debit Transaction</th>
                      <th class="text-left">Total Balance</th>
                      <th class="text-left">Currency</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(account, index) in accounts" :key="index">
                      <td>{{ account.account_id }}</td>
                      <td>{{ account.last_credit_transaction }}</td>
                      <td>{{ account.last_debit_transaction }}</td>
                      <td>{{ account.amount }}</td>
                      <td>EUR</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="1"></v-col>
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
.action-dialog {
  max-width: 500px;
}

.bottom-right-alert {
  position: fixed;
  bottom: 20px;
  right: 20px;
  max-width: 500px;
  width: 100%;
  z-index: 9999;
}
</style>
