const algosdk = require('algosdk');
const fs = require("fs");

(async() => {
    function generateAlgorandKeyPair() {
        let account = algosdk.generateAccount();
        let passphrase = algosdk.secretKeyToMnemonic(account.sk);
        console.log( "--------------------------------" );
        console.log( "My address: " + account.addr );
        console.log( "My passphrase: " + passphrase );
        console.log( "--------------------------------" );
        return [account, passphrase];
    }


    // recover accounts
    // paste in mnemonic phrases here for each account
    // Shown for demonstration purposes. NEVER reveal secret mnemonics in practice.
    // Change these values to use the accounts created previously.
    let account1_mnemonic = generateAlgorandKeyPair()[1];
    let account2_mnemonic = generateAlgorandKeyPair()[1];
    let account3_mnemonic = generateAlgorandKeyPair()[1];

    let account1 = algosdk.mnemonicToSecretKey(account1_mnemonic);
    let account2 = algosdk.mnemonicToSecretKey(account2_mnemonic);
    let account3 = algosdk.mnemonicToSecretKey(account3_mnemonic);
    console.log(account1.addr);
    console.log(account2.addr);
    console.log(account3.addr);

    //Setup the parameters for the multisig account
    const mparams = {
        version: 1,
        threshold: 2,
        addrs: [
            account1.addr,
            account2.addr,
            account3.addr,
        ],
    };

    let multsigaddr = algosdk.multisigAddress(mparams);
    console.log("Multisig Address: " + multsigaddr);
    // Fund TestNet account
    console.log('Dispense funds to this account on TestNet https://bank.testnet.algorand.network/');
})();

(async() => {

    const algodToken = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
    const algodServer = 'http://localhost';
    const algodPort = 4001;

    let algodClient = new algosdk.Algodv2(algodToken, algodServer, algodPort);

    //main wallet
    const address = "NZHJVFZNVQGCKVMSHZC2QCB22EO7CU6ZXPH3XFRS5RENGVLUTI2K3J2ALA";
    const passPhrase = "amount oval fabric pave tip stand essay apart galaxy embark invite become bracket maximum innocent horror pelican cage eager sing uniform material cereal ability bottom"

    const account = algosdk.mnemonicToSecretKey(passPhrase);
    // second wallet
    const address2 = "MS5OMYMTMWO7VM4CU4LMQRWN7YL2P7ZY45AX2OKP2LAUEZUWEV2SIZLVDE"
    const passphrase2 = "glance monkey turkey work crime drum spread ride guide crucial wood pencil burst borrow vessel actress vanish oyster quick media bullet fat inform about raven"
    console.log("****************************************************************")
    let params = await algodClient.getTransactionParams().do();
    params.fee = 1000;
    params.flatFee = true;
    console.log("params", params);

    // check account balance
    let accountInfo = await algodClient.accountInformation(address).do();
    console.log("Account balance: %d microAlgos", accountInfo.amount);

    let startingAmount = accountInfo.amount;
    const receiver = accountInfo.addrs//address2;

    console.log("params", params);
    const enc = new TextEncoder();
    const note = enc.encode("Hello World");
    let txn = algosdk.makePaymentTxnWithSuggestedParams(account.addr, account.addr, 1000000, undefined, note, params);        
    // // Save transaction to file
    // fs.writeFileSync('./unsigned.txn', algosdk.encodeUnsignedTransaction( txn ));     

    console.log("sk", account.sk);
    
    // // read transaction from file and sign it
    // txn = algosdk.decodeUnsignedTransaction(fs.readFileSync('./unsigned.txn'));  
    let signedTxn = txn.signTxn(account.sk);
    console.log("signedTxn", signedTxn);
    let txId = txn.txID().toString();
    console.log("Signed transaction with txID: %s", txId);

    // // send signed transaction to node
    await algodClient.sendRawTransaction(signedTxn).do();
    // console.log("hello")
    // // Wait for transaction to be confirmed
    // let confirmedTxn = await waitForConfirmation(algodClient, tx.txId, 4);
    // var string = new TextDecoder().decode(confirmedTxn.txn.txn.note);
    // console.log("Note field: ", string);       

})();
