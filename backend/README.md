# Bank Account Cobol Backend

Python web application that interfaces with OpenCobol to process account balances and transactions.

The integration between Python and OpenCobol was inspired by the project https://github.com/perspectivism/web-stacks-with-cobol.

The following Dockerfile for OpenCobol has been used: https://github.com/humbertodias/docker-cobol-gnu/blob/main/Dockerfile.alpine.

## Development

### Cobol

Renumber Cobol files:

```sh
cd cobol
make renumber
```

# REST APIs

Create Account:

```sh
curl --header "Content-Type: application/json" -X POST --data '{"balance_total":"11.99"}' http://localhost:8081/accounts/1
```

Read Account:

```sh
curl -X GET http://localhost:8081/accounts/1
```

Read Accounts:

```sh
curl -X GET http://localhost:8081/accounts
```

Create Transaction:

```sh
curl --header "Content-Type: application/json" -X POST --data '{"destination_id":"2", "amount":"11.99"}' http://localhost:8081/accounts/1/transactions
```

Read Transactions:

```sh
curl -X GET "http://localhost:8081/accounts/1/transactions?type=<type>&start=<start>"
```
where `type` is either `credit` or `debit`, and `start` is the start transaction id for pagination.

Process Transactions:

```sh
curl -X PUT "http://localhost:8081/accounts/1/transactions"
```
