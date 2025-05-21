all: create-account read-account read-accounts create-transaction read-credits read-debits process-transactions

create-account: create-account.cob
	cobc --debug -m -g -fimplicit-init -o create-account.so create-account.cob

read-account: read-account.cob
	cobc --debug -m -g -fimplicit-init -o read-account.so read-account.cob

read-accounts: read-accounts.cob
	cobc --debug -m -g -fimplicit-init -o read-accounts.so read-accounts.cob

create-transaction: create-transaction.cob
	cobc --debug -m -g -fimplicit-init -o create-transaction.so create-transaction.cob

read-credits: read-credits.cob
	cobc --debug -m -g -fimplicit-init -o read-credits.so read-credits.cob

read-debits: read-debits.cob
	cobc --debug -m -g -fimplicit-init -o read-debits.so read-debits.cob

process-transactions: process-transactions.cob
	cobc --debug -m -g -fimplicit-init -o process-transactions.so process-transactions.cob

renumber: create-account.cob
	./renumber.sh create-account.cob
	./renumber.sh read-account.cob
	./renumber.sh read-accounts.cob
	./renumber.sh create-transaction.cob
	./renumber.sh read-credits.cob
	./renumber.sh read-debits.cob
	./renumber.sh process-transactions.cob

clean:
	rm -f ./*.c || true
	rm -f ./*.h || true
	rm -f ./*.i || true
	rm -f ./*.dek || true
	rm -f ./*.lst || true
	rm -f ./*.o || true
	rm -f ./*.so || true
