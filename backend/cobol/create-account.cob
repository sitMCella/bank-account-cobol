000100 IDENTIFICATION DIVISION.
000200  PROGRAM-ID. createaccount.
000300  AUTHOR. Marco Cella.
000400  Installation. Create user bank account.
000500  Date-Written. 2025/05/21.
000600  Date-Compiled. 2025/05/21.
000700*
000800 ENVIRONMENT DIVISION.
000900  CONFIGURATION SECTION.
001000   Source-Computer. ALPINE-3-21.
001100   Object-Computer. ALPINE-3-21.
001200  INPUT-OUTPUT SECTION.
001300   FILE-CONTROL.
001400     SELECT DATAFILE ASSIGN TO "/opt/app/storage/accounts.idx"
001500       ORGANIZATION IS INDEXED
001600       ACCESS MODE IS DYNAMIC
001700       RECORD KEY IS IKEY
001800       FILE STATUS IS FILE-STATUS.
001900*
002000 DATA DIVISION.
002100  FILE SECTION.
002200   FD DATAFILE
002300     RECORD CONTAINS 100 CHARACTERS.
002400   01 DATAFILEFD.
002500     05 IKEY PIC 9(4).
002600     05 BALANCE-TOTAL PIC S9(29)V99 COMP-3.
002700     05 LAST-CREDIT-TRANSACTION PIC 9(4).
002800     05 LAST-DEBIT-TRANSACTION PIC 9(4).
002900*
003000  WORKING-STORAGE SECTION.
003100   01 FILE-STATUS PIC XX.
003200   01 WS-ENDOFFILE PIC 9 VALUE ZERO.
003300   01 WS-FILE-ERROR PIC 9 VALUE ZERO.
003400   01 WS-DATAFILEFD.
003500     05 WS-IKEY PIC 9(4).
003600     05 WS-BALANCE-TOTAL PIC S9(29)V99 COMP-3.
003700* WS-BALANCE-TOTAL max value: +99999999999999999999999999999.99
003800     05 WS-LAST-CREDIT-TRANSACTION PIC 9(4).
003900     05 WS-LAST-DEBIT-TRANSACTION PIC 9(4).
004000*
004100  LINKAGE SECTION.
004200   77 USERACCOUNTIKEY PIC 9(4).
004300   77 USERACCOUNTBALANCETOTAL PIC S9(29)V99 COMP-3.
004400   01 ACCOUNT.
004500     05 ACCOUNTIKEY PIC 9(4).
004600     05 ACCOUNTBALANCETOTAL PIC S9(29)V99 COMP-3.
004700     05 LASTCREDITTRANSACTION PIC 9(4).
004800     05 LASTDEBITTRANSACTION PIC 9(4).
004900   77 RETURNCODE PIC XX.
005000*
005100 PROCEDURE DIVISION USING
005200  BY REFERENCE USERACCOUNTIKEY
005300  BY REFERENCE USERACCOUNTBALANCETOTAL
005400  BY REFERENCE ACCOUNT
005500  BY REFERENCE RETURNCODE.
005600     DISPLAY "CREATE ACCOUNT."
005700     DISPLAY "Key: " USERACCOUNTIKEY.
005800     IF USERACCOUNTIKEY IS NOT NUMERIC
005900       DISPLAY "Wrong key value."
006000       MOVE "01" TO RETURNCODE
006100       GO TO QUIT
006200     END-IF.
006300*
006400     IF USERACCOUNTBALANCETOTAL IS NOT NUMERIC
006500       DISPLAY "Wrong balance total value."
006600       MOVE "50" TO RETURNCODE
006700       GO TO QUIT
006800     END-IF.
006900*
007000     IF USERACCOUNTBALANCETOTAL IS < 0
007100       DISPLAY "Wrong balance total value."
007200       MOVE "50" TO RETURNCODE
007300       GO TO QUIT
007400     END-IF.
007500*
007600     MOVE USERACCOUNTIKEY TO WS-IKEY.
007700     MOVE USERACCOUNTBALANCETOTAL TO WS-BALANCE-TOTAL.
007800     MOVE 0 TO WS-LAST-CREDIT-TRANSACTION.
007900     MOVE 0 TO WS-LAST-DEBIT-TRANSACTION.
008000*
008100     OPEN I-O DATAFILE.
008200       IF FILE-STATUS = "35"
008300         DISPLAY "File does not exist. Creating it."
008400         OPEN OUTPUT DATAFILE
008500       ELSE
008600         DISPLAY "The file exists."
008700       END-IF.
008800     CLOSE DATAFILE.
008900*
009000     OPEN I-O DATAFILE.
009100       MOVE WS-IKEY TO IKEY
009200       MOVE WS-BALANCE-TOTAL TO BALANCE-TOTAL
009300       MOVE WS-LAST-CREDIT-TRANSACTION TO LAST-CREDIT-TRANSACTION
009400       MOVE WS-LAST-DEBIT-TRANSACTION TO LAST-DEBIT-TRANSACTION
009500       DISPLAY "Account key: " IKEY
009600       DISPLAY "Account balance total: " BALANCE-TOTAL
009700       DISPLAY "Last credit transaction: " LAST-CREDIT-TRANSACTION
009800       DISPLAY "Last debit transaction: " LAST-DEBIT-TRANSACTION
009900       WRITE DATAFILEFD
010000         INVALID KEY MOVE 1 TO WS-FILE-ERROR
010100         NOT INVALID KEY DISPLAY "Item Added."
010200       END-WRITE.
010300     CLOSE DATAFILE.
010400*
010500     IF WS-FILE-ERROR IS ZERO
010600       MOVE WS-IKEY TO ACCOUNTIKEY
010700       MOVE WS-BALANCE-TOTAL TO ACCOUNTBALANCETOTAL
010800       MOVE WS-LAST-CREDIT-TRANSACTION
010900         TO LASTCREDITTRANSACTION
011000       MOVE WS-LAST-DEBIT-TRANSACTION
011100         TO LASTDEBITTRANSACTION
011200       MOVE "00" TO RETURNCODE
011300       GO TO QUIT
011400     ELSE
011500       DISPLAY "Error: Record already exists."
011600       MOVE WS-FILE-ERROR TO RETURNCODE
011700     END-IF.
011800  QUIT.
011900 EXIT PROGRAM.
